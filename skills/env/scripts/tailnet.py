#!/usr/bin/env python3
"""Portas privadas do Serve, com registro único por máquina e operações delimitadas."""
import argparse
import contextlib
import fcntl
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import uuid
import tempfile
from urllib.parse import urlsplit, urljoin


class TailnetError(ValueError):
    pass


def atomic_json(path, data):
    path = Path(path)
    if path.is_symlink():
        raise TailnetError('Estado não pode ser symlink.')
    fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def state_dir():
    return Path(os.environ.get('ENV_TAILNET_STATE_DIR') or
                str(Path(os.environ.get('XDG_STATE_HOME') or Path.home()/'.local/state')/'envstack/tailnet'))


def ts(*args):
    binary = os.environ.get('ENV_TAILSCALE_BIN') or shutil.which('tailscale')
    if not binary:
        raise TailnetError('Tailscale ausente; configure ENV_TAILSCALE_BIN.')
    result = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise TailnetError('Tailscale falhou; confira login, HTTPS e permissões (saída privada omitida).')
    return result.stdout


def hostname():
    data = json.loads(ts('status', '--json'))
    host = data.get('Self', {}).get('DNSName', '').rstrip('.')
    if data.get('BackendState') != 'Running' or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]+', host):
        raise TailnetError('Tailscale não está conectado ou Self.DNSName está ausente.')
    return host


def serve_status():
    data = json.loads(ts('serve', 'status', '--json'))
    if not isinstance(data, dict):
        raise TailnetError('Status Serve inválido.')
    return data


def occupied(config):
    ports = {int(p) for p in config.get('TCP', {})}
    for field in ('Web', 'AllowFunnel'):
        ports.update(int(host.rsplit(':', 1)[1]) for host in config.get(field, {}))
    # Configurações de foreground/services também reservam portas.
    for field in ('Foreground', 'Services'):
        for child in config.get(field, {}).values():
            ports.update(occupied(child))
    return ports


def safe_port(port):
    port = int(port)
    if not 1024 <= port <= 65535:
        raise TailnetError('Porta Tailnet deve estar entre 1024 e 65535; 443 é protegida.')
    return port


def own_mapping(config, host, port):
    address = f'{host}:{safe_port(port)}'
    handlers = config.get('Web', {}).get(address, {}).get('Handlers', {})
    return (config.get('TCP', {}).get(str(port)) == {'HTTPS': True}
            and handlers == {'/': {'Proxy': f'http://127.0.0.1:{port}'}}
            and [key for key in config.get('Web', {}) if int(key.rsplit(':', 1)[1]) == port] == [address]
            and not any(value for key, value in config.get('AllowFunnel', {}).items() if int(key.rsplit(':', 1)[1]) == port)
            and not config.get('AllowFunnel', {}).get(address, False)
            and not any(port in occupied(child) for field in ('Foreground', 'Services')
                        for child in config.get(field, {}).values()))


def listening(port):
    # Bind detecta também listeners em wildcard. Nenhuma conexão a app alheio.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


@contextlib.contextmanager
def registry():
    directory = state_dir()
    if directory.is_symlink():
        raise TailnetError('Diretório de registro não pode ser symlink.')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = directory/'registry.lock'
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'a+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        path = directory/'registry.json'
        if path.is_symlink():
            raise TailnetError('Registro não pode ser symlink.')
        data = json.loads(path.read_text()) if path.exists() else {'schema_version': 1, 'entries': {}}
        validate_registry(data)
        yield data


def validate_registry(data):
    if data.get('schema_version') != 1 or not isinstance(data.get('entries'), dict):
        raise TailnetError('Registro Tailnet inválido; preserve-o para diagnóstico.')
    ports = []
    for key, entry in data['entries'].items():
        if key != identity(entry['root'], entry['project'], entry['environment'], entry['folder']):
            raise TailnetError('Identidade divergente no registro.')
        ports.append(safe_port(entry['port']))
    if len(ports) != len(set(ports)):
        raise TailnetError('Registro possui portas duplicadas.')


def identity(root, project, environment, folder):
    return json.dumps([str(Path(root).resolve()), project, environment, folder], separators=(',', ':'))


