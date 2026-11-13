#!/usr/bin/env python3
"""Emite somente metadados públicos do ambiente; nunca imprime Compose/env bruto."""
import json
from pathlib import Path
import subprocess
import sys


def query(args):
    result=subprocess.run(args,capture_output=True,text=True,timeout=60)
    if result.returncode:
        raise ValueError('Consulta de status falhou.')
    return result.stdout


def status(root,state,name,context):
    compose=['docker','compose','-f',str(state/'docker-compose.yml')]
    config=json.loads(query(compose+['config','--format','json']))
    manifest=json.loads(query(['yq','-o=json','.',str(root/'.envstack/stack.yaml')]))
    raw=query(compose+['ps','--all','--format','json']).strip()
    try:
        containers=json.loads(raw) if raw else []
        if isinstance(containers,dict): containers=[containers]
    except ValueError:
        containers=[json.loads(line) for line in raw.splitlines() if line.strip()]
    def ready(service):
        rows=[c for c in containers if c.get('Service')==service]
        return bool(rows) and all(c.get('State')=='running' and c.get('Health','') in ('','healthy') for c in rows)
    active=[c.get('Service') for c in containers if c.get('State')=='running']
    remembered=(state/'started-services').read_text().splitlines() if (state/'started-services').is_file() else []
    required=set(remembered or active or config.get('x-envstack',{}).get('startup_services',[]) or config['services'])
    todo=list(required)
    while todo:
        service=todo.pop()
        for dependency in config['services'].get(service,{}).get('depends_on',{}):
            if dependency not in required:
                required.add(dependency); todo.append(dependency)
    project=manifest['project']; tld=manifest.get('tld','local')
    services=[]
    for service in manifest['services']:
        folder=service['folder']
        services.append({'folder':folder,'url':f'https://{name}-{folder}.{project}.{tld}',
                         'port':service['port'],'ready':ready(folder),
                         'aliases':[f'https://{name}-{folder}-{a}.{project}.{tld}' for a in service.get('aliases',[])]})
    engine=manifest.get('database','postgres')
    if engine not in ('mysql','postgres'): engine='postgres'
    ports=config['services'].get(engine,{}).get('ports',[])
    port=next((int(p['published']) for p in ports if isinstance(p,dict) and p.get('published')),None)
    shared=state/'shared-database.json'
    if shared.is_file():
        port=json.loads(shared.read_text())['pool']['port']
    issue=(state/'issue').read_text().strip() if (state/'issue').is_file() else None
    branch=(state/'worktree-branch').read_text().strip()
    return {'project':project,'environment':name,'issue':int(issue) if issue else None,
            'environment_id':(state/'environment-id').read_text().strip() if (state/'environment-id').is_file() else None,
            'branch':branch,'worktree':str(root/'.worktrees'/name),'docker_context':context,
            'ready':bool(required) and all(ready(s) for s in required),'services':services,
            'database':{'engine':engine,'host':'localhost','port':port}}


def main():
    try:
        result=status(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3],sys.argv[4])
        print(json.dumps(result,ensure_ascii=False))
        return 0 if result['ready'] else 5
    except (OSError,ValueError,TypeError,KeyError,subprocess.TimeoutExpired):
        print('Não foi possível verificar status; diagnóstico privado omitido.',file=sys.stderr)
        return 1


if __name__=='__main__': sys.exit(main())
