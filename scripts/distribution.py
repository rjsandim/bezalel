"""Primitivas de distribuição: arquivos declarados, sem executar conteúdo importado."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


class DistributionError(ValueError):
    pass


IGNORED = {'.git', '.DS_Store', '__pycache__', 'state', 'backups', '.pytest_cache'}


def read_json(path):
    return json.loads(Path(path).read_text())


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inside(root, relative):
    """Recusa travessia e symlinks, inclusive os que ainda apontam para dentro."""
    root = Path(root).resolve()
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p in {'.', '..'} for p in path.parts):
        raise DistributionError('Caminho relativo inválido.')
    target = root
    for part in path.parts:
        target = target / part
        if target.is_symlink():
            raise DistributionError(f'Link não gerenciado no destino: {relative}')
    return target


def files(root):
    """Lê arquivos comuns e modos; nunca segue links ou inclui estado operacional."""
    root = Path(root)
    result = {}
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in IGNORED for part in rel.parts) or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_symlink():
            raise DistributionError(f'Link não permitido no pacote: {rel}')
        if path.is_file():
            result[rel.as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
    return result


def fingerprints(content):
    return {name: {'sha256': digest(data), 'mode': mode}
            for name, (data, mode) in content.items()}


def atomic_write(path, data, mode=0o644):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def git(root, *args, timeout=30):
    """Não dispara hooks nem prompts; erros omitem saídas que podem conter credenciais."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1')
    try:
        return subprocess.run(
            ['git', '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, env=env,
        ).stdout
    except (OSError, subprocess.SubprocessError) as error:
        raise DistributionError('Operação Git falhou ou excedeu o prazo; nenhuma saída privada foi exibida.') from error


def git_files(repo, revision, directory):
    """Lê blobs de uma revisão, sem checkout, filtros, hooks ou scripts do upstream."""
    records = git(repo, 'ls-tree', '-rz', revision, '--', directory).split(b'\0')
    result = {}
    for record in records:
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        rel = Path(name.decode()).relative_to(directory).as_posix()
        if mode not in {'100644', '100755'} or kind != 'blob':
            raise DistributionError('Upstream contém link/submódulo ou tipo de arquivo não suportado.')
        if any(part in IGNORED for part in Path(rel).parts):
            continue
        if rel.startswith('/') or '..' in Path(rel).parts:
            raise DistributionError('Caminho inválido no upstream.')
        result[rel] = (git(repo, 'cat-file', 'blob', oid), int(mode[-3:], 8))
    if 'SKILL.md' not in result:
        raise DistributionError('Skill selecionada ausente no upstream; remoção exige revisão.')
    return result


def replace_files(root, before, after):
    """Preflight completo e reversão dos arquivos em caso de falha de gravação."""
    root = Path(root)
    for name in before.keys() | after.keys():
        target = inside(root, name)
        actual = (target.read_bytes(), target.stat().st_mode & 0o777) if target.is_file() else None
        if actual != before.get(name) or (target.exists() and not target.is_file()):
            raise DistributionError(f'Arquivo alterado durante a operação: {name}')
    changed = []
    try:
        for name in sorted(before.keys() | after.keys()):
            if before.get(name) == after.get(name):
                continue
            target = inside(root, name)
            changed.append(name)
            if name in after:
                atomic_write(target, *after[name])
            else:
                target.unlink()
    except BaseException:
        for name in reversed(changed):
            target = inside(root, name)
            if name in before:
                atomic_write(target, *before[name])
            elif target.exists():
                target.unlink()
        raise
