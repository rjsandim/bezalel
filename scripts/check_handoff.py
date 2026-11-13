#!/usr/bin/env python3
"""Valida handoffs locais; não acessa GitHub nem autentica decisões humanas."""
import argparse
import json
from pathlib import Path
import re
import sys

from check_delivery import ContractError, ContractParser, https_reference, read_json, require, text, timestamp

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / ('agents' if (ROOT / 'agents/catalog.json').is_file() else 'contracts')


def schema_check(value, schema):
    """Subconjunto usado pelo schema publicado; sem dependência ou execução externa."""
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'null': type(None)}
    kind = schema.get('type')
    if kind:
        require(type(value) in [types[t] for t in (kind if isinstance(kind, list) else [kind])], 'Tipo inválido no handoff.')
    if 'const' in schema:
        require(value == schema['const'], 'Constante inválida no handoff.')
    if 'enum' in schema:
        require(value in schema['enum'], 'Enumeração inválida no handoff.')
    if isinstance(value, dict):
        require(set(schema.get('required', [])) <= set(value), 'Campos obrigatórios ausentes no handoff.')
        props = schema.get('properties', {})
        require(schema.get('additionalProperties', True) or set(value) <= set(props), 'Campo desconhecido no handoff.')
        for key, item in value.items():
            if key in props:
                schema_check(item, props[key])
    if isinstance(value, list):
        require(len(value) >= schema.get('minItems', 0), 'Lista obrigatória vazia no handoff.')
        for item in value:
            schema_check(item, schema.get('items', {}))
    if isinstance(value, str):
        require(len(value.strip()) >= schema.get('minLength', 0), 'Texto obrigatório vazio no handoff.')
        if schema.get('format') == 'date-time':
            timestamp(value)
        if schema.get('format') == 'uri':
            require(https_reference(value), 'URL deve usar HTTPS sem credenciais.')
    if type(value) is int:
        require(value >= schema.get('minimum', value), 'Inteiro inválido no handoff.')


def handoff_dir(project):
    directory = Path(project) / '.bezalel' / 'handoff'
    for path in (directory.parent, directory):
        require(not path.is_symlink(), 'Diretório de handoff não pode ser symlink.')
    return directory


def filename(issue, round_number, role, cycle=1):
    return f'{issue}' + (f'-c{cycle}' if cycle > 1 else '') + f'-r{round_number}-{role}.json'


def path_for(project, issue, round_number, role, cycle=1):
    directory = handoff_dir(project)
    simple = directory / filename(issue, round_number, role, cycle)
    if cycle == 1:
        explicit = directory / f'{issue}-c1-r{round_number}-{role}.json'
        require(not (simple.exists() and explicit.exists()), 'Colisão de nomes no ciclo 1.')
        if explicit.exists():
            return explicit
    return simple


def rounds(project, issue, cycle=1):
    directory = handoff_dir(project)
    found = set()
    pattern = re.compile(rf'{issue}-(?:c{cycle}-)?r([1-9][0-9]*)-(claude|codex)\.json' if cycle == 1 else rf'{issue}-c{cycle}-r([1-9][0-9]*)-(claude|codex)\.json')
    for path in directory.glob('*.json'):
        match = pattern.fullmatch(path.name)
        if match:
            found.add(int(match[1]))
    return sorted(found)


def decision(project, issue, pr, cycle=1):
    path = handoff_dir(project) / (f'{issue}' + (f'-c{cycle}' if cycle > 1 else '') + '-decisao.json')
    if not path.exists():
        return None
    require(not path.is_symlink(), 'Decisão não pode ser symlink.')
    data = read_json(path)
    fields = {'schema_version','issue','pr','apos_rodada','decisao','autorizado_ate','ator','fonte','registrado_em','motivo','ciclo'}
    require(isinstance(data, dict) and set(data) <= fields and fields - {'ciclo'} <= set(data), 'Registro de decisão inválido.')
    require(all(type(data.get(k,1)) is int for k in ('schema_version','issue','pr','ciclo')) and data['schema_version'] == 1 and data['issue'] == issue and data['pr'] == pr and data.get('ciclo',1) == cycle, 'Decisão pertence a outro objeto.')
    require(type(data['apos_rodada']) is int and data['apos_rodada'] >= 2 and type(data['autorizado_ate']) is int, 'Limite da decisão inválido.')
    require(data['decisao'] in {'iterar','finalizar'} and all(text(data[k]) for k in ('ator','fonte','motivo')), 'Identifique decisão humana real e sua fonte.')
    timestamp(data['registrado_em'])
    if data['decisao'] == 'iterar':
        require(data['autorizado_ate'] > data['apos_rodada'], 'Iteração exige um limite maior.')
    return data