def allocate(root, project, environment, folder, start=41000, end=41999, owner=None, attempt=None):
    start, end = safe_port(start), safe_port(end)
    if start > end:
        raise TailnetError('Faixa Tailnet inválida.')
    key = identity(root, project, environment, folder)
    with registry() as data:
        host = hostname()
        config = serve_status()
        if key in data['entries']:
            entry = data['entries'][key]
            if entry['host'] != host:
                raise TailnetError('Hostname mudou; preserve o registro e audite antes de realocar.')
            return entry
        used = occupied(config) | {e['port'] for e in data['entries'].values()}
        width = end-start+1
        preferred = int(hashlib.sha256(key.encode()).hexdigest(), 16) % width
        for offset in range(width):
            port = start + (preferred+offset) % width
            if port not in used and not listening(port):
                entry = {'root': str(Path(root).resolve()), 'project': project, 'environment': environment,
                         'folder': folder, 'port': port, 'host': host, 'url': f'https://{host}:{port}/'}
                if owner:
                    entry.update(owner_state=str(Path(owner).resolve()), docker_context=os.environ['DOCKER_CONTEXT'])
                if attempt:
                    entry['attempt_id'] = attempt
                data['entries'][key] = entry
                atomic_json(state_dir()/'registry.json', data)
                return entry
        raise TailnetError('Faixa Tailnet esgotada; nenhum recurso foi alterado.')


def mutate(root, project, environment, folder, action):
    key = identity(root, project, environment, folder)
    with registry() as data:
        return mutate_locked(data, key, action)


def mutate_locked(data, key, action):
    entry = data['entries'].get(key)
    if entry is None:
        if action == 'release':
            return None
        raise TailnetError('Serviço sem alocação Tailnet.')
    port = safe_port(entry['port'])
    host = hostname()
    if host != entry['host']:
        raise TailnetError('Hostname divergente; Serve preservado.')
    config = serve_status()
    exists = port in occupied(config)
    owned = own_mapping(config, host, port)
    if exists and not owned:
        raise TailnetError('Porta ocupada por configuração alheia; Serve e registro preservados.')
    if action == 'publish':
        if os.environ.get('ENV_ALLOW_SHARED_INFRA') != '1':
            raise TailnetError('Publish exige ENV_ALLOW_SHARED_INFRA=1 nesta execução.')
        if not owned:
            ts('serve', '--bg', '--yes', f'--https={port}', f'http://127.0.0.1:{port}')
            if not own_mapping(serve_status(), host, port):
                raise TailnetError('Serve não confirmou a publicação; registro preservado.')
    elif action == 'release':
        if owned:
            ts('serve', '--bg', '--yes', f'--https={port}', 'off')
            if port in occupied(serve_status()):
                raise TailnetError('Serve não confirmou a liberação; registro preservado.')
        del data['entries'][key]
        atomic_json(state_dir()/'registry.json', data)
    else:
        raise TailnetError('Operação inválida.')
    return entry


def entries():
    path = state_dir()/'registry.json'
    if path.is_symlink():
        raise TailnetError('Registro não pode ser symlink.')
    data = json.loads(path.read_text()) if path.exists() else {'schema_version': 1, 'entries': {}}
    validate_registry(data)
    return list(data['entries'].values())


