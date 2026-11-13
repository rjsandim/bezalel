#!/usr/bin/env python3
"""Valida os handoffs JSON do modo issue-bot, sem acessar rede ou GitHub.

Arquivos por rodada, em <projeto>/.bezalel/handoff/:
  <issue>-r<rodada>-claude.json / <issue>-r<rodada>-codex.json            (ciclo 1)
  <issue>-c<ciclo>-r<rodada>-claude.json / ...-codex.json                  (ciclo >= 1)
Decisão humana após o limite de rodadas: <issue>-decisao.json (ciclo 1) ou
<issue>-c<ciclo>-decisao.json. JSON não prova identidade nem autorização.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

MAX_ROUNDS = 2
SCHEMA_VERSION = 1
HANDOFF_DIR = Path('.bezalel/handoff')
NAME = re.compile(r'^(?P<issue>[1-9][0-9]*)(?:-c(?P<cycle>[1-9][0-9]*))?-r(?P<round>[1-9][0-9]*)-(?P<role>claude|codex)\.json$')
DECISION = re.compile(r'^(?P<issue>[1-9][0-9]*)(?:-c(?P<cycle>[1-9][0-9]*))?-decisao\.json$')
SHA = re.compile(r'^[0-9a-f]{7,40}$')
CLAUDE_FIELDS = {'schema_version', 'papel', 'issue', 'pr', 'rodada', 'ciclo', 'candidato', 'ci', 'veredito',
                 'criterios', 'ajustes', 'fora_de_escopo', 'skills_usadas', 'gerado_em'}
CODEX_FIELDS = {'schema_version', 'papel', 'issue', 'pr', 'rodada', 'ciclo', 'candidato', 'ajustes', 'gerado_em'}
DECISION_FIELDS = {'schema_version', 'issue', 'pr', 'ciclo', 'apos_rodada', 'decisao', 'autorizado_ate',
                   'ator', 'fonte', 'registrado_em', 'motivo'}


class HandoffError(ValueError):
    """Diagnóstico fixo, sem reproduzir o conteúdo do handoff."""


def require(condition, message):
    if not condition:
        raise HandoffError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def positive(value):
    return type(value) is int and value >= 1


def timestamp(value, label):
    try:
        when = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError):
        raise HandoffError(label + ': data inválida; use ISO 8601 com fuso.') from None
    require(when.tzinfo is not None, label + ': data precisa incluir fuso.')
    return when


def https_url(value):
    try:
        parsed = urlparse(value)
    except (TypeError, ValueError, AttributeError):
        return False
    return parsed.scheme == 'https' and bool(parsed.hostname) and not parsed.username and not parsed.password


def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError):
        raise HandoffError(path.name + ': JSON ilegível ou malformado; conteúdo omitido.') from None


def file_name(issue, cycle, rnd, role):
    prefix = str(issue) + ('-c' + str(cycle) if cycle and cycle > 1 else '')
    return prefix + '-r' + str(rnd) + '-' + role + '.json'


def decision_name(issue, cycle):
    return str(issue) + ('-c' + str(cycle) if cycle and cycle > 1 else '') + '-decisao.json'


def scan(directory, issue):
    """Mapeia (ciclo, rodada, papel) -> arquivo, recusando colisão entre os dois padrões."""
    found = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.iterdir()):
        match = NAME.match(path.name)
        if not match or int(match['issue']) != issue:
            continue
        require(path.is_file() and not path.is_symlink(), path.name + ': handoff precisa ser arquivo comum.')
        key = (int(match['cycle'] or 1), int(match['round']), match['role'])
        require(key not in found, 'Colisão de handoff: ' + found.get(key, Path('?')).name + ' e ' + path.name + ' descrevem a mesma rodada.')
        found[key] = path
    return found


def cycles(found):
    return sorted({cycle for cycle, _, _ in found})


def rounds(found, cycle):
    return sorted({rnd for c, rnd, _ in found if c == cycle})


def find_decision(directory, issue, cycle):
    names = [decision_name(issue, cycle)]
    if cycle == 1:
        names.append(str(issue) + '-c1-decisao.json')
    present = [directory / name for name in names if (directory / name).is_file()]
    require(len(present) <= 1, 'Colisão de decisão humana para o mesmo ciclo.')
    return present[0] if present else None


def validate_decision(path, issue, cycle):
    """Estrutura da decisão humana; não comprova identidade, só o registro declarado."""
    doc = read(path)
    require(isinstance(doc, dict) and set(doc) <= DECISION_FIELDS, path.name + ': campos desconhecidos na decisão.')
    require(doc.get('schema_version') == SCHEMA_VERSION, path.name + ': schema_version deve ser 1.')
    require(doc.get('issue') == issue and positive(doc.get('pr')), path.name + ': issue/pr divergentes ou inválidos.')
    require(doc.get('ciclo', 1) == cycle, path.name + ': ciclo diverge do nome do arquivo.')
    require(positive(doc.get('apos_rodada')) and doc['apos_rodada'] >= MAX_ROUNDS,
            path.name + ': a decisão só cabe após o limite de ' + str(MAX_ROUNDS) + ' rodadas.')
    require(doc.get('decisao') in {'iterar', 'finalizar'}, path.name + ': decisao deve ser iterar ou finalizar.')
    if doc['decisao'] == 'iterar':
        require(positive(doc.get('autorizado_ate')) and doc['autorizado_ate'] > doc['apos_rodada'],
                path.name + ': iterar exige autorizado_ate maior que apos_rodada.')
    else:
        require(doc.get('autorizado_ate') is None, path.name + ': finalizar não autoriza novas rodadas.')
    require(all(text(doc.get(k)) for k in ('ator', 'fonte', 'motivo')), path.name + ': informe ator, fonte e motivo reais.')
    timestamp(doc.get('registrado_em'), path.name)
    return doc


def allowed_rounds(directory, issue, cycle):
    """Limite efetivo do ciclo: 2, ou o autorizado por decisão humana de iterar."""
    path = find_decision(directory, issue, cycle)
    if path is None:
        return MAX_ROUNDS, None
    doc = validate_decision(path, issue, cycle)
    return (doc['autorizado_ate'] if doc['decisao'] == 'iterar' else MAX_ROUNDS), doc


def common(doc, path, role, issue, cycle, rnd, fields):
    require(isinstance(doc, dict), path.name + ': o handoff deve ser um objeto JSON.')
    unknown = set(doc) - fields
    require(not unknown, path.name + ': campos desconhecidos na raiz: ' + ', '.join(sorted(unknown)) + '.')
    require(doc.get('schema_version') == SCHEMA_VERSION, path.name + ': schema_version deve ser 1.')
    require(doc.get('papel') == role, path.name + ': papel diverge do nome do arquivo.')
    require(positive(doc.get('issue')) and positive(doc.get('pr')) and positive(doc.get('rodada')),
            path.name + ': issue, pr e rodada devem ser inteiros >= 1.')
    require(doc['issue'] == issue and doc['rodada'] == rnd, path.name + ': issue/rodada divergem do nome do arquivo.')
    require('ciclo' not in doc or positive(doc['ciclo']), path.name + ': ciclo deve ser inteiro >= 1.')
    require(doc.get('ciclo', 1) == cycle, path.name + ': ciclo diverge do nome do arquivo.')
    candidate = doc.get('candidato')
    require(isinstance(candidate, dict) and set(candidate) == {'base', 'head', 'sha'}
            and all(text(candidate[k]) for k in candidate), path.name + ': candidato exige base, head e sha.')
    require(SHA.match(candidate['sha']) is not None, path.name + ': sha do candidato inválido.')
    timestamp(doc.get('gerado_em'), path.name)


def validate_claude(path, issue, cycle, rnd):
    doc = read(path)
    common(doc, path, 'claude', issue, cycle, rnd, CLAUDE_FIELDS)
    ci = doc.get('ci')
    require(isinstance(ci, dict) and set(ci) <= {'status', 'evidence', 'url'} and text(ci.get('evidence')),
            path.name + ': ci exige status e evidência.')
    require(ci.get('status') == 'passed', path.name + ': revisão só é válida com CI verde (ci.status passed).')
    require('url' not in ci or ci['url'] is None or https_url(ci['url']), path.name + ': URL de CI deve ser HTTPS, sem credencial.')
    require(doc.get('veredito') in {'pode_mergear', 'ajustes'}, path.name + ': veredito deve ser pode_mergear ou ajustes.')
    criteria = doc.get('criterios')
    require(isinstance(criteria, list) and criteria, path.name + ': informe a aderência de cada critério de aceite.')
    ids = []
    for item in criteria:
        require(isinstance(item, dict) and set(item) == {'id', 'criterio', 'status', 'evidencia'}
                and all(text(item[k]) for k in ('id', 'criterio', 'evidencia')),
                path.name + ': critério exige id, criterio, status e evidencia.')
        require(item['status'] in {'atendido', 'parcial', 'nao_atendido'}, path.name + ': status de critério inválido.')
        ids.append(item['id'])
    require(len(ids) == len(set(ids)), path.name + ': IDs de critérios duplicados.')
    adjustments = doc.get('ajustes')
    require(isinstance(adjustments, list), path.name + ': ajustes deve ser lista (pode ser vazia).')
    adjustment_ids = []
    for item in adjustments:
        require(isinstance(item, dict) and set(item) <= {'id', 'gravidade', 'arquivo', 'problema', 'porque', 'sugestao'}
                and all(text(item.get(k)) for k in ('id', 'problema', 'porque', 'sugestao')),
                path.name + ': ajuste exige id, gravidade, problema, porque e sugestao.')
        require(item.get('gravidade') in {'bloqueante', 'sugestao'}, path.name + ': gravidade deve ser bloqueante ou sugestao.')
        require(item.get('arquivo') is None or text(item['arquivo']), path.name + ': arquivo do ajuste vazio.')
        adjustment_ids.append(item['id'])
    require(len(adjustment_ids) == len(set(adjustment_ids)), path.name + ': IDs de ajustes duplicados.')
    out_of_scope = doc.get('fora_de_escopo', [])
    require(isinstance(out_of_scope, list) and all(text(i) for i in out_of_scope), path.name + ': fora_de_escopo é lista de textos.')
    skills = doc.get('skills_usadas')
    require(isinstance(skills, list) and all(text(s) for s in skills) and {'pr-audit', 'security-audit'} <= set(skills),
            path.name + ': registre as skills usadas, incluindo pr-audit e security-audit.')
    blocking = [i for i in adjustments if i['gravidade'] == 'bloqueante']
    pending = [c for c in criteria if c['status'] != 'atendido']
    if doc['veredito'] == 'pode_mergear':
        require(not blocking and not pending,
                path.name + ': pode_mergear exige todos os critérios atendidos e nenhum ajuste bloqueante.')
    else:
        require(blocking or pending, path.name + ': ajustes exige ajuste bloqueante ou critério não atendido.')
    return doc


def validate_codex(path, claude, issue, cycle, rnd):
    doc = read(path)
    common(doc, path, 'codex', issue, cycle, rnd, CODEX_FIELDS)
    require(doc['pr'] == claude['pr'], path.name + ': PR diverge do handoff do Claude da mesma rodada.')
    require(claude['veredito'] == 'ajustes', path.name + ': rodada encerrada com pode_mergear não recebe resposta.')
    asked = {item['id']: item for item in claude['ajustes']}
    answers = doc.get('ajustes')
    require(isinstance(answers, list), path.name + ': ajustes deve ser lista.')
    seen = []
    for item in answers:
        require(isinstance(item, dict) and set(item) == {'id', 'status', 'como', 'commit'} and text(item.get('id'))
                and text(item.get('como')), path.name + ': resposta exige id, status, como e commit.')
        require(item['id'] in asked, path.name + ': ajuste ' + item['id'] + ' não existe no handoff do Claude.')
        require(item['status'] in {'corrigido', 'nao_corrigido'}, path.name + ': status deve ser corrigido ou nao_corrigido.')
        if item['status'] == 'corrigido':
            require(isinstance(item['commit'], str) and SHA.match(item['commit']) is not None,
                    path.name + ': ajuste corrigido exige o SHA do commit.')
        else:
            require(item['commit'] is None or (isinstance(item['commit'], str) and SHA.match(item['commit'])),
                    path.name + ': commit inválido.')
        seen.append(item['id'])
    require(len(seen) == len(set(seen)), path.name + ': resposta duplicada para o mesmo ajuste.')
    missing = [i for i, item in asked.items() if item['gravidade'] == 'bloqueante' and i not in seen]
    require(not missing, path.name + ': responda todos os ajustes bloqueantes (faltam ' + ', '.join(missing) + ').')
    return doc


def validate_round(project, issue, cycle=None, rnd=None, role=None):
    """Valida uma rodada e devolve o resumo. Lança HandoffError com diagnóstico fixo."""
    require(positive(issue), 'Informe a issue como inteiro >= 1.')
    directory = Path(project) / HANDOFF_DIR
    require(not directory.is_symlink(), '.bezalel/handoff não pode ser link.')
    found = scan(directory, issue)
    require(found, 'Nenhum handoff da issue ' + str(issue) + ' em .bezalel/handoff/.')
    cycle = cycle or cycles(found)[-1]
    present = rounds(found, cycle)
    require(present, 'Nenhum handoff no ciclo ' + str(cycle) + '.')
    rnd = rnd or present[-1]
    limit, decision = allowed_rounds(directory, issue, cycle)
    require(rnd <= MAX_ROUNDS or (decision and decision['decisao'] == 'iterar' and rnd <= limit),
            'Rodada ' + str(rnd) + ' exige decisão humana iterar com autorizado_ate >= ' + str(rnd) + '.')
    claude_path = found.get((cycle, rnd, 'claude'))
    codex_path = found.get((cycle, rnd, 'codex'))
    role = role or ('par' if claude_path and codex_path else 'codex' if codex_path else 'claude')
    require(role in {'claude', 'codex', 'par'}, 'Papel inválido.')
    require(claude_path is not None, 'Handoff do Claude ausente na rodada ' + str(rnd) + '.')
    if rnd > 1:
        require((cycle, rnd - 1, 'codex') in found,
                'Rodada ' + str(rnd) + ' exige a resposta do Codex da rodada ' + str(rnd - 1) + '.')
    claude = validate_claude(claude_path, issue, cycle, rnd)
    codex = None
    if role in {'codex', 'par'}:
        require(codex_path is not None, 'Handoff do Codex ausente na rodada ' + str(rnd) + '.')
        codex = validate_codex(codex_path, claude, issue, cycle, rnd)
    blocking = [i['id'] for i in claude['ajustes'] if i['gravidade'] == 'bloqueante']
    if codex:
        fixed = {i['id'] for i in codex['ajustes'] if i['status'] == 'corrigido'}
        blocking = [i for i in blocking if i not in fixed]
    finalized = bool(decision and decision['decisao'] == 'finalizar')
    return {
        'issue': issue, 'pr': claude['pr'], 'ciclo': cycle, 'rodada': rnd,
        'veredito': claude['veredito'], 'bloqueantes_abertos': len(blocking),
        'criterios_pendentes': sum(1 for c in claude['criterios'] if c['status'] != 'atendido'),
        'resposta_codex': codex is not None, 'limite_rodadas': limit,
        'decisao_humana': decision['decisao'] if decision else None,
        'pronto_para_humano': claude['veredito'] == 'pode_mergear' or finalized,
        'arquivos': {'claude': str(HANDOFF_DIR / claude_path.name),
                     'codex': str(HANDOFF_DIR / codex_path.name) if codex_path else None},
        'merge_autorizado': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--issue', required=True, type=int)
    parser.add_argument('--round', type=int)
    parser.add_argument('--cycle', type=int)
    parser.add_argument('--role', choices=['claude', 'codex', 'par'])
    args = parser.parse_args(argv)
    try:
        summary = validate_round(args.project.resolve(), args.issue, args.cycle, args.round, args.role)
    except HandoffError as error:
        print('Handoff inválido: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
