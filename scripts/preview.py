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


def ensure_directory(path):
    """Não publica através de um link preexistente na árvore de destino."""
    path = Path(path).absolute()
    for component in reversed((path, *path.parents)):
        if component.is_symlink():
            raise PreviewError('Diretório de previews contém link simbólico; publicação recusada.')
    path.mkdir(parents=True, exist_ok=True)
    return path


def publish(project, issue, source):
    if not isinstance(issue, int) or issue <= 0:
        raise PreviewError('Issue deve ser um número positivo.')
    name = project_name(project)
    source = Path(source).expanduser().absolute()
    if source.is_symlink() or not source.is_file():
        raise PreviewError('Informe um arquivo regular de preview, sem link simbólico.')
    host = tailnet_host()  # Falha de consulta não deixa uma cópia sem URL anunciável.
    directory = ensure_directory(previews_dir() / name / f'issue-{issue}')
    destination = directory / source.name
    descriptor, temporary = tempfile.mkstemp(prefix='.preview-', dir=directory)
    try:
        with os.fdopen(descriptor, 'wb') as output, source.open('rb') as input_file:
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
    command = commands.add_parser('publish', help='Copia um preview; nunca move ou sobrescreve outra versão.')
    command.add_argument('--project', type=Path, required=True)
    command.add_argument('--issue', type=int, required=True)
    command.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(publish(args.project, args.issue, args.file), ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print('Publicação recusada; confira projeto, arquivo, Tailscale e se o nome já possui outra versão.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
