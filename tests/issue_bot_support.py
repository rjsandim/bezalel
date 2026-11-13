"""Dublês de `gh` e `tmux` para os testes do modo issue-bot; nada acessa rede ou terminal real."""
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/issue-bot'

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
path = Path(os.environ['FAKE_GH_STATE'])
state = json.loads(path.read_text())
args = sys.argv[1:]
state['calls'].append(args)
def done(code=0, out=None, err=''):
    path.write_text(json.dumps(state))
    if out is not None:
        print(out if isinstance(out, str) else json.dumps(out))
    if err:
        print(err, file=sys.stderr)
    sys.exit(code)
if args[:2] == ['pr', 'checks']:
    if state.get('checks_sequence') and '--required' not in args:
        state['checks'] = state['checks_sequence'].pop(0)
    if '--required' in args:
        required = state.get('required')
        if not required:
            done(1, None, 'no required checks reported on the branch')
        done(0, required)
    if not state.get('checks'):
        done(1, None, "no checks reported on the 'issue-122' branch")
    done(0, state['checks'])
if args[:2] == ['pr', 'view']:
    done(0, {'headRefOid': state.get('sha', 'abc1234'), 'url': 'https://github.com/exemplo/projeto/pull/' + args[2],
             'number': int(args[2]), 'headRefName': state.get('head', 'issue-122'), 'baseRefName': 'main'})
if args[:2] == ['pr', 'list']:
    done(0, state.get('prs', []))
if args[:2] == ['issue', 'view']:
    done(0, state['issue'])
if args[:2] in (['pr', 'merge'], ['pr', 'review']):
    done(99, None, 'operação proibida no dublê')
done(98, None, 'chamada inesperada: ' + ' '.join(args))
'''

FAKE_TMUX = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
path = Path(os.environ['FAKE_TMUX_STATE'])
state = json.loads(path.read_text())
args = sys.argv[1:]
state['calls'].append(args)
sessions = state['sessions']
def done(code=0, out=None):
    path.write_text(json.dumps(state))
    if out is not None:
        print(out)
    sys.exit(code)
def opt(flag):
    return args[args.index(flag) + 1] if flag in args else None
def target():
    t = opt('-t') or ''
    session, _, window = t.partition(':')
    return session.lstrip('='), window
cmd = args[0]
if cmd == 'has-session':
    done(0 if target()[0] in sessions else 1)
if cmd == 'new-session':
    name = opt('-s')
    sessions[name] = {'options': {}, 'windows': {opt('-n'): {'cwd': opt('-c'), 'command': 'zsh', 'pane': [], 'pipe': None}}}
    done()
if cmd == 'load-buffer':
    state['buffer'] = Path(args[-1]).read_text()
    done()
s, w = target()
if s not in sessions:
    done(1)
session = sessions[s]
if cmd == 'new-window':
    session['windows'][opt('-n')] = {'cwd': opt('-c'), 'command': 'zsh', 'pane': [], 'pipe': None}
    done()
if cmd == 'list-windows':
    done(0, '\n'.join(session['windows']))
if cmd == 'display-message':
    window = session['windows'].get(w)
    if window is None:
        done(1)
    fmt = args[-1]
    done(0, fmt.replace('#{pane_current_command}', window['command']).replace('#{pane_dead}', '0')
         .replace('#{pane_current_path}', window['cwd'] or '').replace('#{pane_pipe}', '1' if window['pipe'] else '0'))
if cmd == 'set-option':
    session['options'][args[-2]] = args[-1]
    done()
if cmd == 'show-options':
    value = session['options'].get(args[-1])
    done(0 if value is not None else 1, value)
window = session['windows'].get(w)
if cmd == 'pipe-pane':
    window['pipe'] = args[-1]
    done()
if cmd == 'send-keys':
    text = args[args.index('-t') + 2:]
    if '-l' in args:
        text = args[args.index('-l') + 1:]
        window['pane'].append(' '.join(text))
        window['command'] = w  # o dublê trata o texto literal como o comando que inicia o CLI
    done()
if cmd == 'paste-buffer':
    window['pane'].append(state.pop('buffer', ''))
    # Simula o agente gravando o handoff depois de receber o prompt.
    hook = state.get('on_paste', {}).pop(w, None)
    if hook:
        Path(hook['path']).parent.mkdir(parents=True, exist_ok=True)
        Path(hook['path']).write_text(hook['content'])
    done()
if cmd == 'capture-pane':
    done(0, '\n'.join(window['pane']))
if cmd == 'kill-session':
    del sessions[s]
    done()
done(97)
'''


def load(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install(bindir, name, source):
    bindir.mkdir(parents=True, exist_ok=True)
    path = bindir / name
    path.write_text(source)
    path.chmod(0o755)
    return path


def fake_environment(base, gh_state=None, tmux_state=None):
    """Cria PATH com dublês e devolve o ambiente; estados ficam em arquivos JSON."""
    bindir = base / 'bin'
    env = {k: v for k, v in os.environ.items()}
    if gh_state is not None:
        install(bindir, 'gh', FAKE_GH)
        (base / 'gh.json').write_text(json.dumps({'calls': [], **gh_state}))
        env['FAKE_GH_STATE'] = str(base / 'gh.json')
    if tmux_state is not None:
        install(bindir, 'tmux', FAKE_TMUX)
        (base / 'tmux.json').write_text(json.dumps({'calls': [], 'sessions': {}, **tmux_state}))
        env['FAKE_TMUX_STATE'] = str(base / 'tmux.json')
    env['PATH'] = str(bindir) + os.pathsep + env['PATH']
    return env


def check(name, bucket):
    return {'name': name, 'bucket': bucket, 'state': bucket.upper(), 'workflow': 'CI',
            'link': 'https://github.com/exemplo/projeto/actions/runs/1'}