def manifest(path):
    result = subprocess.run(['yq', '-o=json', '.', str(path)], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise TailnetError('Manifesto inválido.')
    return json.loads(result.stdout)


def selection(config, name):
    options = config.get('tailnet') or {}
    if options is True:
        options = {}
    if not isinstance(options, dict):
        raise TailnetError('tailnet deve ser mapa ou true.')
    # Sobrescrita por ambiente é opcional; não muda o padrão dos demais.
    options = {**options, **options.get('environments', {}).get(name, {})}
    primary = options.get('primary')
    requested = options.get('services', [])
    selected = [s for s in config['services'] if s.get('tailnet') or s['folder'] in requested or s['folder'] == primary]
    if config.get('access') == 'tailnet' and not selected:
        raise TailnetError('access: tailnet exige serviço primário ou serviços tailnet explícitos.')
    if primary and primary not in {s['folder'] for s in selected}:
        raise TailnetError('Serviço primário Tailnet ausente.')
    if set(requested) - {s['folder'] for s in config['services']}:
        raise TailnetError('Serviço Tailnet solicitado não existe.')
    return options, selected


def prepare(root, state, name, attempt_path=None):
    config = manifest(root/'.envstack/stack.yaml')
    options, selected = selection(config, name)
    saved = state/'tailnet.json'
    previous = json.loads(saved.read_text()) if saved.exists() else None
    if previous and {s['folder'] for s in previous['services']} != {s['folder'] for s in selected}:
        raise TailnetError('Seleção Tailnet mudou; libere os vínculos antigos explicitamente antes de regenerar.')
    if not selected:
        return
    attempt = str(uuid.uuid4()) if attempt_path else None
    if attempt_path:
        atomic_json(attempt_path, {'id': attempt, 'root': str(root.resolve()), 'previous': previous})
    result = {'access': config.get('access', 'local'), 'attempt_id': attempt, 'host': None, 'primary': options.get('primary', selected[0]['folder']), 'services': []}
    for service in selected:
        entry = allocate(root, config['project'], name, service['folder'],
                         options.get('port_start', 41000), options.get('port_end', 41999),
                         owner=state, attempt=attempt)
        result['host'] = entry['host']
        service_options = service.get('tailnet') if isinstance(service.get('tailnet'), dict) else {}
        probe_path = service_options.get('probe_path', '/')
        validate_probe_path(entry['url'], probe_path)
        statuses = service_options.get('probe_statuses')
        if statuses is not None and (not isinstance(statuses, list) or not statuses or
                any(type(code) is not int or not 200 <= code < 500 for code in statuses)):
            raise TailnetError('probe_statuses exige lista de códigos HTTP entre 200 e 499.')
        result['services'].append({**entry, 'probe_path': probe_path, 'probe_statuses': statuses, 'container_port': int(service['port']),
                                   'checks': (service.get('tailnet') or {}).get('checks', {})
                                   if isinstance(service.get('tailnet'), dict) else {}})
    atomic_json(saved, result)


LOCAL = re.compile(r'(?i)(?:(?<![a-z0-9_-])(?:localhost|127\.0\.0\.1)|\.local)(?=[:/\s\"\x27,;?&#)]|$)')

def public_variable(name):
    name = name.upper()
    # HOST de DB/cache/mail é conexão interna, não origem do navegador.
    if re.match(r'^(?:DB|DATABASE|REDIS|CACHE|MAIL|SMTP|MEMCACHED)(?:_|$)', name):
        return False
    return bool(re.search(r'URL|ORIGIN|CORS|CALLBACK', name) or
                name in {'APP_HOST','PUBLIC_HOST','FRONTEND_HOST','VITE_HOST','NEXT_PUBLIC_HOST','HOST'})


def env_warnings(worktree, services):
    warnings = []
    for entry in services:
        path = worktree/entry['folder']/'.env'
        if not path.is_file():
            continue
        for line in path.read_text().splitlines():
            match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)', line)
            if match and public_variable(match[1]) and LOCAL.search(match[2]):
                warnings.append({'folder': entry['folder'], 'variable': match[1],
                                 'message': 'Revise .envstack/*.env.example com ${env:public.url.*}; .env existente é preservado.'})
    return warnings


def request(url, websocket=False):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise TailnetError('Check exige HTTPS sem credenciais.')
    conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=2)
    headers = {}
    if websocket:
        headers = {'Connection': 'Upgrade', 'Upgrade': 'websocket', 'Sec-WebSocket-Version': '13',
                   'Sec-WebSocket-Key': 'dGhlIHNhbXBsZSBub25jZQ=='}
    try:
        conn.request('GET', parsed.path + ('?' + parsed.query if parsed.query else ''), headers=headers)
        response = conn.getresponse()
        # Não segue Location nem subrecursos: nunca acessa alvos descobertos na página.
        body = '' if response.status == 101 else response.read(1024*1024).decode('utf-8', errors='replace')
        return response.status, response.getheaders(), body
    finally:
        conn.close()


