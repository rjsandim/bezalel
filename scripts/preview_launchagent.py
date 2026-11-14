#!/usr/bin/env python3
"""Planeja/instala o servidor local de previews; nunca substitui processos existentes."""
import argparse
import json
import os
from pathlib import Path
import plistlib
import socket
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

from preview import PreviewError, ensure_directory, previews_dir


LABEL = 'com.bezalel.previews'
TEMPLATE = Path(__file__).resolve().parent / 'templates/preview-server.plist'


def configuration():
    logs = Path(os.environ.get('XDG_STATE_HOME') or str(Path.home() / '.local/state')) / 'bezalel/previews'
    values = {'PYTHON': sys.executable, 'PREVIEWS_DIR': str(previews_dir()), 'LOG_DIR': str(logs.absolute())}
    content = TEMPLATE.read_text()
    for key, value in values.items():
        content = content.replace('${' + key + '}', escape(value))
    plistlib.loads(content.encode())
    return content.encode(), logs


def port_in_use():
    with socket.socket() as listener:
        try:
            listener.bind(('127.0.0.1', 8000))
            return False
        except OSError:
            return True


def plan():
    content, _ = configuration()
    return {'label': LABEL, 'file': str(Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')),
            'listen': '127.0.0.1:8000', 'directory': str(previews_dir()),
            'arguments': plistlib.loads(content)['ProgramArguments'], 'installed': False}


def install():
    if sys.platform != 'darwin':
        raise PreviewError('LaunchAgent exige macOS.')
    content, logs = configuration()
    path = Path(plan()['file'])
    domain = f'gui/{os.getuid()}'
    # Um plist existente de outra configuração pertence ao operador.
    if path.is_symlink() or (path.exists() and path.read_bytes() != content):
        raise PreviewError('LaunchAgent existente diverge; preserve e revise sua configuração.')
    loaded = subprocess.run(['launchctl', 'print', f'{domain}/{LABEL}'], capture_output=True, timeout=30)
    if loaded.returncode == 0:
        if not path.is_file():
            raise PreviewError('Serviço carregado sem o plist esperado; revisão manual necessária.')
        return {**plan(), 'installed': True, 'changed': False}
    if port_in_use():
        raise PreviewError('Porta 8000 ocupada; preserve o processo existente e faça a transição manualmente.')
    ensure_directory(previews_dir())
    ensure_directory(logs)
    ensure_directory(path.parent)
    descriptor, temporary = tempfile.mkstemp(prefix='.preview-launchagent-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            output.write(content)
            output.flush()
            os.fchmod(output.fileno(), 0o600)
            os.fsync(output.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes() != content:
                raise PreviewError('LaunchAgent alterado durante a instalação; operação interrompida.')
    finally:
        Path(temporary).unlink(missing_ok=True)
    result = subprocess.run(['launchctl', 'bootstrap', domain, str(path)], capture_output=True, timeout=30)
    if result.returncode:
        raise PreviewError('Falha ao carregar LaunchAgent; plist preservado para diagnóstico. Nenhum processo foi encerrado.')
    verified = subprocess.run(['launchctl', 'print', f'{domain}/{LABEL}'], capture_output=True, timeout=30)
    if verified.returncode:
        raise PreviewError('Não foi possível confirmar o LaunchAgent; não declarar servidor pronto.')
    return {**plan(), 'installed': True, 'changed': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'install'))
    args = parser.parse_args()
    try:
        print(json.dumps(install() if args.command == 'install' else plan(), ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print('LaunchAgent não instalado/verificado; preserve o servidor atual e confira porta 8000 e configuração existente.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
