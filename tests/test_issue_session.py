"""Sessão com tmux/CLIs simulados; nenhuma conta ou sessão do operador é usada."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import issue_session as session
from check_delivery import ContractError


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.cwd=self.root/'.worktrees/issue-122'; self.cwd.mkdir(parents=True)
        self.processes={}; self.options={}; self.exists=False; self.calls=[]; self.content={}; self.buffer=''; self.pipes=set()
        self.patchers=[patch.object(session,'tmux',side_effect=self.tmux),
                       patch.object(session,'project_paths',return_value=(self.root,self.cwd)),
                       patch.object(session,'cli_commands',return_value={'codex':['codex'],'claude':['claude']}),
                       patch.object(session.shutil,'which',return_value='/fixture/tmux')]
        for p in self.patchers: p.start(); self.addCleanup(p.stop)
        self.args=argparse.Namespace(cwd=self.cwd,issue=122,project_name='Projeto Fixture',branch=None,log_dir=None)

    def tmux(self,*args,allowed=(0,)):
        self.calls.append(args); command=args[0]; out=''; code=0
        if command=='has-session': code=0 if self.exists else 1
        elif command=='new-session': self.exists=True
        elif command=='set-option': self.options[args[-2]]=args[-1]
        elif command=='show-options': out=self.options.get(args[-1],'')
        elif command=='list-windows': out='codex\nclaude\n'
        elif command=='display-message':
            target=args[args.index('-t')+1]; name=target.split(':')[-1]
            if args[-1]=='#{pane_pipe}': out='1' if target in self.pipes else '0'
            else:
                out=f'0\t{self.processes.get(name,name)}\t{self.cwd}'
                if '#{pane_pipe}' in args[-1]: out+='\t1'
        elif command=='pipe-pane': self.pipes.add(args[args.index('-t')+1])
        elif command=='load-buffer': self.buffer=Path(args[-1]).read_text()
        elif command=='paste-buffer': self.content[args[-1]]=self.buffer
        elif command=='capture-pane': out=self.content.get(args[-1],'')
        elif command=='kill-session': self.exists=False
        return subprocess.CompletedProcess(args,code,out,'')

    def main(self,*args):
        output=io.StringIO()
        with patch.object(sys,'argv',['issue_session.py',*args]),contextlib.redirect_stdout(output),contextlib.redirect_stderr(io.StringIO()):
            result=session.main()
        return result,output.getvalue()

    def test_create_is_idempotent_and_logs_append(self):
        hint=session.create(self.args)
        self.assertIn('tmux attach -t projeto-fixture-122',hint)
        log=self.root/'.bezalel/logs/projeto-fixture-122-codex.log'; log.write_text('preserve\n')
        before=sum(c[0]=='new-session' for c in self.calls)
        pipes_before=sum(c[0]=='pipe-pane' for c in self.calls)
        session.create(self.args)
        self.assertEqual(log.read_text(),'preserve\n')
        self.assertEqual(sum(c[0]=='new-session' for c in self.calls),before)
        self.assertEqual(sum(c[0]=='pipe-pane' for c in self.calls),pipes_before)
        self.assertTrue(any(c[0]=='pipe-pane' and '-o' in c for c in self.calls))
        self.assertIn('Ctrl+b',hint)

    def test_send_is_literal_and_capture_reads_the_pane(self):
        session.create(self.args)
        prompt=self.root/'prompt.md'; prompt.write_text('Texto\n$(touch bad) `id` --no-shell')
        self.assertEqual(self.main('send','--session','projeto-fixture-122','--window','codex','--text-file',str(prompt))[0],0)
        code,output=self.main('capture','--session','projeto-fixture-122','--window','codex')
        self.assertEqual(code,0); self.assertEqual(output.strip(),prompt.read_text())
        self.assertFalse((self.root/'bad').exists())
        self.assertIn(('send-keys','-t','projeto-fixture-122:codex','Enter'),self.calls)

    def test_destroy_preserves_log_and_status_is_json(self):
        session.create(self.args)
        code,value=self.main('status','--session','projeto-fixture-122')
        self.assertEqual(code,0); self.assertEqual(len(json.loads(value)['windows']),2)
        code,_=self.main('destroy','--session','projeto-fixture-122')
        self.assertEqual(code,0); self.assertFalse(self.exists)
        self.assertTrue((self.root/'.bezalel/logs/projeto-fixture-122-codex.log').is_file())

    def test_invalid_name_and_log_path_are_rejected(self):
        for name in ['foo/bar','../foo','bad_name','x;id','-x']:
            with self.assertRaises(ContractError): session.valid_name(name)
        self.args.log_dir=str(self.cwd/'logs')
        with self.assertRaises(ContractError): session.create(self.args)

    def test_unmanaged_session_is_never_adopted(self):
        self.exists=True
        with self.assertRaises(ContractError): session.create(self.args)

    def test_versioned_native_binary_is_alive_but_unrelated_process_is_not(self):
        session.create(self.args)
        self.options['@bezalel-executable-claude']='/fixture/versions/2.1.316'
        self.processes['claude']='2.1.316'
        self.assertTrue(session.status('projeto-fixture-122')['windows'][1]['alive'])
        prompt=self.root/'prompt'; prompt.write_text('fixture')
        self.assertEqual(self.main('send','--session','projeto-fixture-122','--window','claude','--text-file',str(prompt))[0],0)
        self.processes['claude']='python3'
        self.assertFalse(session.status('projeto-fixture-122')['windows'][1]['alive'])
        before=len([c for c in self.calls if c[0]=='load-buffer'])
        self.assertEqual(self.main('send','--session','projeto-fixture-122','--window','claude','--text-file',str(prompt))[0],1)
        self.assertEqual(len([c for c in self.calls if c[0]=='load-buffer']),before)

    def test_dead_or_shell_pane_does_not_receive_prompt(self):
        session.create(self.args)
        with patch.object(session,'pane',return_value=['0','bash',str(self.cwd),'1']):
            code,_=self.main('send','--session','projeto-fixture-122','--window','codex','--text-file',str(self.root/'unused'))
        self.assertEqual(code,1)
        self.assertFalse(any(c[0]=='load-buffer' for c in self.calls))


class AuthenticationTests(unittest.TestCase):
    def cli(self,api=False,auto_review=True):
        def result(args,**kw):
            if args==['codex','--help']:
                out=('--approve-for-me ' if auto_review else '')+'--sandbox --ask-for-approval --cd --no-alt-screen --no-daemon'
            elif args==['claude','--help']:
                out='--dangerously-skip-permissions --settings --setting-sources --strict-mcp-config --tools'
            elif args[:3]==['codex','login','status']: out='Logged in using API key' if api else 'Logged in using ChatGPT'
            else: out=json.dumps({'loggedIn':True,'authMethod':'apiKey' if api else 'claude.ai'})
            return subprocess.CompletedProcess(args,0,out,'')
        with patch.dict(os.environ,{},clear=True),patch.object(session,'run',side_effect=result),patch.object(session.shutil,'which',return_value='/fixture/bin'):
            return session.cli_commands(Path('/fixture/.worktrees/issue-122'),Path('/fixture'))

    def test_account_required_and_no_bypass_of_codex_sandbox(self):
        commands=self.cli()
        self.assertIn('--approve-for-me',commands['codex']); self.assertNotIn('never',commands['codex'])
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',commands['codex'])
        settings=json.loads(commands['claude'][-1])
        self.assertTrue(settings['sandbox']['failIfUnavailable'])
        self.assertFalse(settings['sandbox']['allowUnsandboxedCommands'])
        with self.assertRaises(ContractError): self.cli(True)
        with self.assertRaises(ContractError): self.cli(auto_review=False)

    def test_inherited_api_key_is_rejected_without_reading_login(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fixture-not-a-real-key'}),patch.object(session,'run') as run:
            with self.assertRaises(ContractError): session.cli_commands(Path('/fixture'),Path('/fixture'))
            run.assert_not_called()


@unittest.skipUnless(os.environ.get('BEZALEL_TMUX_SMOKE')=='1' and session.shutil.which('tmux'),
                     'Fumaça tmux isolada é opt-in; não usa CLIs de conta.')
class TmuxSmokeTests(unittest.TestCase):
    def test_private_socket_logs_and_literal_send_capture(self):
        import shutil
        import time
        with tempfile.TemporaryDirectory(prefix='bezalel-tmux-') as name:
            root=Path(name).resolve(); cwd=root/'.worktrees/issue-122'; cwd.mkdir(parents=True)
            socket=str(root/'tmux.sock')
            if not shutil.which('cc'): self.skipTest('Compilador nativo ausente; não instalar para o teste.')
            versioned=root/'versions/2.1.316'; versioned.parent.mkdir()
            source='#include <stdio.h>\nint main(void) { char line[4096]; while (fgets(line,sizeof(line),stdin)) { fputs(line,stdout); fflush(stdout); } return 0; }'
            subprocess.run(['cc','-x','c','-o',str(versioned),'-'],input=source,text=True,check=True,capture_output=True)
            alias=root/'claude'; alias.symlink_to(versioned)
            def tmux(*args,allowed=(0,)):
                return session.run(['tmux','-f','/dev/null','-S',socket,*args],allowed=allowed)
            args=argparse.Namespace(cwd=cwd,issue=122,project_name='fixture',branch=None,log_dir=None)
            try:
                with patch.object(session,'tmux',side_effect=tmux),patch.object(session,'project_paths',return_value=(root,cwd)),patch.object(session,'cli_commands',return_value={'codex':['/bin/cat'],'claude':[str(alias.resolve())]}):
                    session.create(args)
                    deadline=time.monotonic()+5
                    while not all(w['alive'] for w in session.status('fixture-122')['windows']):
                        self.assertLess(time.monotonic(),deadline); time.sleep(0.05)
                    self.assertEqual({w['cwd'] for w in session.status('fixture-122')['windows']},{str(cwd)})
                    session.create(args)
                    self.assertEqual(tmux('display-message','-p','-t','fixture-122:claude','#{pane_current_command}').stdout.strip(),'2.1.316')
                    text=root/'prompt.txt'; text.write_text('fixture literal $(no-shell)')
                    for window in ('codex','claude'):
                        with patch.object(sys,'argv',['issue_session.py','send','--session','fixture-122','--window',window,'--text-file',str(text)]),contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(session.main(),0)
                        captured=''
                        while 'fixture literal $(no-shell)' not in captured:
                            self.assertLess(time.monotonic(),deadline)
                            captured=tmux('capture-pane','-p','-J','-t','fixture-122:'+window).stdout
                            time.sleep(0.05)
                        log=root/f'.bezalel/logs/fixture-122-{window}.log'
                        while 'fixture literal' not in log.read_text():
                            self.assertLess(time.monotonic(),deadline); time.sleep(0.05)
                    tmux('kill-session','-t','=fixture-122')
                    self.assertTrue(log.exists())
                    self.assertIn('fixture literal',log.read_text())
            finally:
                subprocess.run(['tmux','-S',socket,'kill-server'],capture_output=True)