def validate_probe_path(base, path):
    if not isinstance(path, str) or not path.startswith('/') or path.startswith('//'):
        raise TailnetError('Caminho de check precisa ser relativo à origem Tailnet.')
    target = urljoin(base, path)
    if urlsplit(target).netloc != urlsplit(base).netloc or urlsplit(target).scheme != 'https':
        raise TailnetError('Caminho de check precisa ser relativo à origem Tailnet.')
    return target


def probe(entry, kind, path):
    target = validate_probe_path(entry['url'], path)
    base = entry['url']
    try:
        code, headers, body = request(target, websocket=kind == 'websocket')
        problems = []
        if LOCAL.search(body):
            problems.append('Resposta contém referência a localhost/127.0.0.1/.local.')
        locations = [v for k, v in headers if k.lower() == 'location']
        for location in locations:
            destination = urlsplit(urljoin(target, location))
            origin = urlsplit(base)
            if destination.scheme != 'https' or destination.netloc != origin.netloc:
                problems.append('Redirect sai da origem HTTPS Tailnet; confira Location.')
        for key, value in headers:
            if key.lower() == 'set-cookie':
                if LOCAL.search(value) or ('domain=' in value.lower() and
                        not re.search(r'domain=\.?'+re.escape(entry['host'])+r'(?:;|$)', value, re.I)):
                    problems.append('Cookie tem domínio incompatível com Tailnet.')
                if not re.search(r'(?:^|;)\s*secure(?:;|$)', value, re.I):
                    problems.append('Cookie sem Secure; confira autenticação no Safari.')
        valid = (code == 101 and any(k.lower() == 'upgrade' and v.lower() == 'websocket' for k,v in headers)
                 if kind == 'websocket' else (300 <= code < 400 and bool(locations))
                 if kind == 'redirect' else code in entry['probe_statuses']
                 if kind == 'page' and entry.get('probe_statuses') is not None else 200 <= code < 400)
        return {'kind': kind, 'path': path, 'http_code': code, 'ok': valid and not problems, 'warnings': problems}
    except (OSError, http.client.HTTPException, ValueError):
        return {'kind': kind, 'path': path, 'http_code': None, 'ok': False, 'warnings': ['Requisição HTTPS falhou.']}


def page_probe(entry):
    result = probe(entry, 'page', entry.get('probe_path', '/'))
    # Uma repetição curta apenas para falha de transporte; não mascara HTTP ruim.
    if result['http_code'] is None:
        result = probe(entry, 'page', entry.get('probe_path', '/'))
    return result


def report(root, state, name, full=False):
    saved = state/'tailnet.json'
    if not saved.is_file():
        return {'host': None, 'services': [], 'warnings': []}
    data = json.loads(saved.read_text())
    config = serve_status()
    host = hostname()
    registered = {identity(e['root'],e['project'],e['environment'],e['folder']): e for e in entries()}
    results = []
    for entry in data['services']:
        key = identity(root, entry['project'], name, entry['folder'])
        registered_entry = registered.get(key, {})
        owned = all(registered_entry.get(k) == entry[k] for k in ('root','project','environment','folder','port','host','url'))
        ok = owned and host == entry['host'] and own_mapping(config, host, entry['port'])
        checks = [page_probe(entry)] if ok else [{'kind': 'page', 'path': '/', 'http_code': None, 'ok': False, 'warnings': ['Vínculo Serve não confirmado; HTTP não consultado.']}]
        if full and ok:
            for kind in ('static', 'redirect', 'api', 'health', 'websocket', 'login'):
                paths = entry.get('checks', {}).get(kind, [])
                if isinstance(paths, str): paths = [paths]
                checks.extend(probe(entry, kind, path) for path in paths)
                if not paths:
                    checks.append({'kind': kind, 'status': 'not_configured', 'ok': None})
        results.append({k:entry[k] for k in ('folder','url','port')} | {
            'serve_ok': ok, 'probe_ok': checks[0]['ok'], 'probe_path': entry.get('probe_path', '/'), 'http_code': checks[0]['http_code'] if checks else None,
            'checks': checks})
    return {'host': data['host'], 'services': results, 'primary': data['primary'],
            'warnings': env_warnings(root/'.worktrees'/name, data['services'])}