def validate_file(path):
    require(not path.is_symlink(), 'Handoff não pode ser symlink.')
    data = read_json(path)
    require(isinstance(data, dict) and data.get('papel') in {'claude','codex'}, 'Papel do handoff inválido.')
    schema_check(data, read_json(CONTRACTS / 'contracts/handoff.schema.json')['$defs'][data['papel']])
    cycle = data.get('ciclo',1)
    names = {filename(data['issue'],data['rodada'],data['papel'],cycle)}
    if cycle == 1:
        names.add(f"{data['issue']}-c1-r{data['rodada']}-{data['papel']}.json")
    require(path.name in names, 'Nome diverge de issue/ciclo/rodada/papel.')
    ids = [a['id'] for a in data['ajustes']]
    require(len(ids) == len(set(ids)), 'IDs de ajustes duplicados.')
    if data['papel'] == 'claude':
        ids = [c['id'] for c in data['criterios']]
        require(len(ids) == len(set(ids)), 'IDs de critérios duplicados.')
        require({'pr-audit','security-audit'} <= set(data['skills_usadas']), 'Revisão exige as duas skills de auditoria.')
        pending = any(c['status'] != 'atendido' for c in data['criterios'])
        blocking = any(a['gravidade'] == 'bloqueante' for a in data['ajustes'])
        require((not pending and not blocking) if data['veredito'] == 'pode_mergear' else (pending or blocking), 'Veredito incoerente com critérios/ajustes.')
    else:
        for item in data['ajustes']:
            require(item['commit'] is None or text(item['commit']) and re.fullmatch('[a-fA-F0-9]{7,64}',item['commit']), 'Commit deve ser SHA ou null.')
            require(item['status'] != 'corrigido' or item['commit'] is not None, 'Correção exige SHA do commit.')
    return data


def validate_round(project, issue, round_number=None, cycle=1, role=None):
    require(role in {None,'claude','codex','par'}, 'Papel de validação inválido.')
    require(type(issue) is int and issue > 0 and type(cycle) is int and cycle > 0, 'Issue/ciclo inválidos.')
    existing = rounds(project, issue, cycle)
    number = round_number if round_number is not None else (max(existing) if existing else 0)
    require(type(number) is int and number > 0, 'Rodada ausente/inválida.')
    claude = validate_file(path_for(project,issue,number,'claude',cycle))
    require(claude['issue'] == issue and claude['rodada'] == number and claude.get('ciclo',1) == cycle, 'Objeto do handoff divergente.')
    if number > 2:
        d = decision(project,issue,claude['pr'],cycle)
        require(d and d['decisao'] == 'iterar' and d['apos_rodada'] < number <= d['autorizado_ate'], 'Rodada adicional exige decisão humana iterar.')
    if number > 1:
        previous, _ = validate_round(project,issue,number-1,cycle,'par')
        require(previous['veredito'] == 'ajustes' and previous['pr'] == claude['pr'], 'Rodada anterior não exige ajustes ou pertence a outra PR.')
    response_path = path_for(project,issue,number,'codex',cycle)
    response = None
    if role in {'codex','par'} or role is None and response_path.exists():
        response = validate_file(response_path)
        require(all(response.get(k,1) == claude.get(k,1) for k in ('issue','pr','rodada','ciclo')), 'Resposta pertence a outra issue/PR/rodada/ciclo.')
        require(all(response['candidato'][k] == claude['candidato'][k] for k in ('base','head')), 'Resposta trocou base/branch do candidato.')
        require(claude['veredito'] == 'ajustes', 'Não responder uma revisão já aprovada.')
        ids = {a['id'] for a in claude['ajustes']}
        answered = {a['id'] for a in response['ajustes']}
        blocking = {a['id'] for a in claude['ajustes'] if a['gravidade'] == 'bloqueante'}
        require(answered <= ids and blocking <= answered, 'Resposta tem ID desconhecido ou não responde todos os bloqueantes.')
    return claude, response


def summary(claude, response=None):
    fixed = {a['id'] for a in (response or {}).get('ajustes',[]) if a['status'] == 'corrigido'}
    return {'issue':claude['issue'],'pr':claude['pr'],'ciclo':claude.get('ciclo',1),'rodada':claude['rodada'],
            'veredito':claude['veredito'],'bloqueantes_abertos':sum(a['gravidade']=='bloqueante' and a['id'] not in fixed for a in claude['ajustes']),
            'pronto_para_humano':claude['veredito']=='pode_mergear'}


def main():
    parser=ContractParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--issue',type=int,required=True)
    parser.add_argument('--round',type=int)
    parser.add_argument('--cycle',type=int,default=1)
    parser.add_argument('--role',choices=['claude','codex','par'])
    args=parser.parse_args()
    try:
        print(json.dumps(summary(*validate_round(args.project.resolve(),args.issue,args.round,args.cycle,args.role)),ensure_ascii=False))
        return 0
    except (ContractError,OSError,ValueError,KeyError,TypeError,RecursionError):
        print('Handoff inválido ou incompleto; confira schema, nomes, vínculos e decisões. Conteúdo omitido.',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
