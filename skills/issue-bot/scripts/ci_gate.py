#!/usr/bin/env python3
"""Portão de CI do modo issue-bot: lê `gh pr checks` e nunca corrige, mergeia ou faz deploy.

Saída: 0 verde; 1 erro de uso/ferramenta; 2 check exigido falhou ou foi cancelado;
3 pendente ao fim do prazo (ou em --dry-run). Imprime JSON no stdout.
Se o GitHub distingue checks obrigatórios (--required), só eles bloqueiam; senão, todos.
PR sem checks reportados conta como pendente: o portão não é satisfeito por ausência.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

FIELDS = 'name,bucket,state,link,workflow'
BUCKETS = {'pass': 'passed', 'skipping': 'skipped', 'fail': 'failed', 'cancel': 'failed', 'pending': 'pending'}


class GateError(RuntimeError):
    """Falha de uso ou de ferramenta (código 1)."""


def now():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def gh(project, *args):
    try:
        result = subprocess.run(['gh', *args], cwd=project, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        raise GateError('gh não encontrado; instale e autentique o GitHub CLI.') from None
    except subprocess.TimeoutExpired:
        raise GateError('gh não respondeu no prazo.') from None
    return result


def read_checks(project, pr, required):
    args = ['pr', 'checks', str(pr), '--json', FIELDS] + (['--required'] if required else [])
    result = gh(project, *args)
    output = result.stdout.strip()
    if output:
        try:
            data = json.loads(output)
        except ValueError:
            raise GateError('Saída de gh pr checks ilegível.') from None
        if isinstance(data, list):
            return data
        raise GateError('Saída de gh pr checks inesperada.')
    message = result.stderr.lower()
    # Sem checks (nenhum reportado, ou nenhum obrigatório) não é erro de ferramenta.
    if 'no checks' in message or 'no required checks' in message:
        return []
    if result.returncode != 0:
        raise GateError('gh pr checks falhou (código ' + str(result.returncode) + '); confira autenticação, repositório e PR.')
    return []


def head_sha(project, pr):
    result = gh(project, 'pr', 'view', str(pr), '--json', 'headRefOid,url')
    if result.returncode != 0:
        raise GateError('gh pr view falhou; confira a PR ' + str(pr) + ' no repositório do projeto.')
    try:
        data = json.loads(result.stdout)
        return data['headRefOid'], data.get('url')
    except (ValueError, KeyError, TypeError):
        raise GateError('Saída de gh pr view ilegível.') from None


def snapshot(project, pr):
    """Uma leitura: checks obrigatórios quando existirem, senão todos."""
    sha, url = head_sha(project, pr)
    scope = 'required'
    checks = read_checks(project, pr, required=True)
    if not checks:
        scope, checks = 'all', read_checks(project, pr, required=False)
    items = []
    for check in checks:
        if not isinstance(check, dict):
            raise GateError('Check em formato inesperado.')
        status = BUCKETS.get(check.get('bucket'), 'pending')
        items.append({'name': check.get('name') or check.get('workflow') or '?', 'status': status,
                      'url': check.get('link') or None})
    # Falha já conhecida devolve ao implementador sem esperar os checks restantes.
    if any(i['status'] == 'failed' for i in items):
        overall = 'failed'
    elif not items or any(i['status'] == 'pending' for i in items):
        overall = 'pending'
    else:
        overall = 'passed'
    return {'pr': pr, 'sha': sha, 'url': url, 'status': overall, 'scope': scope, 'checks': items,
            'evidence': 'gh pr checks em ' + now(), 'merge_autorizado': False}


CODES = {'passed': 0, 'failed': 2, 'pending': 3}


def gate(project, pr, timeout=1800, poll=30, dry_run=False, sleep=time.sleep, clock=time.monotonic):
    if type(pr) is not int or pr < 1:
        raise GateError('Informe --pr como inteiro >= 1.')
    deadline = clock() + max(timeout, 0)
    while True:
        state = snapshot(project, pr)
        if state['status'] != 'pending' or dry_run or clock() >= deadline:
            return CODES[state['status']], state
        sleep(max(1, min(poll, deadline - clock())))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--pr', required=True, type=int)
    parser.add_argument('--timeout-seconds', type=int, default=1800)
    parser.add_argument('--poll-seconds', type=int, default=30)
    parser.add_argument('--dry-run', action='store_true', help='uma leitura, sem esperar')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        if not project.is_dir():
            raise GateError('Pasta do projeto inexistente.')
        code, state = gate(project, args.pr, args.timeout_seconds, args.poll_seconds, args.dry_run)
    except GateError as error:
        print('Portão de CI: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
