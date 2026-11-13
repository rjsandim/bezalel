#!/usr/bin/env python3
"""Sessões tmux interativas por issue, com login de conta e sandbox preservado."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from check_delivery import ContractError, ContractParser, require

KEY_VARIABLES = ('OPENAI_API_KEY','ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','CODEX_API_KEY',
                 'AZURE_OPENAI_API_KEY','OPENAI_BASE_URL','ANTHROPIC_BASE_URL',
                 'CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY')
CLI_PROCESS_NAMES = {'codex': {'codex'}, 'claude': {'claude'}}


def run(args, cwd=None, allowed=(0,)):
    try:
        result = subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=30)
    except (OSError,subprocess.TimeoutExpired):
        raise ContractError('Ferramenta ausente/indisponível ou timeout.') from None
    require(result.returncode in allowed,'Comando falhou; diagnóstico privado omitido.')
    return result


def tmux(*args, allowed=(0,)):
    return run(['tmux',*args],allowed=allowed)


def valid_name(value):
    require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',value or ''),'Nome de sessão/projeto inválido.')
    return value


def session_exists(session):
    return tmux('has-session','-t','='+session,allowed=(0,1)).returncode==0


def project_paths(cwd, issue, branch=None):
    cwd=Path(cwd).absolute()
    require(cwd.is_dir() and cwd.resolve()==cwd,'cwd deve ser diretório real, sem symlink.')
    top=Path(run(['git','rev-parse','--show-toplevel'],cwd).stdout.strip()).resolve()
    require(top==cwd,'Use a raiz exata da worktree da issue.')
    common=Path(run(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd).stdout.strip())
    root=common.parent.resolve()
    current=run(['git','branch','--show-current'],cwd).stdout.strip()
    require(current==(branch or f'issue-{issue}'),'cwd/branch não corresponde à issue informada.')
    listed=run(['git','worktree','list','--porcelain'],root).stdout
    require('worktree '+str(cwd)+'\n' in listed,'Worktree não registrada.')
    return root,cwd


def cli_commands(cwd, root):
    require(not any(os.environ.get(k) for k in KEY_VARIABLES),'Remova variáveis de chave/provedor desta invocação; use login da conta.')
    binaries={}
    for name in ('codex','claude'):
        found=shutil.which(name)
        require(found,f'{name} ausente; instale e faça login da conta manualmente.')
        binaries[name]=str(Path(found).resolve())
    codex=run(['codex','--help']).stdout
    claude=run(['claude','--help']).stdout
    require(all(flag in codex for flag in ('--approve-for-me','--ask-for-approval','--cd','--no-alt-screen','--no-daemon')),'Codex sem flags interativas suportadas; confira a versão.')
    require(all(flag in claude for flag in ('--dangerously-skip-permissions','--settings','--setting-sources','--strict-mcp-config','--tools')),'Claude sem flags suportadas; confira a versão.')
    login=run(['codex','login','status'],allowed=(0,1))
    require(login.returncode==0 and re.search(r'^Logged in using ChatGPT\b',login.stdout+login.stderr,re.M|re.I),'Faça codex login com sua conta ChatGPT.')
    login=run(['claude','auth','status','--json'],allowed=(0,1))
    try:
        account=json.loads(login.stdout)
    except ValueError:
        raise ContractError('Não foi possível confirmar login; execute claude auth login.') from None
    require(login.returncode==0 and account.get('loggedIn') is True and account.get('authMethod')=='claude.ai','Faça claude auth login com sua conta Claude; API key não é aceita.')
    # Apenas Bash fica disponível ao revisor. Sem hooks/MCP; sandbox estrito não
    # tem retry fora do isolamento. Nenhuma configuração persistente é editada.
    settings={'disableAllHooks':True,'sandbox':{'enabled':True,'autoAllowBashIfSandboxed':True,
                'allowUnsandboxedCommands':False,'failIfUnavailable':True,
                'excludedCommands':[],'filesystem':{'disabled':False,'allowWrite':[str(cwd),str(root/'.bezalel/handoff')]}},
              'permissions':{'additionalDirectories':[]}}
    return {'codex':[binaries['codex'],'--no-daemon','--approve-for-me',
                     '--cd',str(cwd),'--add-dir',str(root/'.bezalel/handoff'),'--no-alt-screen',
                     '-c','forced_login_method="chatgpt"','-c','model_provider="openai"',
                     '-c','sandbox_workspace_write.writable_roots=[]','-c','sandbox_workspace_write.network_access=true'],
            'claude':[binaries['claude'],'--dangerously-skip-permissions','--setting-sources','',
                      '--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--tools','Bash',
                      '--settings',json.dumps(settings,separators=(',',':'))]}


def pane(session,window):
    require(window in {'codex','claude'},'Janela inválida.')
    result=tmux('display-message','-p','-t',session+':'+window,'#{pane_dead}\t#{pane_current_command}\t#{pane_current_path}\t#{pane_pipe}')
    values=result.stdout.rstrip('\n').split('\t')
    require(len(values)==4 and values[0]=='0','Janela ausente ou morta.')
    return values


def cli_alive(session, window, process):
    # O executável autenticado pode ter nome de versão (instalação nativa Claude).
    # Não considerar qualquer processo que não seja shell como um CLI válido.
    executable=tmux('show-options','-qv','-t',session,'@bezalel-executable-'+window).stdout.strip()
    names=CLI_PROCESS_NAMES[window] | ({Path(executable).name} if executable.startswith('/') else set())
    return process in names


def hint(session):
    return f'tmux attach -t {session}\nCtrl+b depois n troca a janela; Ctrl+b depois d sai sem encerrar. Você pode digitar para intervir.'


def status(session):
    if not session_exists(session):
        return {'session':session,'exists':False,'windows':[]}
    require(tmux('show-options','-qv','-t',session,'@bezalel-issue-session').stdout.strip()=='1','Sessão preexistente não gerenciada; não será adotada.')
    require(tmux('list-windows','-t','='+session,'-F','#{window_name}').stdout.splitlines()==['codex','claude'],'Sessão não possui exatamente as duas janelas esperadas.')
    windows=[]
    for window in ('codex','claude'):
        data=tmux('display-message','-p','-t',session+':'+window,'#{pane_dead}\t#{pane_current_command}\t#{pane_current_path}').stdout.rstrip('\n').split('\t')
        require(len(data)==3,'Janela ausente.')
        log=tmux('show-options','-qv','-t',session,'@bezalel-log-'+window).stdout.strip()
        windows.append({'name':window,'alive':data[0]=='0' and cli_alive(session,window,data[1]),'cwd':data[2],'log':log})
    return {'session':session,'exists':True,'windows':windows}


def create(args):
    require(args.cwd and args.issue and args.issue>0 and args.project_name,'Informe projeto, issue e cwd.')
    project=valid_name(args.project_name.lower().replace(' ','-'))
    session=f'{project}-{args.issue}'
    root,cwd=project_paths(args.cwd,args.issue,args.branch)
    exists=session_exists(session)
    commands=None if exists else cli_commands(cwd,root)
    log_dir=Path(args.log_dir).absolute() if args.log_dir else root/'.bezalel/logs'
    require(log_dir.resolve()==log_dir and (log_dir==root or root in log_dir.parents),'Logs precisam ficar dentro do projeto, sem symlinks.')
    require(not (root/'.worktrees'==log_dir or root/'.worktrees' in log_dir.parents),'Logs devem sobreviver à worktree efêmera.')
    require(not (root/'.bezalel/handoff').is_symlink(), 'Diretório de handoff não pode ser symlink.')
    if exists:
        state=status(session)
        require(all(w['cwd']==str(cwd) and w['alive'] for w in state['windows']),'Sessão existe em outra pasta ou CLI morreu; confira antes de recriar.')
        saved=tmux('show-options','-qv','-t',session,'@bezalel-log-dir').stdout.strip()
        require(saved==str(log_dir),'Não troque diretório de logs de uma sessão em andamento.')
    else:
        log_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
        (root/'.bezalel/handoff').mkdir(parents=True,exist_ok=True,mode=0o700)
        # tmux usa um shell para o comando; quoting explícito e ambiente sem chaves
        # impedem interpolação e herança de chaves antigas do servidor tmux.
        clean=['env']+[arg for key in KEY_VARIABLES for arg in ('-u',key)]
        tmux('new-session','-d','-s',session,'-n','codex','-c',str(cwd),shlex.join(clean+commands['codex']))
        tmux('set-option','-t',session,'@bezalel-issue-session','1')
        tmux('set-option','-t',session,'@bezalel-log-dir',str(log_dir))
        tmux('set-option','-w','-t',session+':codex','remain-on-exit','on')
        tmux('new-window','-t',session,'-n','claude','-c',str(cwd),shlex.join(clean+commands['claude']))
        tmux('set-option','-w','-t',session+':claude','remain-on-exit','on')
        for window in ('codex','claude'):
            tmux('set-option','-t',session,'@bezalel-executable-'+window,commands[window][0])
    for window in ('codex','claude'):
        log=log_dir/f'{session}-{window}.log'
        require(not log.is_symlink(),'Log não pode ser symlink.')
        fd=os.open(log,os.O_CREAT|os.O_APPEND|os.O_WRONLY|os.O_NOFOLLOW,0o600)
        os.fchmod(fd,0o600)
        os.close(fd)
        tmux('set-option','-t',session,'@bezalel-log-'+window,str(log))
        target=session+':'+window
        # pipe-pane -o também fecha o pipe anterior quando usado como toggle.
        # Idempotência precisa consultar pane_pipe antes de chamar novamente.
        if tmux('display-message','-p','-t',target,'#{pane_pipe}').stdout.strip()!='1':
            tmux('pipe-pane','-o','-t',target,'cat >> '+shlex.quote(str(log)))
    return hint(session)


def main():
    parser=ContractParser(description=__doc__)
    parser.add_argument('command',choices=['create','send','capture','hint','logs','destroy','status'])
    parser.add_argument('--project-name')
    parser.add_argument('--issue',type=int)
    parser.add_argument('--cwd',type=Path)
    parser.add_argument('--branch')
    parser.add_argument('--log-dir')
    parser.add_argument('--session')
    parser.add_argument('--window',choices=['codex','claude'])
    parser.add_argument('--text-file',type=Path)
    args=parser.parse_args()
    try:
        require(shutil.which('tmux'),'tmux ausente; instale manualmente antes de usar.')
        if args.command=='create':
            output=create(args)
        else:
            session=valid_name(args.session)
            if args.command=='hint':
                output=hint(session)
            elif args.command=='status':
                output=json.dumps(status(session),ensure_ascii=False)
            else:
                state=status(session)
                require(state['exists'],'Sessão ausente.')
                if args.command=='destroy':
                    tmux('kill-session','-t','='+session)
                    output='Sessão encerrada; logs e ambiente preservados.'
                else:
                    values=pane(session,args.window)
                    require(cli_alive(session,args.window,values[1]),'CLI não está em primeiro plano; não enviaremos texto ao shell.')
                    target=session+':'+args.window
                    if args.command=='send':
                        require(args.text_file and not args.text_file.is_symlink(),'Informe arquivo de texto real.')
                        content=args.text_file.read_text(encoding='utf-8')
                        require(content and not any(ord(c)<32 and c not in '\n\t' for c in content),'Prompt deve conter somente texto, sem controles de terminal.')
                        # load-buffer/paste-buffer evita interpretar $(), ``, - ou teclas.
                        buffer='bezalel-'+session+'-'+args.window
                        tmux('load-buffer','-b',buffer,str(args.text_file.resolve()))
                        tmux('paste-buffer','-p','-d','-b',buffer,'-t',target)
                        tmux('send-keys','-t',target,'Enter')
                        output='Prompt enviado.'
                    elif args.command=='capture':
                        output=tmux('capture-pane','-p','-J','-t',target).stdout.rstrip('\n')
                    else:
                        output=next(w['log'] for w in state['windows'] if w['name']==args.window)
        print(output)
        return 0
    except (ContractError,OSError,ValueError,TypeError,StopIteration) as error:
        print(str(error) if isinstance(error,ContractError) else 'Sessão não pôde concluir a operação; conteúdo privado omitido.',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
