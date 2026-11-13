#!/usr/bin/env python3
"""Conduz etapas explícitas de uma issue: Codex, CI, Claude e aceite humano local."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

from check_delivery import ContractError, ContractParser, read_json, require, validate_config
from distribution import atomic_write
import check_handoff as handoff
import ci_gate
import issue_session

ROOT=Path(__file__).resolve().parents[1]
PROMPTS=ROOT/'skills/issue-bot/prompts'
STAGES={'implement':'implementar','review':'revisar','respond':'responder-handoff',
        'corrigir-ci':'corrigir-ci','subir-ambiente':'subir-ambiente'}
COMMANDS=['session-up','session-down','implement','ci-gate','review','respond','env-up','status','prepare-prompt']


def local_run(project,args,allowed=(0,)):
    result=issue_session.run(args,cwd=project,allowed=allowed)
    return result.stdout.strip()


def project_root(project):
    project=Path(project).absolute()
    require(project.resolve()==project,'Projeto não pode usar caminho com symlink.')
    common=local_run(project,['git','rev-parse','--path-format=absolute','--git-common-dir'])
    root=Path(common).parent.resolve()
    require(root==project,'--project deve apontar para o checkout principal, não outra worktree.')
    return root


def worktree_path(args):
    return args.project/'.worktrees'/f'issue-{args.issue}'


def cycle_receipt(args,cycle):
    directory=args.project/'.bezalel/issue-bot'
    require(not directory.is_symlink() and not directory.parent.is_symlink(),'Estado do ciclo não pode usar symlink.')
    path=directory/f'{args.issue}-c{cycle}-environment.json'
    require(not path.is_symlink(),'Recibo do ambiente não pode ser symlink.')
    return path


def verify_cycle(args):
    if args.cycle==1:
        return
    path=cycle_receipt(args,args.cycle-1)
    require(path.is_file(),'Novo ciclo exige env-up concluído no ciclo anterior.')
    receipt=read_json(path)
    require(isinstance(receipt,dict) and receipt.get('issue')==args.issue and receipt.get('ciclo')==args.cycle-1
            and receipt.get('ready') is True,'Novo ciclo exige env-up concluído no ciclo anterior.')
    require(args.pr is None or receipt.get('pr')==args.pr,'Novo ciclo pertence à PR do ambiente testado.')
    require(bool(args.human_decision_source and args.human_decision_source.strip()),
            'Novo ciclo exige --human-decision-source com a origem real do ajuste de usabilidade humano.')


def config_for(project):
    config=read_json(project/'.bezalel/project.json')
    validate_config(config,project)
    return config


def session_name(config,issue):
    return issue_session.valid_name(config['project'].lower().replace(' ','-'))+f'-{issue}'


def resolve_pr(args,required=True):
    if args.pr:
        pr=ci_gate.pr_info(args.project,args.pr)
    else:
        results=json.loads(ci_gate.gh(args.project,'pr','list','--state','open','--json','number,closingIssuesReferences').stdout)
        matches=[p for p in results if any(i.get('number')==args.issue for i in p.get('closingIssuesReferences',[]))]
        if not matches and not required:
            return None
        require(len(matches)==1,'Informe --pr: é necessária uma PR aberta vinculada de forma inequívoca à issue.')
        pr=ci_gate.pr_info(args.project,matches[0]['number'])
    issue_url=pr['url'].rsplit('/pull/',1)[0]+'/issues/'+str(args.issue)
    require(any(i.get('number')==args.issue and i.get('url')==issue_url for i in pr.get('closingIssuesReferences',[])), 'A PR não está vinculada à issue deste repositório por closing reference.')
    if args.branch:
        require(pr['headRefName']==args.branch,'Branch informada diverge da PR.')
    args.pr=pr['number']
    return pr


def check_worktree(args,pr=None,create=False,config=None):
    path=worktree_path(args)
    branch=pr['headRefName'] if pr else args.branch or f'issue-{args.issue}'
    local_run(args.project,['git','check-ref-format','--branch',branch])
    if path.exists() or path.is_symlink():
        root,_=issue_session.project_paths(path,args.issue,branch)
        require(root==args.project,'Worktree pertence a outro projeto.')
    elif create:
        exists=subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+branch],cwd=args.project).returncode==0
        if exists:
            command=['git','worktree','add',str(path),branch]
        else:
            require(pr is None,'Branch da PR ausente localmente; solicite fetch explícito ao operador.')
            branches=set(config['production_branches'].values())
            base=args.base_ref or (next(iter(branches)) if len(branches)==1 else None)
            require(base and base!='CONFIGURAR_BRANCH_REAL','Informe --base-ref local verificável.')
            local_run(args.project,['git','rev-parse','--verify','--end-of-options',base+'^{commit}'])
            command=['git','worktree','add','-b',branch,str(path),base]
        local_run(args.project,command)
        issue_session.project_paths(path,args.issue,branch)
    else:
        raise ContractError('Worktree da issue ausente; execute session-up primeiro.')
    if pr:
        sha=local_run(path,['git','rev-parse','HEAD'])
        require(sha==pr['headRefOid'],'HEAD local diverge da PR; atualize explicitamente antes de continuar.')
        local_run(path,['git','diff','--quiet'])
        local_run(path,['git','diff','--cached','--quiet'])
    return path,branch


def latest(args,role=None):
    numbers=handoff.rounds(args.project,args.issue,args.cycle)
    if not numbers:
        return None
    return handoff.validate_round(args.project,args.issue,max(numbers),args.cycle,role)


def human_extension(args,pr,last_round):
    data=handoff.decision(args.project,args.issue,pr,args.cycle)
    if data:
        require(data['apos_rodada']<=last_round,'Decisão humana não corresponde à revisão.')
        # Arquivo escrito pelo agente não autentica a pessoa. O operador precisa
        # confirmar a fonte na invocação, a partir da interação humana real.
        require(args.human_decision_source==data['fonte'],'Confirme --human-decision-source com a fonte da interação humana real; JSON sozinho não autoriza.')
    return data


def target_round(args,pr):
    previous=latest(args)
    if previous is None:
        number=1
    else:
        claude,response=previous
        if args.round==claude['rodada']:
            if args.round>2:
                human_extension(args,pr['number'],claude['rodada'])
            return args.round
        require(claude['veredito']=='ajustes','Revisão aprovada; ajustes humanos de usabilidade exigem novo --cycle.')
        number=claude['rodada']+1
        if number>2:
            d=human_extension(args,pr['number'],claude['rodada'])
            if not d or d['decisao']!='iterar' or d['autorizado_ate']<number:
                return None
        require(response is not None,'Responda o handoff anterior antes de nova revisão.')
    require(args.round is None or args.round==number,'Rodada solicitada não é a próxima válida.')
    return number


def render_prompt(args,stage,pr=None,number=None):
    require(stage in STAGES,'Estágio de prompt inválido.')
    issue=json.loads(ci_gate.gh(args.project,'issue','view',str(args.issue),'--json','number,url,body,title').stdout)
    require(issue.get('number')==args.issue and issue.get('body'),'Issue precisa ter escopo, critérios de aceite e fora de escopo explícitos.')
    # O texto integral evita inventar ou descartar critérios na extração por regex.
    number=number or args.round or 1
    role='claude' if stage=='review' else 'codex'
    path=handoff.path_for(args.project,args.issue,number,role,args.cycle)
    previous=handoff.path_for(args.project,args.issue,number-1,'codex',args.cycle) if number>1 else None
    fence='`'*max(3,1+max((len(m[0]) for m in re.finditer(r'`+',issue['body'])),default=0))
    values={'data_fence':fence,'issue_url':issue['url'],'issue_body':issue['body'],'acceptance_criteria':issue['body'],
            'pr_url':pr['url'] if pr else 'Ainda não aberta: abrir PR vinculada à issue.',
            'round':str(number),'cycle':str(args.cycle),'handoff_path':str(path),
            'review_handoff_path':str(handoff.path_for(args.project,args.issue,number,'claude',args.cycle)),
            'previous_handoff_path':str(previous) if previous else 'Primeira rodada deste ciclo.',
            'project_root':str(args.project),'worktree':str(worktree_path(args)),
            'branch':pr['headRefName'] if pr else args.branch or f'issue-{args.issue}',
            'sha':pr['headRefOid'] if pr else 'Confirmar HEAD após implementação.',
            'max_rounds':'2 (rodadas adicionais somente após decisão humana real)',
            'schema_path':str(handoff.CONTRACTS/'contracts/handoff.schema.json'),
            'env_prompt':str(PROMPTS/'subir-ambiente.md'),'package_root':str(ROOT)}
    template=(PROMPTS/(STAGES[stage]+'.md')).read_text()
    def replace(match):
        require(match[1] in values,'Placeholder de prompt desconhecido.')
        return values[match[1]]
    # Substituição única: conteúdo da issue é dado não confiável e não é template.
    return re.sub(r'\{\{([a-z_]+)\}\}',replace,template)


def dispatch(args,config,stage,pr=None,number=None):
    prompt=render_prompt(args,stage,pr,number)
    if args.dry_run:
        return prompt
    path,branch=check_worktree(args,pr)
    state=issue_session.status(session_name(config,args.issue))
    require(state['exists'] and all(w['alive'] and w['cwd']==str(path) for w in state['windows']), 'Sessão não está pronta na worktree da issue.')
    directory=args.project/'.bezalel/issue-bot'
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,name=tempfile.mkstemp(prefix=f'{args.issue}-prompt-',suffix='.md',dir=directory)
    with os.fdopen(fd,'w') as stream:
        stream.write(prompt)
    window='claude' if stage=='review' else 'codex'
    result=subprocess.run(['bash',str(ROOT/'scripts/issue_session.sh'),'send','--session',session_name(config,args.issue),
                           '--window',window,'--text-file',name],capture_output=True,text=True)
    require(result.returncode==0,'Falha ao enviar prompt; arquivo local preservado para diagnóstico.')


def wait_handoff(args,pr,number,role):
    deadline=time.monotonic()+args.timeout_seconds
    path=handoff.path_for(args.project,args.issue,number,role,args.cycle)
    while not path.exists():
        if time.monotonic()>=deadline:
            return None
        time.sleep(min(args.poll_seconds,max(0,deadline-time.monotonic())))
    pair=handoff.validate_round(args.project,args.issue,number,args.cycle,role if role=='claude' else 'par')
    current=ci_gate.pr_info(args.project,pr['number'])
    candidate=pair[0 if role=='claude' else 1]
    require(candidate['pr']==pr['number'] and candidate['candidato']=={'base':current['baseRefName'],'head':current['headRefName'],'sha':current['headRefOid']},'Handoff não pertence ao candidato atual da PR.')
    return pair


def env_up(args,config,pr):
    previous=latest(args)
    require(previous is not None,'Revisão válida ausente antes de env-up.')
    claude,response=previous
    require(claude['pr']==pr['number'],'Handoff pertence a outra PR.')
    if claude['veredito']!='pode_mergear':
        d=human_extension(args,pr['number'],claude['rodada'])
        if not d or d['decisao']!='finalizar' or d['apos_rodada']!=claude['rodada']:
            return 4,{'status':'decisao_humana_necessaria','issue':args.issue}
    current=(response or claude)['candidato']
    require(current=={'base':pr['baseRefName'],'head':pr['headRefName'],'sha':pr['headRefOid']},'Revisão/resposta pertence a outra versão; refaça CI/revisão.')
    code,ci=ci_gate.gate(args.project,pr['number'],args.timeout_seconds,args.poll_seconds,args.dry_run)
    if code: return code,ci
    data=config['data']
    mode=args.data_mode or data['mode']
    if mode=='ask': return 5,{'status':'decisao_de_dados_necessaria','issue':args.issue}
    if not (args.project/'.envstack/stack.yaml').is_file(): return 5,{'status':'manifesto_ausente','issue':args.issue}
    if args.dry_run: return 0,{'status':'dry_run','branch':pr['headRefName'],'data_mode':mode}
    path,branch=check_worktree(args,pr)
    env_scripts=ROOT/'skills/env/scripts'
    # A autorização compartilhada só alcança ensure. Status e restore não a herdam.
    clean_env={k:v for k,v in os.environ.items() if k!='ENV_ALLOW_SHARED_INFRA'}
    def observe_environment():
        result=subprocess.run(['bash',str(env_scripts/'ctl.sh'),'status',f'issue-{args.issue}','--json'],
                              cwd=args.project,capture_output=True,text=True,env=clean_env)
        require(result.returncode in (0,5),'ENV não forneceu status verificável.')
        return result,json.loads(result.stdout)
    run,status=observe_environment()
    if run.returncode or not status.get('ready'):
        if not (getattr(args,'allow_shared_infra',False) or os.environ.get('ENV_ALLOW_SHARED_INFRA')=='1'):
            return 5,{'status':'autorizacao_de_infra_necessaria','issue':args.issue}
        run=subprocess.run(['bash',str(env_scripts/'ctl.sh'),'ensure',f'issue-{args.issue}','--branch',branch,'--issue',str(args.issue)],
                           cwd=args.project,capture_output=True,text=True,env={**clean_env,'ENV_ALLOW_SHARED_INFRA':'1'})
        require(run.returncode==0,'ENV não concluiu ensure; dados não foram restaurados (diagnóstico omitido).')
        run,status=observe_environment()
        if run.returncode or not status.get('ready'): return 5,status
    require(status.get('worktree')==str(path) and status.get('branch')==branch and status.get('issue')==args.issue,'ENV aponta para outro destino; restore bloqueado.')
    check_worktree(args,pr)
    observed=ci_gate.pr_info(args.project,pr['number'])
    require(observed['headRefOid']==pr['headRefOid'],'PR mudou enquanto ENV iniciava; restore bloqueado.')
    restore_result='not_applicable'
    if mode=='snapshot':
        identity=status.get('environment_id')
        require(isinstance(identity,str) and re.fullmatch(r'[a-zA-Z0-9-]+',identity),
                'ENV sem identidade de geração; atualize seus metadados antes do snapshot.')
        workdir=(path/data.get('workdir','.')).resolve()
        require(workdir.is_dir() and (workdir==path or path in workdir.parents),'workdir do restore fora da worktree.')
        receipt=cycle_receipt(args,args.cycle).parent/f'{args.issue}-{identity}-restore.json'
        require(not receipt.is_symlink(),'Recibo de restore não pode usar symlink.')
        signature=hashlib.sha256(json.dumps({'restore':data['restore'],'dataset':data['dataset'],'workdir':str(workdir)},sort_keys=True).encode()).hexdigest()
        previous_restore=read_json(receipt) if receipt.exists() else None
        repeat=getattr(args,'restore_again',False)
        if repeat:
            require(bool(args.human_decision_source and args.human_decision_source.strip()),
                    'Repetir restore exige --human-decision-source com aprovação humana do comando configurado.')
        elif previous_restore:
            require(previous_restore.get('signature')==signature and previous_restore.get('state')=='completed',
                    'Restore mudou ou ficou incompleto; preserve os dados e solicite --restore-again com aprovação humana.')
        if previous_restore and not repeat:
            restore_result='already_completed'
        else:
            # Marcar antes: uma falha parcial não autoriza tentar novamente e apagar dados.
            record={'environment_id':identity,'signature':signature,'state':'started'}
            atomic_write(receipt,json.dumps(record).encode(),0o600)
            restore=subprocess.run(data['restore'],cwd=workdir,capture_output=True,text=True,env=clean_env)
            require(restore.returncode==0,'Restore falhou; saída privada omitida. Ambiente não declarado pronto para aceite.')
            atomic_write(receipt,json.dumps({**record,'state':'completed'}).encode(),0o600)
            restore_result='completed'
    atomic_write(cycle_receipt(args,args.cycle),json.dumps({'issue':args.issue,'pr':pr['number'],
                 'ciclo':args.cycle,'sha':pr['headRefOid'],'ready':True}).encode(),0o600)
    return 0,{**status,'data_mode':mode,'restore':restore_result,'merge_autorizado':False}


@contextlib.contextmanager
def command_lock(args):
    directory=args.project/'.bezalel/issue-bot'
    require(not directory.is_symlink() and not directory.parent.is_symlink(),'Estado local não pode usar symlink.')
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    path=directory/f'{args.issue}.lock'
    require(not path.is_symlink(),'Lock não pode ser symlink.')
    with path.open('a') as stream:
        try: fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise ContractError('Outra etapa desta issue está em andamento.') from None
        yield


def execute(args,config):
    if args.command in {'review','respond'}:
        verify_cycle(args)
    session=session_name(config,args.issue)
    if args.command=='session-down':
        if args.dry_run: return 0,{'session':session,'dry_run':True}
        return destroy_session(session)
    if args.command=='session-up':
        if args.dry_run: return 0,{'session':session,'worktree':str(worktree_path(args)),'dry_run':True}
        pr=resolve_pr(args,required=False)
        path,branch=check_worktree(args,pr,create=True,config=config)
        return 0,{'session':session,'hint':issue_session.create(argparse.Namespace(project_name=config['project'],issue=args.issue,cwd=path,branch=branch,log_dir=args.log_dir))}
    if args.command=='prepare-prompt':
        require(args.prompt_stage,'Informe estágio do prompt.')
        pr=resolve_pr(args,required=False)
        prompt=render_prompt(args,args.prompt_stage,pr)
        if args.output:
            require(not args.output.exists() and args.project in args.output.resolve().parents,'Saída deve ser nova e interna ao projeto.')
            args.output.write_text(prompt)
        else: print(prompt)
        return 0,None
    pr=resolve_pr(args,required=args.command!='status')
    if args.command=='ci-gate':
        code,result=ci_gate.gate(args.project,pr['number'],args.timeout_seconds,args.poll_seconds,args.dry_run)
        if code==2:
            prompt=dispatch(args,config,'corrigir-ci',pr)
            if args.dry_run: result['correction_prompt']=prompt
        return code,result
    if args.command=='status':
        prior=latest(args)
        ci=ci_gate.observe(args.project,pr['number']) if pr else {'status':'not_started'}
        state=issue_session.status(session)
        env=subprocess.run(['bash',str(ROOT/'skills/env/scripts/ctl.sh'),'status',f'issue-{args.issue}','--json'],cwd=args.project,capture_output=True,text=True)
        try: environment=json.loads(env.stdout)
        except ValueError: environment={'ready':False,'status':'ausente_ou_indisponivel'}
        return 0,{'issue':args.issue,'pr':pr['number'] if pr else None,'sha':pr['headRefOid'] if pr else None,'ci':ci,'ciclo':args.cycle,
                  'rodada':prior[0]['rodada'] if prior else 0,'veredito':prior[0]['veredito'] if prior else None,
                  'handoff_paths':[str(handoff.path_for(args.project,args.issue,n,r,args.cycle)) for n in handoff.rounds(args.project,args.issue,args.cycle) for r in ('claude','codex')],
                  'session':state,'environment':environment}
    if args.command=='env-up': return env_up(args,config,pr)
    if args.command=='implement':
        dispatch(args,config,'implement',pr)
        return 0,{'status':'prompt_preparado' if args.dry_run else 'enviado','issue':args.issue}
    if args.command=='review':
        number=target_round(args,pr)
        if number is None: return 4,{'status':'limite_de_rodadas','issue':args.issue}
        code,ci=ci_gate.gate(args.project,pr['number'],args.timeout_seconds,args.poll_seconds,args.dry_run)
        if code: return code,ci
        require(pr['headRefOid']==ci['sha'],'Candidato mudou durante o portão de CI; repita a etapa.')
        path=handoff.path_for(args.project,args.issue,number,'claude',args.cycle)
        prompt=dispatch(args,config,'review',pr,number) if not path.exists() else None
        if args.dry_run: return 0,{'status':'dry_run','rodada':number,'prompt':prompt}
        pair=wait_handoff(args,pr,number,'claude')
        if pair is None: return 3,{'status':'aguardando_handoff','rodada':number}
        code,ci=ci_gate.gate(args.project,pr['number'],0,args.poll_seconds,True)
        if code: return code,ci
        require(pair[0]['candidato']['sha']==ci['sha'],'PR mudou durante a revisão; refaça as provas afetadas.')
        return (0 if pair[0]['veredito']=='pode_mergear' else 2),handoff.summary(*pair)
    if args.command=='respond':
        pair=latest(args,'claude')
        require(pair and pair[0]['veredito']=='ajustes','Não existe handoff de ajustes válido.')
        number=pair[0]['rodada']
        require(args.round is None or args.round==number,'Responda a última rodada.')
        if number>=2:
            d=human_extension(args,pr['number'],number)
            if not d or d['decisao']!='iterar' or d['autorizado_ate']<=number:
                return 4,{'status':'limite_de_rodadas','issue':args.issue}
        path=handoff.path_for(args.project,args.issue,number,'codex',args.cycle)
        prompt=None
        if not path.exists():
            require(pair[0]['pr']==pr['number'] and pair[0]['candidato']=={'base':pr['baseRefName'],'head':pr['headRefName'],'sha':pr['headRefOid']},'Handoff do Claude está desatualizado; não responda outro candidato.')
            prompt=dispatch(args,config,'respond',pr,number)
        if args.dry_run: return 0,{'status':'dry_run','rodada':number,'prompt':prompt}
        response=wait_handoff(args,pr,number,'codex')
        if response is None: return 3,{'status':'aguardando_handoff','rodada':number}
        return 0,handoff.summary(*response)
    raise ContractError('Comando desconhecido.')


def destroy_session(session):
    state=issue_session.status(session)
    require(state['exists'],'Sessão ausente.')
    issue_session.tmux('kill-session','-t','='+session)
    return 0,{'session':session,'status':'encerrada','logs':'preservados','environment':'preservado'}


def main():
    parser=ContractParser(description=__doc__)
    parser.add_argument('command',choices=COMMANDS)
    parser.add_argument('prompt_stage',nargs='?',choices=list(STAGES))
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--issue',type=int,required=True)
    parser.add_argument('--pr',type=int)
    parser.add_argument('--round',type=int)
    parser.add_argument('--cycle',type=int,default=1)
    parser.add_argument('--branch')
    parser.add_argument('--base-ref')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--log-dir')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--timeout-seconds',type=float,default=1800)
    parser.add_argument('--poll-seconds',type=float,default=2)
    parser.add_argument('--allow-shared-infra',action='store_true',help='Autoriza infra apenas no ensure desta chamada.')
    parser.add_argument('--restore-again',action='store_true',help='Repete snapshot; exige origem da aprovação humana do comando.')
    parser.add_argument('--data-mode',choices=['empty'])
    parser.add_argument('--human-decision-source')
    args=parser.parse_args()
    try:
        require(args.issue>0 and args.cycle>0 and (args.round is None or args.round>0) and args.timeout_seconds>=0 and args.poll_seconds>0,'Argumentos numéricos inválidos.')
        args.project=project_root(args.project)
        config=config_for(args.project)
        if args.command=='implement':
            verify_cycle(args)
            # Ainda não existe PR na primeira implementação.
            pr=resolve_pr(args,required=False)
            with contextlib.nullcontext() if args.dry_run else command_lock(args):
                prompt=dispatch(args,config,'implement',pr)
            print(json.dumps({'status':'dry_run' if args.dry_run else 'enviado','issue':args.issue,'prompt':prompt},ensure_ascii=False))
            return 0
        with contextlib.nullcontext() if args.dry_run or args.command in {'status','prepare-prompt'} else command_lock(args):
            code,result=execute(args,config)
        if result is not None: print(json.dumps(result,ensure_ascii=False))
        return code
    except (ContractError,OSError,ValueError,TypeError,KeyError,RecursionError,subprocess.TimeoutExpired) as error:
        print(str(error) if isinstance(error,ContractError) else 'Etapa interrompida: entrada ou ferramenta inválida; conteúdo privado omitido.',file=sys.stderr)
        return 1


if __name__=='__main__': sys.exit(main())
