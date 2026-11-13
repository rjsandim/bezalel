#!/usr/bin/env python3
"""Status do ambiente em JSON, a partir do manifesto e de `docker compose ps --format json`.

Chamado por ctl.sh status --json com dados em variáveis ES_*; não lê .env nem segredos.
Saída 0 quando os serviços pedidos (ou o conjunto ativo) estão prontos; 5 quando não.
"""
import json
import os
from pathlib import Path
import sys


def read_state(directory, name):
    path = Path(directory) / name
    return path.read_text().strip() if path.is_file() else None


def compose_entries(raw):
    """Compose v2 emite um array JSON (versões antigas) ou uma linha JSON por container."""
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith('['):
        return json.loads(raw)
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def main():
    env = os.environ
    project, name, tld = env['ES_PROJECT'], env['ES_NAME'], env['ES_TLD']
    state_dir = env['ES_STATE_DIR']
    states = {}
    for entry in compose_entries(env.get('ES_PS', '')):
        service = entry.get('Service')
        if service:
            running = entry.get('State') == 'running'
            health = entry.get('Health') or ''
            states[service] = running and health in ('', 'healthy')
    requested = [s for s in env.get('ES_REQUESTED', '').splitlines() if s.strip()]
    services = []
    for item in json.loads(env.get('ES_SERVICES') or '[]'):
        folder = item['folder']
        aliases = item.get('aliases') or []
        services.append({
            'folder': folder,
            'url': f'https://{name}-{folder}.{project}.{tld}',
            'port': item.get('port'),
            'ready': states.get(folder, False),
            'aliases': [f'https://{name}-{folder}-{alias}.{project}.{tld}' for alias in aliases],
        })
    issue = read_state(state_dir, 'issue')
    ready = bool(requested) and all(states.get(service, False) for service in requested)
    print(json.dumps({
        'project': project,
        'environment': name,
        'issue': int(issue) if issue and issue.isdigit() else None,
        'branch': read_state(state_dir, 'worktree-branch'),
        'source_branch': read_state(state_dir, 'source-branch'),
        'worktree': env['ES_WORKTREE'],
        'docker_context': env['ES_CONTEXT'],
        'ready': ready,
        'requested_services': requested,
        'services': services,
        'database': {'engine': env['ES_DB_ENGINE'], 'host': 'localhost', 'port': int(env['ES_DB_PORT'])},
    }, ensure_ascii=False, indent=2))
    return 0 if ready else 5


if __name__ == '__main__':
    sys.exit(main())
