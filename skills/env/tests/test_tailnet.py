"""Serve simulado: nenhum comando modifica a configuração real da máquina."""
import copy
import hashlib
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
import tailnet

FAKE = r'''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
path=Path(os.environ['TAILNET_FIXTURE'])
d=json.loads(path.read_text())
a=sys.argv[1:]
if os.environ.get('TAILNET_FAKE_FAIL')=='1': sys.exit(8)
d['calls'].append(a)
if a==['status','--json']:
    print(json.dumps({'BackendState':'Running','Self':{'DNSName':'fixture.ts.net.'}}))
elif a==['serve','status','--json']:
    print(json.dumps(d['serve']))
elif a[:3]==['serve','--bg','--yes'] and len(a)==5:
    p=int(a[3].split('=')[1]); assert 41000<=p<=41999
    address=f'fixture.ts.net:{p}'
    if a[4]=='off':
        del d['serve']['TCP'][str(p)]; del d['serve']['Web'][address]
    else:
        assert a[4]==f'http://127.0.0.1:{p}'
        d['serve']['TCP'][str(p)]={'HTTPS':True}
        d['serve']['Web'][address]={'Handlers':{'/':{'Proxy':a[4]}}}
else:
    sys.exit('Forbidden command')
path.write_text(json.dumps(d))
'''


def worker(root, project, name, service):
    tailnet.allocate(root, project, name, service)


def mutation_worker(root, name):
    tailnet.allocate(root, 'fixture', name, 'api')
    tailnet.mutate(root, 'fixture', name, 'api', 'publish')
    tailnet.mutate(root, 'fixture', 'other-owner', 'api', 'release')
    tailnet.mutate(root, 'fixture', name, 'api', 'release')



class TailnetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='tailnet-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.fixture=self.root/'tailscale.json'
        self.protected={'TCP':{'443':{'HTTPS':True}},'Web':{'fixture.ts.net:443':{'Handlers':{'/':{'Proxy':'http://127.0.0.1:8000'}}}}}
        self.fixture.write_text(json.dumps({'serve':self.protected,'calls':[]}))
        binary=self.root/'tailscale'
        binary.write_text(FAKE);binary.chmod(0o755)
        self.addCleanup(patch.stopall)
        patch.dict(os.environ,ENV_TAILNET_STATE_DIR=str(self.root/'global'),ENV_TAILSCALE_BIN=str(binary),TAILNET_FIXTURE=str(self.fixture),ENV_ALLOW_SHARED_INFRA='1').start()

    def allocate(self, service='api', **kwargs):
        return tailnet.allocate(self.root,'fixture','issue-21',service,**kwargs)

    def operate(self, action='publish', service='api'):
        return tailnet.mutate(self.root,'fixture','issue-21',service,action)

    def data(self): return json.loads(self.fixture.read_text())

    def test_idempotent_global_registry_across_copies_and_lifecycle(self):
        entry=self.allocate()
        self.assertEqual(entry,self.allocate())
        path=self.root/'global/registry.json'
        self.assertEqual(path.stat().st_mode & 0o777,0o600)
        self.operate();before=self.data()
        self.operate();after=self.data()
        self.assertEqual(len([c for c in before['calls'] if '--bg' in c]),len([c for c in after['calls'] if '--bg' in c]))
        # Lock global independe do SKILL_DIR da cópia carregada.
        script=self.root/'copy';script.mkdir()
        (script/'tailnet.py').write_bytes((SCRIPTS/'tailnet.py').read_bytes())
        result=subprocess.run([sys.executable,str(script/'tailnet.py'),'allocate','--root',str(self.root),'--project','fixture','--environment','issue-21','--service','api'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),entry)
        self.operate('release');self.operate('release')
        self.assertEqual(self.data()['serve'],self.protected)
        self.assertEqual(tailnet.entries(),[])
        self.assertFalse(any('reset' in c or 'funnel' in c or 'set-config' in c for c in self.data()['calls']))

    def test_multi_process_unique_and_same_identity(self):
        context=multiprocessing.get_context('fork')
        processes=[context.Process(target=worker,args=(self.root,'fixture',f'issue-{i}','api')) for i in range(20)]
        for p in processes:p.start()
        for p in processes:p.join(30);self.assertEqual(p.exitcode,0)
        entries=tailnet.entries()
        self.assertEqual(len(entries),20)
        self.assertEqual(len({e['port'] for e in entries}),20)
        processes=[context.Process(target=worker,args=(self.root,'fixture','same','api')) for _ in range(8)]
        for p in processes:p.start()
        for p in processes:p.join(30);self.assertEqual(p.exitcode,0)
        self.assertEqual(len(tailnet.entries()),21)

    def test_skips_registry_serve_and_listener_and_exhaustion(self):
        key=tailnet.identity(self.root,'fixture','issue-21','api')
        first=41000+int(hashlib.sha256(key.encode()).hexdigest(),16)%3
        following=41000+(first-41000+1)%3
        data=self.data()
        data['serve']['TCP'][str(first)]={'TCPForward':'elsewhere:80'}
        self.fixture.write_text(json.dumps(data))
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',following));listener.listen()
            entry=self.allocate(start=41000,end=41002)
            self.assertNotIn(entry['port'],(first,following))
            with self.assertRaises(tailnet.TailnetError):self.allocate('web',start=41000,end=41002)

    def test_foreign_target_extra_handler_tcp_and_funnel_refused(self):
        entry=self.allocate();self.operate()
        original=self.data()
        changes=[lambda c:c['Web'][f'fixture.ts.net:{entry["port"]}']['Handlers']['/'].update(Proxy='http://127.0.0.1:9000'),
                 lambda c:c['Web'][f'fixture.ts.net:{entry["port"]}']['Handlers'].update({'/other':{'Text':'keep'}}),
                 lambda c:c['TCP'][str(entry['port'])].update(TCPForward='elsewhere:90'),
                 lambda c:c.update(AllowFunnel={f'fixture.ts.net:{entry["port"]}':True})]
        for change in changes:
            data=copy.deepcopy(original);change(data['serve']);self.fixture.write_text(json.dumps(data))
            before=(self.root/'global/registry.json').read_bytes()
            for action in ('publish','release'):
                with self.assertRaises(tailnet.TailnetError):self.operate(action)
            self.assertEqual(self.data()['serve'],data['serve'])
            self.assertEqual((self.root/'global/registry.json').read_bytes(),before)

    def test_never_releases_someone_elses_environment(self):
        entry=self.allocate();self.operate()
        tailnet.mutate(self.root,'fixture','other','api','release')
        self.assertIn(str(entry['port']),self.data()['serve']['TCP'])
        for p in (0,80,443,65536):
            with self.assertRaises(tailnet.TailnetError):tailnet.safe_port(p)

    def test_status_returns_iphone_url_checks_and_not_ready_on_serve_drift(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('env_status_fixture',SCRIPTS/'status.py')
        status_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(status_module)
        entry={**self.allocate(),'container_port':8000,'probe_path':'/health','probe_statuses':[200,401,404]};self.operate()
        state=self.root/'status';state.mkdir()
        (state/'worktree-branch').write_text('issue-21')
        tailnet.atomic_json(state/'tailnet.json',{'host':entry['host'],'primary':'api','services':[entry]})
        config={'services':{'api':{'depends_on':{}},'postgres':{}},'x-envstack':{'startup_services':['api']}}
        def query(args):
            if args[0]=='yq':return json.dumps({'project':'fixture','access':'tailnet','services':[{'folder':'api','port':8000}]})
            if 'config' in args:return json.dumps(config)
            return json.dumps([{'Service':'api','State':'running','Health':'healthy'}])
        with patch.object(status_module,'query',side_effect=query),patch.object(tailnet,'request',return_value=(200,[],'ok')):
            result=status_module.status(self.root,state,'issue-21','fixture')
            self.assertEqual(result['iphone_url'],entry['url']);self.assertTrue(result['ready'])
            self.assertEqual(result['services'][0]['url'],entry['url'])
            self.assertEqual(result['tailnet']['services'][0]['http_code'],200)
            for code in (401,404):
                with patch.object(tailnet,'request',return_value=(code,[],'')) as request:
                    result=status_module.status(self.root,state,'issue-21','fixture')
                    self.assertTrue(result['ready'])
                    self.assertTrue(request.call_args.args[0].endswith('/health'))
            self.operate('release')
            result=status_module.status(self.root,state,'issue-21','fixture')
            self.assertFalse(result['ready'])
            self.assertFalse(result['tailnet']['services'][0]['serve_ok'])

    def test_only_tailnet_removes_proxy_but_preserves_shared_pool_networks(self):
        compose=self.root/'compose.yml';compose.write_text('placeholder')
        config={'networks':{'internal':{},'proxy':{'external':True},'shared-database':{'external':True},'shared-redis':{'external':True}},
                'services':{'api':{'networks':['internal','proxy','shared-database','shared-redis'],'labels':['traefik.enable=true']},
                            'web':{'networks':{'internal':{},'proxy':{},'shared-redis':{'aliases':['cache']}}}}}
        completed=subprocess.CompletedProcess([],0,json.dumps(config),'')
        with patch.object(tailnet,'manifest',return_value={'access':'tailnet'}),patch.object(tailnet.subprocess,'run',return_value=completed):
            tailnet.configure(self.root,compose)
        result=json.loads(compose.read_text())
        self.assertEqual(result['services']['api']['networks'],['internal','shared-database','shared-redis'])
        self.assertEqual(result['services']['web']['networks'],{'internal':{},'shared-redis':{'aliases':['cache']}})
        self.assertNotIn('proxy',result['networks'])
        self.assertTrue(result['networks']['shared-database']['external'])

    def test_publish_requires_exact_compose_loopback_binding(self):
        entry={**self.allocate(),'container_port':8000}
        state=self.root/'saved';state.mkdir()
        tailnet.atomic_json(state/'tailnet.json',{'host':entry['host'],'primary':'api','services':[entry]})
        config={'services':{'api':{'ports':[{'published':str(entry['port']),'target':8000,'host_ip':'0.0.0.0'}]}}}
        with patch.object(tailnet,'compose_config',return_value=config):
            with self.assertRaises(tailnet.TailnetError):tailnet.lifecycle(state,'publish',['api'])
        self.assertEqual(self.data()['serve'],self.protected)
        config['services']['api']['ports'][0]['host_ip']='127.0.0.1'
        with patch.object(tailnet,'compose_config',return_value=config):tailnet.lifecycle(state,'publish',['api'])
        self.assertTrue(tailnet.own_mapping(self.data()['serve'],entry['host'],entry['port']))

    def test_missing_authorization_or_failed_tool_keeps_registry(self):
        self.allocate()
        with patch.dict(os.environ,ENV_ALLOW_SHARED_INFRA='0'):
            with self.assertRaises(tailnet.TailnetError):self.operate()
        with patch.dict(os.environ,ENV_TAILSCALE_BIN='/no-such-command'):
            with self.assertRaises(OSError):self.operate()
        self.assertEqual(len(tailnet.entries()),1)

    def test_check_paths_upgrade_redirect_cookie_scan_and_env_warnings(self):
        entry=self.allocate()
        with patch.object(tailnet,'request',return_value=(101,[('Upgrade','websocket')],'')):
            self.assertTrue(tailnet.probe(entry,'websocket','/ws')['ok'])
        with patch.object(tailnet,'request',return_value=(200,[],'')):
            self.assertFalse(tailnet.probe(entry,'websocket','/ws')['ok'])
            self.assertTrue(tailnet.probe(entry,'static','/assets/app.js')['ok'])
            self.assertTrue(tailnet.probe(entry,'api','/api/health')['ok'])
        with patch.object(tailnet,'request',return_value=(302,[('Location','/login'),('Set-Cookie','sid=private; Secure; HttpOnly; SameSite=Lax')],'')):
            self.assertTrue(tailnet.probe(entry,'redirect','/private')['ok'])
        with patch.object(tailnet,'request',return_value=(302,[('Location','http://localhost:3000/login'),('Set-Cookie','sid=private; Domain=fixture.local')],'')):
            result=tailnet.probe(entry,'redirect','/private')
            self.assertFalse(result['ok']);self.assertNotIn('private',json.dumps(result['warnings']))
        with patch.object(tailnet,'request',return_value=(200,[],"fetch('https://api.fixture.local/data')")):
            self.assertFalse(tailnet.probe(entry,'page','/')['ok'])
        with self.assertRaises(tailnet.TailnetError):tailnet.probe(entry,'api','https://elsewhere.invalid/')
        path=self.root/'api';path.mkdir();(path/'.env').write_text('APP_URL=http://localhost:3000\nDB_HOST=mysql\nTOKEN=private\nCORS_ORIGINS=https://a.fixture.local\n')
        warnings=tailnet.env_warnings(self.root,[entry])
        self.assertEqual([w['variable'] for w in warnings],['APP_URL','CORS_ORIGINS'])
        self.assertNotIn('private',json.dumps(warnings))

    def test_full_check_marks_unconfigured_cases_and_serve_down(self):
        state=self.root/'state';state.mkdir()
        entry=self.allocate();self.operate()
        tailnet.atomic_json(state/'tailnet.json',{'host':entry['host'],'primary':'api','services':[{**entry,'checks':{'static':'/app.js','redirect':'/private','health':'/health','websocket':'/ws'}}]})
        def response(url,websocket=False):
            if websocket:return (101,[('Upgrade','websocket')],'')
            return (302,[('Location','/login')],'') if url.endswith('/private') else (200,[],'ok')
        with patch.object(tailnet,'request',side_effect=response):
            result=tailnet.report(self.root,state,'issue-21',True)
            self.assertTrue(result['services'][0]['serve_ok'])
            self.assertIn({'kind':'login','status':'not_configured','ok':None},result['services'][0]['checks'])
        self.operate('release')
        with patch.object(tailnet,'request') as request:
            result=tailnet.report(self.root,state,'issue-21')
            self.assertFalse(result['services'][0]['serve_ok']);request.assert_not_called()

    def test_multiprocess_publish_release_preserves_foreign_and_primary(self):
        foreign=self.allocate('foreign');self.operate(service='foreign')
        context=multiprocessing.get_context('fork')
        processes=[context.Process(target=mutation_worker,args=(self.root,f'parallel-{i}')) for i in range(12)]
        for process in processes:process.start()
        for process in processes:
            process.join(30);self.assertEqual(process.exitcode,0)
        self.assertEqual(tailnet.entries(),[foreign])
        config=self.data()['serve']
        self.assertEqual(config['TCP']['443'],self.protected['TCP']['443'])
        self.assertEqual(config['Web']['fixture.ts.net:443'],self.protected['Web']['fixture.ts.net:443'])
        self.assertTrue(tailnet.own_mapping(config,foreign['host'],foreign['port']))

    def test_local_scan_adversarial_megabyte_is_bounded(self):
        adversarial='a.'*(1024*512)
        started=time.monotonic()
        self.assertIsNone(tailnet.LOCAL.search(adversarial))
        self.assertIsNotNone(tailnet.LOCAL.search(adversarial+'local/'))
        self.assertLess(time.monotonic()-started,2.0)

    def test_internal_hosts_do_not_break_public_url_check(self):
        entry=self.allocate();directory=self.root/'api';directory.mkdir()
        (directory/'.env').write_text('DB_HOST=localhost\nREDIS_HOST=127.0.0.1\nMAIL_HOST=localhost\nSMTP_HOST=localhost\nDB_URL=mysql://localhost/database\nAPP_HOST=localhost\nAPP_URL=http://localhost\nNEXT_PUBLIC_API_URL=https://api.fixture.local\n')
        self.assertEqual([w['variable'] for w in tailnet.env_warnings(self.root,[entry])],['APP_HOST','APP_URL','NEXT_PUBLIC_API_URL'])

    def test_probe_path_statuses_and_short_transport_retry(self):
        entry={**self.allocate(),'probe_path':'/health','probe_statuses':[200,401,403,404]}
        for code in (401,403,404):
            with patch.object(tailnet,'request',return_value=(code,[],'')) as request:
                self.assertTrue(tailnet.page_probe(entry)['ok'])
                self.assertTrue(request.call_args.args[0].endswith('/health'))
        with patch.object(tailnet,'request',side_effect=[OSError(),(401,[], '')]) as request:
            self.assertTrue(tailnet.page_probe(entry)['ok']);self.assertEqual(request.call_count,2)
        with patch.object(tailnet,'request',return_value=(500,[],'')) as request:
            self.assertFalse(tailnet.page_probe(entry)['ok']);self.assertEqual(request.call_count,1)

    def test_prune_requires_absent_worktree_state_and_docker(self):
        state=self.root/'skill/state/fixture/issue-21';state.mkdir(parents=True)
        with patch.dict(os.environ,DOCKER_CONTEXT='fixture'):
            entry=self.allocate(owner=state)
        self.operate()
        original=self.data()['serve']
        with patch.object(tailnet.subprocess,'run') as command:
            result=tailnet.prune(self.root,'fixture','issue-21')
            self.assertEqual(result['released'],[]);command.assert_not_called()
        state.rmdir()
        worktree=self.root/'.worktrees/issue-21';worktree.mkdir(parents=True)
        with patch.object(tailnet.subprocess,'run') as command:
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],[]);command.assert_not_called()
        worktree.rmdir()
        real_run=tailnet.subprocess.run
        def query(args,**kwargs):
            if args[0]=='docker':
                self.assertIn('--context',args);self.assertIn('com.docker.compose.project=fixture-issue-21',args[-1])
                return subprocess.CompletedProcess(args,0,'some-container','')
            return real_run(args,**kwargs)
        with patch.object(tailnet.subprocess,'run',side_effect=query):
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],[])
        self.assertEqual(self.data()['serve'],original)
        def absent(args,**kwargs):
            return subprocess.CompletedProcess(args,0,'','') if args[0]=='docker' else real_run(args,**kwargs)
        with patch.object(tailnet.subprocess,'run',side_effect=absent):
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],['api'])
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],[])
        self.assertEqual(self.data()['serve'],self.protected)

    def test_prune_preserves_unknown_provenance_foreign_mapping_and_failed_docker(self):
        self.allocate()
        with patch.object(tailnet.subprocess,'run') as run:
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],[]);run.assert_not_called()
        self.operate('release')
        state=self.root/'skill/state/fixture/issue-21';state.mkdir(parents=True);state.rmdir()
        with patch.dict(os.environ,DOCKER_CONTEXT='fixture'):entry=self.allocate(owner=state)
        with patch.object(tailnet.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','')):
            with self.assertRaises(tailnet.TailnetError):tailnet.prune(self.root,'fixture','issue-21')
        data=self.data();data['serve']['TCP'][str(entry['port'])]={'TCPForward':'foreign:80'};self.fixture.write_text(json.dumps(data))
        real_run=tailnet.subprocess.run
        def absent(args,**kwargs):
            return subprocess.CompletedProcess(args,0,'','') if args[0]=='docker' else real_run(args,**kwargs)
        with patch.object(tailnet.subprocess,'run',side_effect=absent):
            self.assertEqual(tailnet.prune(self.root,'fixture','issue-21')['released'],[])
        self.assertEqual(len(tailnet.entries()),1);self.assertEqual(self.data()['serve'],data['serve'])

    def test_missing_proof_preserves_inaccessible_paths(self):
        with patch.object(Path,'lstat',side_effect=PermissionError()):
            self.assertFalse(tailnet.confirmed_missing(self.root/'unknown'))
        with patch.object(Path,'lstat',side_effect=FileNotFoundError()):
            self.assertTrue(tailnet.confirmed_missing(self.root/'absent'))

    def test_completed_attempt_cannot_rollback_an_adopted_reservation(self):
        state=self.root/'attempt-state';state.mkdir()
        receipt=state/'attempt.json'
        config={'project':'fixture','access':'tailnet','tailnet':{'primary':'api'},'services':[{'folder':'api','port':8000,'tailnet':{'probe_path':'/health','probe_statuses':[200,401,404]}}]}
        with patch.dict(os.environ,DOCKER_CONTEXT='fixture'),patch.object(tailnet,'manifest',return_value=config):
            tailnet.prepare(self.root,state,'issue-21',receipt)
        saved=json.loads((state/'tailnet.json').read_text())
        self.assertEqual(saved['services'][0]['probe_path'],'/health')
        self.assertEqual(saved['services'][0]['probe_statuses'],[200,401,404])
        tailnet.complete_attempt(state,receipt)
        self.assertNotIn('attempt_id',tailnet.entries()[0])
        tailnet.rollback(state,receipt)
        self.assertEqual(len(tailnet.entries()),1)
        self.assertEqual(json.loads((state/'tailnet.json').read_text()),saved)

    def test_corrupt_registry_and_symlinks_fail_closed(self):
        self.allocate();path=self.root/'global/registry.json'
        before=self.data()['serve'];path.write_text('{}')
        with self.assertRaises(tailnet.TailnetError):self.allocate()
        self.assertEqual(self.data()['serve'],before)
        path.unlink();outside=self.root/'outside';outside.write_text('{}');path.symlink_to(outside)
        with self.assertRaises(tailnet.TailnetError):self.allocate()
        self.assertEqual(outside.read_text(),'{}')



class TailnetLifecycleTests(unittest.TestCase):
    # Reutiliza somente preparação/driver; não duplica os testes legados.
    from test_lifecycle import LifecycleTests as Driver
    setUp = Driver.setUp
    command = Driver.command
    run_process = Driver.run_process
    observed = Driver.observed

    def configure_tailnet(self):
        manifest=self.repo/'.envstack/stack.yaml'
        manifest.write_text(manifest.read_text()+'''\naccess: tailnet
tailnet:
  primary: api
  services: [site]
''')
        fixture=self.base/'tailscale.json'
        fixture.write_text(json.dumps({'serve':{'TCP':{'443':{'HTTPS':True}},'Web':{'fixture.ts.net:443':{'Handlers':{'/':{'Proxy':'http://127.0.0.1:8000'}}}}},'calls':[]}))
        binary=self.base/'bin/tailscale';binary.write_text(FAKE);binary.chmod(0o755)
        self.env.update(ENV_TAILNET_STATE_DIR=str(self.base/'global-tailnet'),ENV_TAILSCALE_BIN=str(binary),TAILNET_FIXTURE=str(fixture))
        return fixture

    def test_only_tailnet_compose_placeholders_and_preservation(self):
        fixture=self.configure_tailnet()
        for folder in ('api','site'):
            (self.worktree/folder/'.env').unlink()
            (self.repo/f'.envstack/{folder}.env.example').write_text('APP_URL=${env:public.url.self}\nPEER=${env:public.url.api}\nTAIL=${env:tailnet.url.site}\nHOST=${env:public.host.self}\nTSHOST=${env:tailnet.host}\n')
        self.command('update.sh','check',extra={'ENV_DRY_RUN':'1'})
        config=json.loads(self.run_process([os.environ.get('ENV_TEST_DOCKER') or __import__('test_lifecycle').DOCKER,'compose','-f',str(self.compose),'config','--format','json']).stdout)
        self.assertNotIn('proxy',config['networks'])
        self.assertEqual(config['services']['mysql']['ports'][0]['host_ip'],'127.0.0.1')
        for folder in ('api','site'):
            service=config['services'][folder]
            self.assertNotIn('labels',service)
            self.assertNotIn('proxy',service['networks'])
            self.assertEqual(service['ports'][0]['host_ip'],'127.0.0.1')
            self.assertTrue(41000<=int(service['ports'][0]['published'])<=41999)
            env=(self.worktree/folder/'.env').read_text()
            self.assertIn('https://fixture.ts.net:',env)
            self.assertIn('HOST=fixture.ts.net',env)
            self.assertNotIn('${env:',env)
        env=(self.worktree/'api/.env');before=env.read_bytes()
        self.command('ctl.sh','start','check')
        self.assertFalse(any(c[0]=='start' for c in self.observed()['calls']))
        self.assertNotEqual(json.loads(fixture.read_text())['serve']['TCP'],{'443':{'HTTPS':True}})
        registry=(self.base/'global-tailnet/registry.json').read_bytes()
        self.command('ctl.sh','stop','check')
        self.assertEqual((self.base/'global-tailnet/registry.json').read_bytes(),registry)
        self.command('ctl.sh','ensure','check','site')
        self.assertEqual(env.read_bytes(),before)
        self.command('destroy.sh','check','--confirm','fixture/check','--keep-worktree')
        self.assertEqual(json.loads((self.base/'global-tailnet/registry.json').read_text())['entries'],{})
        self.assertEqual(json.loads(fixture.read_text())['serve']['TCP'],{'443':{'HTTPS':True}})
        self.assertEqual(env.read_bytes(),before)

    def test_tailnet_failed_publish_propagates_and_confirmation_precedes_release(self):
        fixture=self.configure_tailnet()
        self.command('update.sh','check',extra={'ENV_DRY_RUN':'1'})
        metadata=json.loads((self.compose.parent/'tailnet.json').read_text())
        port=metadata['services'][0]['port'];data=json.loads(fixture.read_text())
        data['serve']['TCP'][str(port)]={'TCPForward':'someone:9999'}
        fixture.write_text(json.dumps(data))
        self.command('ctl.sh','start','check',expected=1)
        self.command('destroy.sh','check','--keep-worktree',expected=1)
        result=self.command('destroy.sh','check','--confirm','fixture/check','--keep-worktree')
        self.assertFalse(self.compose.exists())
        self.assertTrue(any('down' in c for c in self.observed()['calls']))
        self.assertIn('reserva Tailnet preservada',result.stderr)
        self.assertTrue(json.loads((self.base/'global-tailnet/registry.json').read_text())['entries'])
        self.assertEqual(json.loads(fixture.read_text())['serve'],data['serve'])

    def test_failed_new_releases_only_new_reservations_and_can_retry(self):
        fixture=self.configure_tailnet()
        # Usa new real com Docker simulado; falha antes do up, após alocar.
        (self.repo/'.envstack/api.env.example').write_text('APP_URL=${env:public.url.docs}\n')
        self.command('new.sh','broken',extra={'ENV_DRY_RUN':'1'},expected=1)
        registry=self.base/'global-tailnet/registry.json'
        self.assertEqual(json.loads(registry.read_text())['entries'],{})
        self.assertFalse((self.skill/'state/fixture/broken/tailnet.json').exists())
        self.assertEqual(json.loads(fixture.read_text())['serve']['TCP'],{'443':{'HTTPS':True}})
        (self.repo/'.envstack/api.env.example').write_text('APP_URL=${env:public.url.self}\n')
        self.command('new.sh','broken',extra={'ENV_DRY_RUN':'1'})
        self.assertEqual(len(json.loads(registry.read_text())['entries']),2)
        # Falha posterior não devolve reservas preexistentes desta geração.
        self.command('update.sh','broken',extra={'ENV_TEST_FAIL_UP':'1'},expected=7)
        self.assertEqual(len(json.loads(registry.read_text())['entries']),2)

    def test_destroy_with_unavailable_tailscale_still_runs_down(self):
        self.configure_tailnet();self.command('update.sh','check',extra={'ENV_DRY_RUN':'1'})
        result=self.command('destroy.sh','check','--confirm','fixture/check','--keep-worktree',extra={'TAILNET_FAKE_FAIL':'1'})
        self.assertIn('release --root',result.stderr)
        self.assertTrue(any('down' in c for c in self.observed()['calls']))
        self.assertTrue(json.loads((self.base/'global-tailnet/registry.json').read_text())['entries'])


if __name__=='__main__':unittest.main()