def configure(root, compose):
    if manifest(root/'.envstack/stack.yaml').get('access') != 'tailnet':
        return
    result = subprocess.run(['yq', '-o=json', '.', str(compose)], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise TailnetError('Compose inválido; nenhuma configuração publicada.')
    config = json.loads(result.stdout)
    config.get('networks', {}).pop('proxy', None)
    for service in config['services'].values():
        service.pop('labels', None)
        networks = service.get('networks', ['internal'])
        if isinstance(networks, dict):
            service['networks'] = {key: value for key, value in networks.items() if key != 'proxy'}
        else:
            service['networks'] = [network for network in networks if network != 'proxy']
        # Bancos exclusivos continuam acessíveis na IDE só pelo loopback.
        # O modo só-tailnet não deixa bindings públicos de infraestrutura.
        ports = []
        for binding in service.get('ports', []):
            if isinstance(binding, str):
                parts = binding.split(':')
                if len(parts) not in (2, 3):
                    raise TailnetError('Binding Compose inesperado; confira as portas.')
                ports.append('127.0.0.1:' + ':'.join(parts[-2:]))
            elif isinstance(binding, dict):
                ports.append({**binding, 'host_ip': '127.0.0.1'})
            else:
                raise TailnetError('Binding Compose inválido.')
        if ports:
            service['ports'] = ports
    atomic_json(compose, config)


def compose_config(state):
    result = subprocess.run(['docker', 'compose', '-f', str(state/'docker-compose.yml'),
                             'config', '--format', 'json'], capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise TailnetError('Não foi possível conferir bindings Compose; Serve preservado.')
    return json.loads(result.stdout)


def binding_matches(config, entry):
    ports = config.get('services', {}).get(entry['folder'], {}).get('ports', [])
    return any(isinstance(p, dict) and p.get('host_ip') == '127.0.0.1'
               and str(p.get('published')) == str(entry['port'])
               and str(p.get('target')) == str(entry['container_port'])
               and p.get('protocol', 'tcp') == 'tcp' for p in ports)


def lifecycle(state, action, folders):
    path = state/'tailnet.json'
    if not path.exists(): return
    data = json.loads(path.read_text())
    selected = [entry for entry in data['services'] if not folders or entry['folder'] in folders]
    if action == 'publish' and selected:
        config = compose_config(state)
        if not all(binding_matches(config, entry) for entry in selected):
            raise TailnetError('Binding loopback Compose diverge do registro; rode update antes de publicar.')
    for entry in selected:
        mutate(entry['root'], entry['project'], entry['environment'], entry['folder'], action)


def complete_attempt(state, attempt_path):
    if not attempt_path.is_file() or not attempt_path.read_text().strip():
        return
    attempt = json.loads(attempt_path.read_text())
    saved = json.loads((state/'tailnet.json').read_text())
    if saved.get('attempt_id') != attempt['id']:
        raise TailnetError('Tentativa superada; preserve os recibos e reconcilie o ambiente.')
    with registry() as data:
        keys = [identity(entry['root'], entry['project'], entry['environment'], entry['folder']) for entry in saved['services']]
        if any(key not in data['entries'] for key in keys):
            raise TailnetError('Reserva mudou antes de concluir a geração.')
        atomic_json(attempt_path, {**attempt, 'completed': True})
        for key in keys:
            data['entries'][key].pop('attempt_id', None)
        atomic_json(state_dir()/'registry.json', data)


def rollback(state, attempt_path):
    if not attempt_path.is_file() or not attempt_path.read_text().strip():
        return
    attempt = json.loads(attempt_path.read_text())
    if attempt.get('completed'):
        return
    failures = []
    with registry() as data:
        for key, entry in list(data['entries'].items()):
            if entry.get('attempt_id') != attempt['id'] or entry['root'] != attempt['root']:
                continue
            try:
                mutate_locked(data, key, 'release')
            except (OSError, ValueError, subprocess.SubprocessError):
                failures.append(entry['folder'])
    if failures:
        raise TailnetError('Rollback Tailnet incompleto; preserve o recibo e repita rollback após diagnosticar o Serve.')
    saved = state/'tailnet.json'
    if saved.is_file() and json.loads(saved.read_text()).get('attempt_id') == attempt['id']:
        if attempt['previous'] is None:
            saved.unlink()
        else:
            atomic_json(saved, attempt['previous'])


def confirmed_missing(path):
    try:
        path.lstat()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


def environment_absent(entry):
    state = Path(entry.get('owner_state', ''))
    root = Path(entry['root'])
    context = entry.get('docker_context')
    if not context or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', context) or not entry.get('owner_state'):
        return False
    # Ausência em disco desconectado, link ou origem legada não é prova.
    if (not root.is_dir() or not state.is_absolute() or not state.parent.parent.is_dir()
            or not confirmed_missing(state) or not confirmed_missing(root/'.worktrees'/entry['environment'])):
        return False
    result = subprocess.run(['docker', '--context', context, 'ps', '-aq', '--filter',
                             f'label=com.docker.compose.project={entry["project"]}-{entry["environment"]}'],
                            capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise TailnetError('Docker não confirmou ausência do ambiente; reserva preservada.')
    return not result.stdout.strip()


def prune(root, project, environment):
    result = {'released': [], 'preserved': []}
    with registry() as data:
        for key, entry in list(data['entries'].items()):
            if (entry['root'], entry['project'], entry['environment']) != (str(root.resolve()), project, environment):
                continue
            if not environment_absent(entry):
                result['preserved'].append({'folder': entry['folder'], 'reason': 'ausencia_nao_comprovada'})
                continue
            try:
                mutate_locked(data, key, 'release')
                result['released'].append(entry['folder'])
            except TailnetError:
                result['preserved'].append({'folder': entry['folder'], 'reason': 'serve_divergente_ou_indisponivel'})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['allocate','publish','check','release','list','prepare','publish-state','release-state','configure','rollback','complete-attempt','prune'])
    parser.add_argument('--root', type=Path)
    parser.add_argument('--state', type=Path)
    parser.add_argument('--environment')
    parser.add_argument('--project')
    parser.add_argument('--service')
    parser.add_argument('--start', type=int, default=41000)
    parser.add_argument('--end', type=int, default=41999)
    parser.add_argument('--compose', type=Path)
    parser.add_argument('--attempt', type=Path)
    parser.add_argument('folders', nargs='*')
    args = parser.parse_args()
    required = {'list': [], 'configure': ['root','compose'],
                'prepare': ['root','state','environment'], 'check': ['root','state','environment'],
                'publish-state': ['state'], 'release-state': ['state'],
                'rollback': ['state','attempt'], 'complete-attempt': ['state','attempt'], 'prune': ['root','project','environment']}.get(
                    args.command, ['root','project','environment','service'])
    for field in required:
        if getattr(args, field) is None:
            parser.error(f'Informe --{field}.')
    try:
        if args.command == 'list': result = entries()
        elif args.command == 'prepare': result = prepare(args.root, args.state, args.environment, args.attempt)
        elif args.command == 'complete-attempt': result = complete_attempt(args.state, args.attempt)
        elif args.command == 'rollback': result = rollback(args.state, args.attempt)
        elif args.command == 'prune': result = prune(args.root, args.project, args.environment)
        elif args.command == 'configure': result = configure(args.root, args.compose)
        elif args.command in ('publish-state','release-state'):
            result = lifecycle(args.state, args.command.split('-')[0], args.folders)
        elif args.command == 'check':
            result = report(args.root, args.state, args.environment, full=True)
        elif args.command == 'allocate':
            result = allocate(args.root,args.project,args.environment,args.service,args.start,args.end)
        else:
            result = mutate(args.root,args.project,args.environment,args.service,args.command)
        if result is not None: print(json.dumps(result, ensure_ascii=False))
        if args.command == 'check':
            return 0 if result['services'] and not result['warnings'] and all(s['serve_ok'] and all(c['ok'] is not False for c in s['checks']) for s in result['services']) else 5
        return 0
    except TailnetError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        # Nunca ecoa saída de ferramentas, envs ou corpos HTTP privados.
        print('Tailnet falhou; confira registro, configuração e disponibilidade (dados privados omitidos).', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
