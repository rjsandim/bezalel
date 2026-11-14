#!/usr/bin/env python3
"""Publica cópias persistentes de previews, sem alterar o Tailscale Serve."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import quote


class PreviewError(ValueError):
    pass


def tailnet_host():
    binary = os.environ.get('ENV_TAILSCALE_BIN') or shutil.which('tailscale')
    if not binary:
        raise PreviewError('Tailscale não encontrado; configure ENV_TAILSCALE_BIN.')
    result = subprocess.run([binary, 'status', '--json'], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise PreviewError('Não foi possível consultar o hostname privado do Tailscale.')
    try:
        status = json.loads(result.stdout)
        host = status['Self']['DNSName'].rstrip('.')
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise PreviewError('Status do Tailscale sem Self.DNSName válido.') from exc
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?', host):
        raise PreviewError('Hostname do Tailscale inválido.')
    return host


def project_name(project):
    project = Path(project).expanduser().resolve(strict=True)
    config = project / '.bezalel/project.json'
    name = json.loads(config.read_text()).get('project') if config.is_file() else project.name
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name):
        raise PreviewError('Projeto precisa de nome em minúsculas, números e hífens.')
    return name


def previews_dir():
    return Path(os.environ.get('BEZALEL_PREVIEWS_DIR') or str(Path.home() / 'previews')).expanduser().absolute()


def ensure_directory(path, *, root=None):
    """Resolve a raiz configurada, recusando links nos descendentes gerenciados."""
    path = Path(path).expanduser().absolute()
    if root is None:
        # HOME e diretórios temporários podem ter ancestrais como /var ->
        # /private/var no macOS. São parte da raiz escolhida pelo operador.
        path = path.resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    root = Path(root).expanduser().absolute()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise PreviewError('Destino de preview fora da raiz configurada.') from exc
    if '..' in relative.parts:
        raise PreviewError('Destino de preview fora da raiz configurada.')
    directory = ensure_directory(root)
    for name in relative.parts:
        directory /= name
        if directory.is_symlink():
            raise PreviewError('Link simbólico no destino de preview; publicação recusada.')
        directory.mkdir(exist_ok=True)
    return directory


def open_preview(project, source):
    """Abre somente HTML regular do projeto, sem seguir links internos."""
    explicit_root = Path(os.path.abspath(Path(project).expanduser()))
    project = explicit_root.resolve(strict=True)
    source = Path(os.path.abspath(Path(source).expanduser()))
    try:
        relative = source.relative_to(explicit_root)
    except ValueError:
        # Aceita também o caminho canônico quando a raiz explícita usa /tmp,
        # /var ou outro ancestral vinculado, sem resolver links da origem.
        try:
            relative = source.relative_to(project)
        except ValueError as exc:
            raise PreviewError('Origem do preview deve estar dentro do projeto informado.') from exc
    if not relative.parts or source.suffix.lower() not in ('.html', '.htm'):
        raise PreviewError('Preview permite somente arquivos .html ou .htm do projeto.')
    allowed_review = relative.parts[:2] == ('.bezalel', 'reviews')
    for index, part in enumerate(relative.parts):
        if part.startswith('.') and not (allowed_review and index == 0):
            raise PreviewError('Arquivos ou diretórios ocultos não podem ser publicados como preview.')
        if Path(part).stem.lower() in {'secret', 'secrets', 'credentials', 'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', 'authorized_keys'}:
            raise PreviewError('Arquivo ou diretório de credenciais não pode ser publicado como preview.')
    # Abrir cada componente com NOFOLLOW impede que uma troca por symlink
    # entre a validação e a leitura escape da raiz explícita.
    directory = os.open(project, os.O_RDONLY | os.O_DIRECTORY)
    descriptor = None
    try:
        for part in relative.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise PreviewError('Informe um arquivo regular de preview, sem link simbólico.')
        file = os.fdopen(descriptor, 'rb')
        descriptor = None
        return file
    except OSError as exc:
        raise PreviewError('Origem de preview ausente, inválida ou com link simbólico.') from exc
    finally:
        os.close(directory)
        if descriptor is not None:
            os.close(descriptor)


def publish(project, issue, source):
    if not isinstance(issue, int) or issue <= 0:
        raise PreviewError('Issue deve ser um número positivo.')
    name = project_name(project)
    source = Path(source).expanduser().absolute()
    with open_preview(project, source) as input_file:
        host = tailnet_host()  # Falha de consulta não deixa uma cópia sem URL anunciável.
        root = previews_dir()
        directory = ensure_directory(root / name / f'issue-{issue}', root=root)
        destination = directory / source.name
        descriptor, temporary = tempfile.mkstemp(prefix='.preview-', dir=directory)
        try:
            with os.fdopen(descriptor, 'wb') as output:
                shutil.copyfileobj(input_file, output)
                output.flush()
                os.fchmod(output.fileno(), 0o644)
                os.fsync(output.fileno())
            try:
                # link é atômico e exclusivo: nunca substitui outra versão, mesmo
                # se dois bots publicarem o mesmo nome ao mesmo tempo.
                os.link(temporary, destination)
                created = True
            except FileExistsError:
                metadata = destination.lstat()
                if not stat.S_ISREG(metadata.st_mode) or destination.read_bytes() != Path(temporary).read_bytes():
                    raise PreviewError('Preview já publicado com conteúdo diferente; use outro nome de versão.')
                created = False
        finally:
            Path(temporary).unlink(missing_ok=True)
    return {'project': name, 'issue': issue, 'file': str(destination), 'created': created,
            'url': f'https://{host}/{quote(name)}/issue-{issue}/{quote(source.name)}',
            'preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('publish', help='Copia HTML do projeto; nunca move ou sobrescreve outra versão.')
    command.add_argument('--project', type=Path, required=True)
    command.add_argument('--issue', type=int, required=True)
    command.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(publish(args.project, args.issue, args.file), ensure_ascii=False))
        return 0
    except PreviewError as exc:
        print(f'Publicação recusada: {exc}', file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print('Publicação recusada; confira projeto, arquivo, Tailscale e se o nome já possui outra versão.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
