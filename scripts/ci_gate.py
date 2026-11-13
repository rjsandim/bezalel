#!/usr/bin/env python3
"""Espera CI verde no SHA atual da PR; nunca corrige, publica ou integra código."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from check_delivery import ContractError, ContractParser, https_reference, require


def gh(project, *args, allowed=(0,)):
    try:
        result = subprocess.run(['gh', *args], cwd=project, text=True, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise ContractError('GitHub CLI ausente, indisponível ou excedeu o tempo; conteúdo omitido.') from None
    require(result.returncode in allowed, 'Consulta GitHub falhou; confira acesso e versão de gh (diagnóstico omitido).')
    return result


def pr_info(project, pr):
    info = json.loads(gh(project, 'pr', 'view', str(pr), '--json',
                         'number,url,state,isDraft,headRefOid,headRefName,baseRefName,closingIssuesReferences').stdout)
    require(info.get('number') == pr and info.get('state') == 'OPEN' and info.get('isDraft') is False,
            'PR deve estar aberta e pronta para revisão.')
    require(https_reference(info.get('url')) and bool(info.get('headRefOid')), 'Identidade da PR inválida.')
    return info


def read_checks(project, pr, required):
    args = ['pr', 'checks', str(pr), '--json', 'name,bucket,link']
    if required:
        args.append('--required')
    result = gh(project, *args, allowed=(0, 1, 8))
    # gh informa ausência de required com exit 1; erros de acesso NÃO viram fallback.
    if required and result.returncode == 1 and 'no required checks reported' in (result.stdout + result.stderr).lower():
        return []
    try:
        checks = json.loads(result.stdout)
    except ValueError:
        raise ContractError('Não foi possível ler checks do GitHub; não é CI verde.') from None
    require(isinstance(checks, list), 'Resposta de checks inválida.')
    if result.returncode == 1:
        require(any(c.get('bucket') in {'fail', 'cancel'} for c in checks), 'Consulta de checks falhou sem resultado verificável.')
    return checks


def observe(project, pr):
    before = pr_info(project, pr)
    checks = read_checks(project, pr, True)
    scope = 'required'
    if not checks:
        checks = read_checks(project, pr, False)
        scope = 'all'
    normalized = []
    for check in checks:
        require(isinstance(check, dict) and isinstance(check.get('name'), str), 'Check inválido.')
        bucket = check.get('bucket')
        status = 'passed' if bucket == 'pass' else 'failed' if bucket in {'fail', 'cancel'} else 'pending'
        url = check.get('link') or None
        require(url is None or https_reference(url), 'URL de check inválida.')
        normalized.append({'name': check['name'], 'status': status, 'url': url})
    after = pr_info(project, pr)
    status = 'failed' if any(c['status'] == 'failed' for c in normalized) else 'passed' if normalized and all(c['status'] == 'passed' for c in normalized) else 'pending'
    if before['headRefOid'] != after['headRefOid']:
        status = 'pending'
    return {'pr': pr, 'sha': after['headRefOid'], 'status': status, 'scope': scope,
            'checks': normalized, 'evidence': 'gh pr checks em ' + datetime.now(timezone.utc).isoformat()}


def gate(project, pr, timeout_seconds=1800, poll_seconds=30, dry_run=False):
    require(timeout_seconds >= 0 and poll_seconds > 0, 'Timeout/poll inválidos.')
    deadline = time.monotonic() + timeout_seconds
    while True:
        result = observe(project, pr)
        code = {'passed': 0, 'failed': 2, 'pending': 3}[result['status']]
        if code != 3 or dry_run or time.monotonic() >= deadline:
            return code, result
        time.sleep(min(poll_seconds, max(0, deadline - time.monotonic())))


def main():
    parser = ContractParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--pr', type=int, required=True)
    parser.add_argument('--timeout-seconds', type=float, default=1800)
    parser.add_argument('--poll-seconds', type=float, default=30)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        require(args.pr > 0, 'PR inválida.')
        code, result = gate(args.project.resolve(), args.pr, args.timeout_seconds, args.poll_seconds, args.dry_run)
        print(json.dumps(result, ensure_ascii=False))
        return code
    except (ContractError, ValueError, TypeError, KeyError):
        print('Não foi possível verificar a CI; confira PR, acesso e ferramentas. Nenhuma aprovação foi produzida.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
