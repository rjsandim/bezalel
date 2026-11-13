#!/usr/bin/env python3
"""Orquestrador do modo issue-bot: uma issue por vez, Codex implementa, CI verde, Claude revisa.

Uso: issue_bot.py <comando> --project <pasta-do-projeto> --issue <n> [opções]
Comandos: session-up, session-down, implement, ci-gate, review, respond, env-up, status,
prepare-prompt <implement|review|respond|corrigir-ci|subir-ambiente>, approve-restore (humano, em TTY).

Códigos: 0 etapa concluída (CI verde; review com pode_mergear; ambiente pronto);
1 erro de uso, contrato inválido, ferramenta ausente ou CLI sem login;
2 CI vermelha ou veredito ajustes; 3 CI pendente ou espera esgotada;
4 limite de rodadas sem decisão humana; 5 ambiente/dados/infra aguardam decisão.
Nenhum código autoriza merge. Este CLI nunca chama `gh pr merge`, deploy ou chave de API.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
sys.dont_write_bytecode = True  # não deixa __pycache__ dentro da skill instalada
sys.path.insert(0, str(SCRIPTS))
import check_handoff as handoff  # noqa: E402
import ci_gate  # noqa: E402

OK, ERROR, ADJUST, PENDING, LIMIT, DECISION = 0, 1, 2, 3, 4, 5
PROMPTS = {'implement': 'implementar.md', 'review': 'revisar.md', 'respond': 'responder-handoff.md',
           'corrigir-ci': 'corrigir-ci.md', 'subir-ambiente': 'subir-ambiente.md'}
PLACEHOLDER = re.compile(r'\{\{([a-z_]+)\}\}')
CRITERIA_HEADING = re.compile(r'^\s*(#{1,6}\s*|\*\*)?\s*(crit[ée]rios?\s+de\s+aceit(e|a[çc][ãa]o)|acceptance\s+criteria)\b', re.I)


class BotError(RuntimeError):
    def __init__(self, message, code=ERROR):
        super().__init__(message)
        self.code = code


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def run(args, cwd, env=None, check=False, timeout=600):
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout)
    except FileNotFoundError:
        raise BotError(args[0] + ' não encontrado no PATH.') from None
    except subprocess.TimeoutExpired:
        raise BotError(args[0] + ' não respondeu no prazo.') from None
    if check and result.returncode != 0:
        raise BotError(' '.join(args[:3]) + ' falhou (código ' + str(result.returncode) + ').')
    return result


# ─── Projeto ───────────────────────────────────────────────────

class Context:
    def __init__(self, args):
        self.args = args
        if args.issue is None or args.issue < 1:
            raise BotError('Informe --issue como inteiro >= 1.')
        self.issue = args.issue
        project = Path(args.project).resolve()
        top = run(['git', 'rev-parse', '--show-toplevel'], project)
        if top.returncode != 0 or Path(top.stdout.strip()).resolve() != project:
            raise BotError('--project deve ser a raiz do repositório do projeto.')
        self.project = project
        self.config = self.read_config()
        name = args.project_name or (self.config or {}).get('project') or project.name
        self.project_name = re.sub(r'[\s_]+', '-', name.strip().lower())
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', self.project_name):
            raise BotError('Nome do projeto inválido para a sessão; use --project-name em kebab-case.')
        self.session = self.project_name + '-' + str(self.issue)
        self.env_name = args.env_name or 'issue-' + str(self.issue)
        self.branch = args.branch or self.env_name
        self.handoff_dir = project / handoff.HANDOFF_DIR

    def read_config(self):
        path = self.project / '.bezalel/project.json'
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, ValueError):
            raise BotError('.bezalel/project.json ilegível; conteúdo omitido.') from None

    def ensure_ignored(self, folder):
        probe = '.bezalel/' + folder + '/probe'
        if run(['git', 'check-ignore', '-q', '--no-index', probe], self.project).returncode != 0:
            raise BotError('.bezalel/' + folder + '/ não está ignorado pelo Git. Acrescente /handoff/ e /logs/ '
                           'em .bezalel/.gitignore antes de continuar; handoffs e logs não entram no Git.')

    def gh_json(self, *args):
        result = run(['gh', *args], self.project, timeout=120)
        if result.returncode != 0:
            raise BotError('gh ' + ' '.join(args[:2]) + ' falhou; confira autenticação do gh e o repositório.')
        try:
            return json.loads(result.stdout)
        except ValueError:
            raise BotError('Saída do gh ilegível.') from None

    def issue_data(self):
        if not hasattr(self, '_issue'):
            data = self.gh_json('issue', 'view', str(self.issue), '--json', 'number,title,body,url')
            if not isinstance(data, dict) or data.get('number') != self.issue:
                raise BotError('Issue retornada pelo gh diverge da solicitada.')
            self._issue = data
        return self._issue

    def pr_number(self, required=True):
        if self.args.pr:
            return self.args.pr
        found = handoff.scan(self.handoff_dir, self.issue) if self.handoff_dir.is_dir() else {}
        for key in sorted(found, reverse=True):
            try:
                pr = json.loads(found[key].read_text()).get('pr')
            except (OSError, ValueError, AttributeError):
                continue
            if isinstance(pr, int) and pr > 0:
                return pr
        try:
            prs = self.gh_json('pr', 'list', '--state', 'open', '--limit', '100', '--json',
                               'number,headRefName,isCrossRepository,closingIssuesReferences')
        except BotError:
            prs = self.gh_json('pr', 'list', '--state', 'open', '--limit', '100', '--json', 'number,headRefName,isCrossRepository')
        # PR de fork nunca é escolhida por inferência: qualquer um pode escrever "Closes #<n>".
        matches = [p['number'] for p in prs if isinstance(p, dict) and p.get('isCrossRepository') is False and (
            any(ref.get('number') == self.issue for ref in p.get('closingIssuesReferences') or [])
            or p.get('headRefName') == self.branch)]
        if len(set(matches)) == 1:
            return matches[0]
        if required:
            raise BotError('PR vinculada à issue não identificada (' + str(len(set(matches))) + ' candidatas); informe --pr.')
        return None


# ─── Rodadas ───────────────────────────────────────────────────

def round_state(ctx, cycle=None):
    found = handoff.scan(ctx.handoff_dir, ctx.issue)
    existing = handoff.cycles(found)
    cycle = cycle or (existing[-1] if existing else 1)
    rounds = handoff.rounds(found, cycle)
    last = rounds[-1] if rounds else 0
    limit, decision = handoff.allowed_rounds(ctx.handoff_dir, ctx.issue, cycle)
    return {'found': found, 'cycle': cycle, 'last': last, 'limit': limit, 'decision': decision,
            'claude': (cycle, last, 'claude') in found, 'codex': (cycle, last, 'codex') in found,
            'cycles': existing}


def handoff_path(ctx, cycle, rnd, role):
    return ctx.handoff_dir / handoff.file_name(ctx.issue, cycle, rnd, role)


def relative(ctx, path):
    return str(Path(path).relative_to(ctx.project))


def wait_for(path, seconds, poll, sleep=time.sleep, clock=time.monotonic):
    """Espera o arquivo existir com JSON completo (tamanho estável entre duas leituras)."""
    deadline = clock() + max(seconds, 0)
    previous = None
    while True:
        if path.is_file():
            size = path.stat().st_size
            if size and size == previous:
                try:
                    json.loads(path.read_text(encoding='utf-8'))
                    return True
                except (OSError, ValueError):
                    pass
            previous = size
            if seconds == 0:
                return True
        if clock() >= deadline:
            return False
        sleep(max(1, poll))


# ─── Prompts e sessão ──────────────────────────────────────────

def acceptance_criteria(body):
    lines = (body or '').splitlines()
    for index, line in enumerate(lines):
        if CRITERIA_HEADING.match(line):
            collected = []
            for item in lines[index + 1:]:
                # Próximo título Markdown ou linha só em negrito encerra a seção.
                if item.lstrip().startswith('#') or (collected and re.fullmatch(r'\*\*[^*]+\*\*:?', item.strip())):
                    break
                collected.append(item)
            text = '\n'.join(collected).strip()
            if text:
                return text
    return ('(A issue não traz uma seção "Critérios de aceite". Não invente critérios: '
            'interrompa e peça ao humano que os registre na issue.)')


def render(kind, values):
    template = (SKILL / 'prompts' / PROMPTS[kind]).read_text(encoding='utf-8')
    missing = sorted(set(PLACEHOLDER.findall(template)) - set(values))
    if missing:
        raise BotError('Prompt ' + kind + ' sem valor para: ' + ', '.join(missing) + '.')
    # Substituição em uma passada: conteúdo da issue nunca é reinterpretado como placeholder.
    return PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), template)


def fence_for(*texts):
    """Cerca mais longa que qualquer sequência de crases do conteúdo: a issue não fecha o bloco."""
    longest = max([len(run) for text in texts for run in re.findall(r'`+', text)] or [0])
    return '`' * max(4, longest + 1)


def base_values(ctx):
    issue = ctx.issue_data()
    body = issue.get('body') or ''
    title = ' '.join((issue.get('title') or '').split()).replace('`', "'")
    criteria = acceptance_criteria(body)
    return {
        'issue': ctx.issue, 'issue_url': issue.get('url') or '', 'issue_title': title,
        'issue_body': body.strip() or '(issue sem descrição)', 'acceptance_criteria': criteria,
        'fence': fence_for(body, criteria),
        'project_root': str(ctx.project), 'branch': ctx.branch, 'worktree': '.worktrees/' + ctx.env_name,
        'environment': ctx.env_name, 'session': ctx.session,
        'schema_path': str(SKILL / 'references/handoff.schema.json'),
        'claude_example_path': str(SKILL / 'references/handoff-claude.example.json'),
        'codex_example_path': str(SKILL / 'references/handoff-codex.example.json'),
        'max_rounds': handoff.MAX_ROUNDS,
    }


def check_command(ctx, cycle, rnd):
    return ('python3 ' + str(SCRIPTS / 'check_handoff.py') + ' --project ' + str(ctx.project) + ' --issue '
            + str(ctx.issue) + ' --cycle ' + str(cycle) + ' --round ' + str(rnd))


def review_values(ctx, pr, cycle, rnd, limit, ci_state=None):
    values = base_values(ctx)
    claude = handoff_path(ctx, cycle, rnd, 'claude')
    previous = handoff_path(ctx, cycle, rnd - 1, 'codex') if rnd > 1 else None
    values.update({
        'pr': pr, 'pr_url': (ci_state or {}).get('url') or 'PR #' + str(pr), 'round': rnd, 'cycle': cycle,
        'max_rounds': limit, 'handoff_path': relative(ctx, claude), 'claude_handoff_path': relative(ctx, claude),
        'codex_handoff_path': relative(ctx, handoff_path(ctx, cycle, rnd, 'codex')),
        'previous_codex_path': relative(ctx, previous) if previous else '(primeira rodada: não há resposta anterior)',
        'ci_summary': ci_summary(ci_state), 'check_command': check_command(ctx, cycle, rnd),
    })
    return values


def ci_summary(state):
    if not state:
        return '(estado da CI não consultado)'
    lines = ['Status: ' + state['status'] + ' (SHA ' + str(state.get('sha')) + ', ' + state['evidence'] + ')']
    lines += ['- ' + c['name'] + ': ' + c['status'] + (' — ' + c['url'] if c.get('url') else '') for c in state['checks']]
    return '\n'.join(lines)


def send(ctx, window, text):
    if ctx.args.dry_run:
        print(text)
        return
    with tempfile.NamedTemporaryFile('w', suffix='.md', prefix='issue-bot-', delete=False, encoding='utf-8') as stream:
        stream.write(text)
        name = stream.name
    try:
        result = run(['bash', str(SCRIPTS / 'issue_session.sh'), 'send', '--session', ctx.session,
                      '--window', window, '--text-file', name], ctx.project)
    finally:
        os.unlink(name)
    if result.returncode != 0:
        raise BotError('Envio à janela ' + window + ' falhou: ' + result.stderr.strip().removeprefix('issue_session: '))


def session_script(ctx, *args):
    return run(['bash', str(SCRIPTS / 'issue_session.sh'), *args], ctx.project)


# ─── Comandos ──────────────────────────────────────────────────

def cmd_session_up(ctx):
    log_dir = ctx.args.log_dir
    if not log_dir:
        ctx.ensure_ignored('logs')
    cwd = Path(ctx.args.cwd).resolve() if ctx.args.cwd else ctx.project
    args = ['create', '--project-name', ctx.project_name, '--issue', str(ctx.issue), '--cwd', str(cwd)]
    if log_dir:
        args += ['--log-dir', str(Path(log_dir).resolve())]
    if ctx.args.dry_run:
        emit({'dry_run': True, 'comando': ['issue_session.sh', *args]})
        return OK
    result = session_script(ctx, *args)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return OK if result.returncode == 0 else ERROR


def cmd_session_down(ctx):
    if ctx.args.dry_run:
        emit({'dry_run': True, 'comando': ['issue_session.sh', 'destroy', '--session', ctx.session]})
        return OK
    result = session_script(ctx, 'destroy', '--session', ctx.session)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return OK if result.returncode == 0 else ERROR


def cmd_implement(ctx):
    send(ctx, 'codex', render('implement', base_values(ctx)))
    if not ctx.args.dry_run:
        emit({'enviado': 'codex', 'sessao': ctx.session, 'issue': ctx.issue, 'branch': ctx.branch})
    return OK


def run_gate(ctx, pr):
    timeout = 0 if ctx.args.dry_run else ctx.args.ci_timeout_seconds
    try:
        return ci_gate.gate(ctx.project, pr, timeout, ctx.args.ci_poll_seconds, dry_run=ctx.args.dry_run)
    except ci_gate.GateError as error:
        raise BotError('Portão de CI: ' + str(error)) from None


def cmd_ci_gate(ctx):
    pr = ctx.pr_number()
    code, state = run_gate(ctx, pr)
    emit(state)
    if code == ADJUST and ctx.args.send_fix:
        values = base_values(ctx)
        values.update({'pr': pr, 'pr_url': state.get('url') or 'PR #' + str(pr), 'ci_summary': ci_summary(state)})
        send(ctx, 'codex', render('corrigir-ci', values))
    return code


def finished(summary):
    emit({**summary, 'proximo_passo': 'env-up e teste humano' if summary['pronto_para_humano'] else 'respond'})
    return OK if summary['veredito'] == 'pode_mergear' else ADJUST


def cmd_review(ctx):
    ctx.ensure_ignored('handoff')
    state = round_state(ctx, ctx.args.cycle)
    cycle, last = state['cycle'], state['last']
    if ctx.args.cycle and ctx.args.cycle not in state['cycles']:
        previous = state['cycles'][-1] if state['cycles'] else 0
        if ctx.args.cycle != previous + 1:
            raise BotError('Novo ciclo deve ser o seguinte ao último existente (' + str(previous + 1) + ').')
        if previous and not handoff.validate_round(ctx.project, ctx.issue, previous)['pronto_para_humano']:
            raise BotError('O ciclo ' + str(previous) + ' ainda não terminou (pode_mergear ou decisão finalizar).')
    if last and state['claude']:
        summary = handoff.validate_round(ctx.project, ctx.issue, cycle, last, 'par' if state['codex'] else 'claude')
        if summary['veredito'] == 'pode_mergear' or not state['codex']:
            return finished(summary)
    elif last:
        raise BotError('Rodada ' + str(last) + ' tem resposta do Codex sem handoff do Claude.')
    rnd = last + 1
    if rnd > state['limit']:
        decision = state['decision']['decisao'] if state['decision'] else None
        emit({'issue': ctx.issue, 'ciclo': cycle, 'rodada': rnd, 'limite_rodadas': state['limit'], 'decisao_humana': decision,
              'proximo_passo': 'env-up (decisão finalizar)' if decision == 'finalizar'
              else 'decisão humana: iterar (com autorizado_ate) ou finalizar em ' + relative(ctx, ctx.handoff_dir / handoff.decision_name(ctx.issue, cycle))})
        return LIMIT
    pr = ctx.pr_number()
    code, ci_state = run_gate(ctx, pr)
    if code != OK:
        emit({**ci_state, 'revisao': 'recusada: o Claude só revisa com CI verde; correção de CI não conta rodada'})
        return code
    send(ctx, 'claude', render('review', review_values(ctx, pr, cycle, rnd, state['limit'], ci_state)))
    if ctx.args.dry_run:
        return OK
    target = handoff_path(ctx, cycle, rnd, 'claude')
    if not wait_for(target, ctx.args.wait_seconds, ctx.args.poll_seconds):
        emit({'aguardando': relative(ctx, target), 'rodada': rnd})
        return PENDING
    try:
        return finished(handoff.validate_round(ctx.project, ctx.issue, cycle, rnd, 'claude'))
    except handoff.HandoffError as error:
        raise BotError('Handoff do Claude inválido; a rodada não avança: ' + str(error)) from None


def cmd_respond(ctx):
    ctx.ensure_ignored('handoff')
    state = round_state(ctx, ctx.args.cycle)
    cycle, last = state['cycle'], state['last']
    if not (last and state['claude']):
        raise BotError('Não há handoff do Claude para responder; rode review.')
    summary = handoff.validate_round(ctx.project, ctx.issue, cycle, last, 'par' if state['codex'] else 'claude')
    if summary['veredito'] == 'pode_mergear':
        raise BotError('A rodada ' + str(last) + ' terminou com pode_mergear; não há ajustes a responder.')
    if state['codex']:
        emit({**summary, 'proximo_passo': 'ci-gate e review'})
        return OK
    if last >= state['limit']:
        emit({**summary, 'proximo_passo': 'decisão humana: iterar (com autorizado_ate) ou finalizar em '
              + relative(ctx, ctx.handoff_dir / handoff.decision_name(ctx.issue, cycle))})
        return LIMIT
    pr = summary['pr']
    values = review_values(ctx, pr, cycle, last, state['limit'])
    values['handoff_path'] = values['codex_handoff_path']
    send(ctx, 'codex', render('respond', values))
    if ctx.args.dry_run:
        return OK
    target = handoff_path(ctx, cycle, last, 'codex')
    if not wait_for(target, ctx.args.wait_seconds, ctx.args.poll_seconds):
        emit({'aguardando': relative(ctx, target), 'rodada': last})
        return PENDING
    try:
        summary = handoff.validate_round(ctx.project, ctx.issue, cycle, last, 'par')
    except handoff.HandoffError as error:
        raise BotError('Handoff do Codex inválido: ' + str(error)) from None
    emit({**summary, 'proximo_passo': 'ci-gate e review'})
    return OK


# ─── Ambiente e dados ──────────────────────────────────────────

def committed_config(ctx):
    """data.restore vira comando executado fora do sandbox dos agentes: só vale a versão commitada."""
    committed = run(['git', 'show', 'HEAD:.bezalel/project.json'], ctx.project)
    if committed.returncode != 0:
        raise BotError('.bezalel/project.json precisa estar commitado para o env-up.', DECISION)
    path = ctx.project / '.bezalel/project.json'
    if not path.is_file() or path.read_text(encoding='utf-8') != committed.stdout:
        raise BotError('.bezalel/project.json tem alterações não commitadas; o env-up só usa a versão '
                       'commitada (revise e commite a mudança antes).')
    try:
        return json.loads(committed.stdout)
    except ValueError:
        raise BotError('.bezalel/project.json commitado é ilegível.') from None


def data_settings(ctx):
    config = committed_config(ctx)
    if not config or config.get('schema_version') != 3 or not isinstance(config.get('data'), dict):
        raise BotError('.bezalel/project.json precisa do schema 3 com data; rode project.py migrate-config.', DECISION)
    data = config['data']
    mode = data.get('mode')
    if mode not in {'snapshot', 'empty', 'ask'}:
        raise BotError('data.mode inválido em .bezalel/project.json.')
    if mode == 'snapshot':
        restore, workdir = data.get('restore'), data.get('workdir', '.')
        if not (isinstance(restore, list) and restore and all(isinstance(a, str) and a.strip() for a in restore)):
            raise BotError('data.restore deve ser lista de argumentos.')
        if not isinstance(workdir, str) or Path(workdir).is_absolute() or '..' in Path(workdir).parts:
            raise BotError('data.workdir deve ser relativo à worktree, sem "..".')
    return data


def env_script(ctx, *args, allow_infra=False):
    skill = Path(ctx.args.env_skill_dir).resolve() if ctx.args.env_skill_dir else SKILL.parent / 'env'
    env = {k: v for k, v in os.environ.items() if k != 'ENV_ALLOW_SHARED_INFRA'}
    if allow_infra:
        env['ENV_ALLOW_SHARED_INFRA'] = '1'  # somente nesta invocação autorizada
    return run(['bash', str(skill / 'scripts/ctl.sh'), *args], ctx.project, env=env, timeout=1800)


def env_status(ctx):
    result = env_script(ctx, 'status', ctx.env_name, '--json')
    if result.returncode in (OK, DECISION):
        try:
            return result.returncode, json.loads(result.stdout)
        except ValueError:
            raise BotError('Status do ambiente ilegível.') from None
    return None, None


def cmd_env_up(ctx):
    ctx.ensure_ignored('handoff')
    data = data_settings(ctx)
    if not ctx.args.allow_before_review:
        state = round_state(ctx)
        if not state['last'] or not handoff.validate_round(ctx.project, ctx.issue, state['cycle'])['pronto_para_humano']:
            raise BotError('Ambiente de teste humano exige pode_mergear ou decisão finalizar no ciclo atual '
                           '(use --allow-before-review só por pedido humano explícito).')
    code, status = env_status(ctx)
    if code != OK:
        if not ctx.args.allow_shared_infra:
            emit({'ambiente': ctx.env_name, 'pronto': False, 'decisao_pendente': 'infra compartilhada',
                  'detalhe': 'Subir o ambiente pode instalar dnsmasq/mkcert, usar sudo e reiniciar o Traefik global. '
                             'Com autorização humana, repita com --allow-shared-infra (ENV_ALLOW_SHARED_INFRA=1 só nesta execução).'})
            return DECISION
        target = ['ensure', ctx.env_name, '--issue', str(ctx.issue)]
        if ctx.args.branch:
            target += ['--branch', ctx.args.branch]
        result = env_script(ctx, *target, *(ctx.args.services or []), allow_infra=True)
        sys.stderr.write(result.stdout[-4000:] + result.stderr[-4000:])
        if result.returncode != 0:
            raise BotError('env ensure falhou (código ' + str(result.returncode) + '); nada foi declarado pronto.')
        code, status = env_status(ctx)
        if code != OK:
            emit({'ambiente': status, 'pronto': False})
            return DECISION
    mode = 'empty' if ctx.args.data_mode == 'empty' else data['mode']
    result = {'modo': mode, 'restaurado': False}
    if mode == 'ask':
        emit({'ambiente': status, 'dados': result, 'decisao_pendente': 'dados',
              'detalhe': 'data.mode ask: defina snapshot/empty no project.json ou repita com --data-mode empty. Produção nunca é lida.'})
        return DECISION
    if mode == 'snapshot':
        result = restore_snapshot(ctx, data, status)
        if result.get('decisao_pendente'):
            emit({'ambiente': status, 'dados': result, 'decisao_pendente': 'restore',
                  'detalhe': 'O humano confere o comando e aprova em terminal interativo: '
                             'issue_bot.py approve-restore --project <raiz> --issue <n>; depois repita o env-up.'})
            return DECISION
        if result.get('codigo_saida'):
            emit({'ambiente': status, 'dados': result})
            return ERROR
    emit({'ambiente': status, 'dados': result, 'proximo_passo': 'teste humano; merge só com ordem explícita'})
    return OK


def restore_digest(data):
    canonical = json.dumps({'restore': data['restore'], 'workdir': data.get('workdir', '.')},
                           ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def approvals_path(ctx):
    base = os.environ.get('ISSUE_BOT_STATE_DIR') or os.path.join(
        os.environ.get('XDG_STATE_HOME') or os.path.expanduser('~/.local/state'), 'bezalel-issue-bot')
    path = Path(base).resolve() / 'restore-approvals.json'
    # Fora da área de escrita do Codex (raiz do projeto); dentro dela a aprovação seria forjável.
    if ctx.project == path.parent or ctx.project in path.parents:
        raise BotError('O registro de aprovações não pode ficar dentro do projeto.')
    return path


def approvals(ctx):
    path = approvals_path(ctx)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise BotError('Registro de aprovações de restore ilegível: ' + str(path)) from None
    return data if isinstance(data, dict) else {}


def cmd_approve_restore(ctx):
    """Aprovação humana do argv exato de restore; exige terminal interativo e confirmação digitada."""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        raise BotError('approve-restore exige terminal interativo do humano; agentes não aprovam restore.')
    data = data_settings(ctx)
    if data['mode'] != 'snapshot':
        raise BotError('data.mode não é snapshot; não há restore a aprovar.')
    print('Comando de restore (project.json commitado):')
    print('  argv:    ' + json.dumps(data['restore'], ensure_ascii=False))
    print('  workdir: ' + data.get('workdir', '.') + ' (dentro da worktree do ambiente)')
    print('Ele roda na sua máquina, fora do sandbox dos agentes, e deve recusar destino de produção.')
    answer = input('Digite o nome do projeto (' + ctx.project_name + ') para aprovar: ').strip()
    if answer != ctx.project_name:
        print('Aprovação não registrada.')
        return DECISION
    path = approvals_path(ctx)
    registry = approvals(ctx)
    approved = registry.setdefault(str(ctx.project), [])
    digest = restore_digest(data)
    if digest not in approved:
        approved.append(digest)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)
    print('Restore aprovado para este comando exato; qualquer mudança exige nova aprovação.')
    return OK


def restore_snapshot(ctx, data, status):
    marker = ctx.handoff_dir / (str(ctx.issue) + '-dados.json')
    if marker.is_file() and not ctx.args.restore_again:
        try:
            previous = json.loads(marker.read_text())
        except ValueError:
            previous = {}
        if previous.get('ambiente') == ctx.env_name:
            return {'modo': 'snapshot', 'restaurado': False, 'motivo': 'já restaurado neste ambiente; use --restore-again para repetir',
                    'anterior': previous}
    worktree = Path(status['worktree']).resolve()
    workdir = (worktree / data.get('workdir', '.')).resolve()
    if workdir != worktree and worktree not in workdir.parents or not workdir.is_dir():
        raise BotError('data.workdir fora da worktree do ambiente ou inexistente.')
    # Os agentes podem commitar no projeto: o restore só roda se este argv exato foi aprovado
    # pelo humano com approve-restore (terminal interativo), registrado fora do projeto.
    if restore_digest(data) not in approvals(ctx).get(str(ctx.project), []):
        return {'modo': 'snapshot', 'restaurado': False, 'decisao_pendente': True, 'restore': data['restore'],
                'workdir': data.get('workdir', '.')}
    # Comando do projeto, como lista e sem shell; deve recusar destino de produção por si.
    print('issue-bot: restore (project.json commitado): ' + json.dumps(data['restore'], ensure_ascii=False)
          + ' em ' + str(workdir), file=sys.stderr)
    process = subprocess.run(data['restore'], cwd=workdir, stdout=sys.stderr, stderr=sys.stderr)
    entry = {'modo': 'snapshot', 'dataset': data.get('dataset'), 'ambiente': ctx.env_name,
             'workdir': str(workdir), 'codigo_saida': process.returncode,
             'registrado_em': datetime.now().astimezone().isoformat(timespec='seconds')}
    if process.returncode == 0:
        ctx.handoff_dir.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
        entry['restaurado'] = True
    else:
        entry['restaurado'] = False
    return entry


# ─── Status e prepare-prompt ───────────────────────────────────

def cmd_status(ctx):
    state = round_state(ctx, ctx.args.cycle)
    summary, error = None, None
    if state['last']:
        try:
            summary = handoff.validate_round(ctx.project, ctx.issue, state['cycle'], ctx.args.round or state['last'])
        except handoff.HandoffError as exc:
            error = str(exc)
    pr = ctx.args.pr or (summary or {}).get('pr')
    ci = None
    if not ctx.args.offline:
        try:
            pr = pr or ctx.pr_number(required=False)
            ci = ci_gate.snapshot(ctx.project, pr) if pr else None
        except (BotError, ci_gate.GateError) as exc:
            ci = {'status': 'desconhecido', 'erro': str(exc)}
    session = None
    if not ctx.args.offline:
        result = session_script(ctx, 'status', '--session', ctx.session)
        session = json.loads(result.stdout) if result.returncode == 0 else {'erro': result.stderr.strip()}
    environment = None
    if not ctx.args.offline:
        try:
            environment = env_status(ctx)[1]
        except BotError as exc:
            environment = {'erro': str(exc)}
    emit({
        'issue': ctx.issue, 'pr': pr, 'ciclo': state['cycle'], 'rodada': summary['rodada'] if summary else state['last'],
        'limite_rodadas': state['limit'], 'veredito': (summary or {}).get('veredito'),
        'bloqueantes_abertos': (summary or {}).get('bloqueantes_abertos'),
        'pronto_para_humano': bool(summary and summary['pronto_para_humano']),
        'decisao_humana': state['decision']['decisao'] if state['decision'] else None,
        'handoff': (summary or {}).get('arquivos'), 'handoff_erro': error, 'ci': ci,
        'sessao': session, 'ambiente': environment, 'merge_autorizado': False,
    })
    return ERROR if error else OK


def cmd_prepare_prompt(ctx):
    kind = ctx.args.kind
    if kind == 'implement':
        text = render(kind, base_values(ctx))
    elif kind in {'review', 'respond'}:
        state = round_state(ctx, ctx.args.cycle)
        rnd = ctx.args.round or (state['last'] + 1 if kind == 'review' else state['last'])
        if rnd < 1:
            raise BotError('Sem rodada para responder; informe --round.')
        pr = ctx.pr_number()
        values = review_values(ctx, pr, state['cycle'], rnd, state['limit'])
        if kind == 'respond':
            values['handoff_path'] = values['codex_handoff_path']
        text = render(kind, values)
    else:
        values = base_values(ctx)
        pr = ctx.pr_number(required=kind == 'corrigir-ci')
        ci_state = None
        if kind == 'corrigir-ci':
            try:
                ci_state = ci_gate.snapshot(ctx.project, pr)
            except ci_gate.GateError as error:
                raise BotError('Portão de CI: ' + str(error)) from None
        values.update({'pr': pr or '(ainda sem PR)', 'pr_url': (ci_state or {}).get('url') or 'PR #' + str(pr),
                       'ci_summary': ci_summary(ci_state),
                       'env_up_command': 'python3 ' + str(SCRIPTS / 'issue_bot.py') + ' env-up --project ' + str(ctx.project)
                       + ' --issue ' + str(ctx.issue)})
        text = render(kind, values)
    if ctx.args.output:
        Path(ctx.args.output).write_text(text, encoding='utf-8')
    else:
        print(text)
    return OK


COMMANDS = {'session-up': cmd_session_up, 'session-down': cmd_session_down, 'implement': cmd_implement,
            'ci-gate': cmd_ci_gate, 'review': cmd_review, 'respond': cmd_respond, 'env-up': cmd_env_up,
            'status': cmd_status, 'prepare-prompt': cmd_prepare_prompt, 'approve-restore': cmd_approve_restore}


def parser():
    main = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = main.add_subparsers(dest='command', required=True, metavar='comando')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--project', required=True, help='raiz do repositório do projeto')
    common.add_argument('--issue', required=True, type=int)
    common.add_argument('--pr', type=int, help='PR já conhecida (senão, resolvida pela issue)')
    common.add_argument('--round', type=int, help='rodada específica (status/prepare-prompt)')
    common.add_argument('--cycle', type=int, help='ciclo de revisão (novo ciclo após ajustes de usabilidade)')
    common.add_argument('--branch', help='branch da PR (padrão issue-<n>)')
    common.add_argument('--env-name', help='nome do ambiente env (padrão issue-<n>)')
    common.add_argument('--project-name', help='nome curto do projeto (padrão: campo project do project.json)')
    common.add_argument('--dry-run', action='store_true', help='não envia teclas ao tmux; imprime o prompt')
    common.add_argument('--log-dir', help='pasta dos logs tmux (padrão .bezalel/logs)')
    common.add_argument('--cwd', help='pasta das janelas (raiz do projeto ou worktree da issue)')
    common.add_argument('--ci-timeout-seconds', type=int, default=1800)
    common.add_argument('--ci-poll-seconds', type=int, default=30)
    common.add_argument('--wait-seconds', type=int, default=3600, help='espera pelo handoff do agente')
    common.add_argument('--poll-seconds', type=int, default=15)
    helps = {'session-up': 'cria ou reutiliza a sessão tmux da issue', 'session-down': 'encerra a sessão; não destrói o ambiente',
             'implement': 'envia o prompt de implementação ao Codex', 'ci-gate': 'portão de CI da PR da issue',
             'review': 'com CI verde, envia a revisão ao Claude e valida o handoff', 'respond': 'envia o handoff ao Codex e valida a resposta',
             'env-up': 'sobe o ambiente da issue e aplica data do project.json', 'status': 'estado da issue em JSON',
             'prepare-prompt': 'gera um prompt sem enviar',
             'approve-restore': 'humano aprova, em terminal interativo, o comando exato de restore'}
    commands = {}
    for name in COMMANDS:
        commands[name] = sub.add_parser(name, parents=[common], help=helps[name])
    commands['prepare-prompt'].add_argument('kind', choices=sorted(PROMPTS))
    commands['prepare-prompt'].add_argument('--output')
    commands['ci-gate'].add_argument('--send-fix', action='store_true', help='com CI vermelha, envia corrigir-ci ao Codex')
    commands['status'].add_argument('--offline', action='store_true', help='sem consultar gh, tmux ou env')
    env = commands['env-up']
    env.add_argument('--allow-shared-infra', action='store_true', help='autorização humana para esta execução')
    env.add_argument('--data-mode', choices=['empty'], help='só nesta execução, ignora data.mode ask')
    env.add_argument('--restore-again', action='store_true')
    env.add_argument('--allow-before-review', action='store_true')
    env.add_argument('--env-skill-dir', help=argparse.SUPPRESS)
    env.add_argument('services', nargs='*', help='serviços do env (padrão do manifesto)')
    return main


# Opções específicas de um comando; os demais recebem estes valores.
DEFAULTS = {'kind': None, 'output': None, 'send_fix': False, 'offline': False, 'allow_shared_infra': False,
            'data_mode': None, 'restore_again': False, 'allow_before_review': False, 'env_skill_dir': None, 'services': None}


def main(argv=None):
    args = parser().parse_args(argv)
    for key, value in DEFAULTS.items():
        if not hasattr(args, key):
            setattr(args, key, value)
    try:
        return COMMANDS[args.command](Context(args))
    except BotError as error:
        print('issue-bot: ' + str(error), file=sys.stderr)
        return error.code
    except handoff.HandoffError as error:
        print('issue-bot: handoff inválido: ' + str(error), file=sys.stderr)
        return ERROR


if __name__ == '__main__':
    sys.exit(main())
