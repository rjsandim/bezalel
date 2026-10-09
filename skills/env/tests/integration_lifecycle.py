"""Real Docker lifecycle rehearsal with synthetic data, isolated from user worktrees.
Requires --allow-real-infrastructure and --docker-context CONTEXT, plus image/module arguments.
Images must contain PHP+Composer+pdo_mysql, or Node+npm, respectively.
Requires the shared envstack proxy infrastructure to be available. Manifests are
prepared in dry-run mode so this rehearsal never configures host DNS or certificates.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('--allow-real-infrastructure', action='store_true', required=True)
parser.add_argument('--docker-context', required=True)
parser.add_argument('--php-image', required=True)
parser.add_argument('--node-image', required=True)
parser.add_argument('--playwright-module', required=True)
args = parser.parse_args()
subprocess.run(['docker', 'context', 'inspect', args.docker_context], check=True, stdout=subprocess.DEVNULL)
run_environment = {**os.environ, 'DOCKER_CONTEXT': args.docker_context, 'ENV_ALLOW_SHARED_INFRA': '1'}
skill_source = Path(__file__).resolve().parents[1]
base = Path(tempfile.mkdtemp(prefix='env-real-lifecycle-'))
skill = base / 'skill'
repo = base / 'repo'
repo.mkdir()
for folder in ('scripts', 'templates'):
    shutil.copytree(skill_source / folder, skill / folder)
name = 'envcheck-' + uuid.uuid4().hex[:8]
project = 'env-fixture'
stack = repo / '.envstack'
stack.mkdir()
compose = skill / f'state/{project}/{name}/docker-compose.yml'
worktree = repo / f'.worktrees/{name}'
checks = []


def run(command, *, env=None, echo=False):
    result = subprocess.run(command, cwd=repo, env={**run_environment, **(env or {})}, text=True, capture_output=True)
    if echo or result.returncode:
        print(result.stdout[-3500:], result.stderr[-3500:], flush=True)
    if result.returncode:
        raise RuntimeError(f'{command[0]} failed with exit {result.returncode}')
    return result.stdout.strip()


def control(action, *services):
    return run(['bash', str(skill / 'scripts/ctl.sh'), action, name, *services])


def docker_compose(*parts):
    return run(['docker', 'compose', '-f', str(compose), *parts])


def running():
    return set(docker_compose('ps', '--services', '--status', 'running').splitlines())


def check(description, condition):
    if not condition:
        raise AssertionError(description)
    checks.append(description)
    print('PASS ' + description, flush=True)


def database(query):
    return run(['docker', 'exec', f'{project}-{name}-mysql', 'sh', '-c',
                'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot --batch --skip-column-names api -e "$1"', 'sh', query])


(stack / 'stack.yaml').write_text(f'''project: {project}
engine: auto
docker_context: {json.dumps(args.docker_context)}
tld: local
database: mysql
startup:
  services: [api]
services:
  - {{folder: api, type: php, port: 8000, database: true, aliases: [admin]}}
  - {{folder: site, type: node, port: 5173, database: false, depends_on: [api]}}
  - {{folder: docs, type: node, port: 5173, database: false, depends_on: []}}
''')
shutil.copyfile(skill_source / 'templates/boot.sh.tpl', stack / 'boot.sh')
for service in ('api', 'site', 'docs'):
    folder = repo / service
    folder.mkdir()
    (folder / 'work.txt').write_text('synthetic uncommitted work\n')
    (stack / f'{service}.env.example').write_text('APP_ENV=local\nDB_USERNAME=${env:db.user}\n')
    if service == 'api':
        image = args.php_image
        command = '["sh", "/usr/local/bin/envstack-boot", "php", "php", "artisan", "serve"]'
        (folder / 'composer.json').write_text('{"name":"envstack/fixture","require":{}}\n')
        (folder / 'artisan').write_text('''<?php
if ($argv[1] === 'migrate') {
    $db = new PDO('mysql:host=mysql;dbname=api', getenv('DB_USERNAME'), 'secret');
    $db->exec('CREATE TABLE IF NOT EXISTS env_probe (id INT PRIMARY KEY, message VARCHAR(80))');
    $db->exec("INSERT IGNORE INTO env_probe VALUES (1, 'initial')");
    exit(0);
}
passthru('php -S 0.0.0.0:8000 router.php', $code);
exit($code);
''')
        (folder / 'router.php').write_text('<?php echo "<h1>Ambiente de teste</h1><p>Somente dados ficticios.</p>";\n')
    else:
        image = args.node_image
        command = '["sh", "/usr/local/bin/envstack-boot", "node", "npm", "run", "dev"]'
        (folder / 'package.json').write_text('{"name":"envstack-fixture","version":"1.0.0","scripts":{"dev":"node server.js"}}\n')
        (folder / 'server.js').write_text("require('http').createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<h1>Documentação de teste</h1><p>Somente dados fictícios.</p>')}).listen(5173,'0.0.0.0');\n")
    (stack / f'{service}.Dockerfile').write_text(f'FROM {image}\nCOPY boot.sh /usr/local/bin/envstack-boot\nWORKDIR /app\nCMD {command}\n')

run(['git', 'init', '-b', 'master'])
run(['git', 'config', 'core.hooksPath', '/dev/null'])
run(['git', 'add', '.'])
run(['git', '-c', 'user.name=Env Test', '-c', 'user.email=env@example.invalid', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'synthetic fixture'])
try:
    run(['bash', str(skill / 'scripts/new.sh'), name], env={'ENV_DRY_RUN': '1'})
    run(['yq', '-i', '(.services[] | select(has("healthcheck"))).healthcheck.start_period = "5s" | (.services[] | select(has("healthcheck"))).healthcheck.interval = "1s"', str(compose)])
    run(['yq', '-i', '.services.docs.ports = ["127.0.0.1::5173"]', str(compose)])
    control('start')
    check('default starts only API, MySQL and Redis', running() == {'api', 'mysql', 'redis'})
    api_id = docker_compose('ps', '-q', 'api')
    db_id = docker_compose('ps', '-q', 'mysql')
    database("UPDATE env_probe SET message='preserved across lifecycle' WHERE id=1")
    run(['docker', 'exec', f'{project}-{name}-redis', 'redis-cli', 'SET', 'env-probe', 'preserved'])
    envfile = worktree / 'api/.env'
    envfile.write_text(envfile.read_text() + 'LOCAL_CHANGE=preserve-this\n')
    sourcefile = worktree / 'api/work.txt'
    sourcefile.write_text('unsaved-in-git user edits\n')
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (envfile, sourcefile)]
    control('ensure', 'docs', 'site')
    check('documentation and site can be added later', running() == {'api', 'mysql', 'redis', 'site', 'docs'})
    check('adding services preserves API and database containers', api_id == docker_compose('ps', '-q', 'api') and db_id == docker_compose('ps', '-q', 'mysql'))
    for service in ('api', 'site', 'docs'):
        port = '8000' if service == 'api' else '5173'
        body = run(['docker', 'exec', f'{project}-{name}-{service}', 'curl', '-fsS', f'http://localhost:{port}/'])
        check(service + ' responds after activation', '<h1>' in body)
    capture = base / 'capture.cjs'
    capture.write_text('''const { chromium } = require(process.argv[2]);
(async () => {
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const page = await browser.newPage({ignoreHTTPSErrors:true});
    await page.goto(process.argv[3]);
    if (await page.locator('h1').innerText() !== 'Documentação de teste') throw new Error('Unexpected page');
    await page.screenshot({path:process.argv[4], fullPage:true});
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
''')
    docs_address = docker_compose('port', 'docs', '5173')
    run(['node', str(capture), args.playwright_module, f'http://{docs_address}', str(base / 'documentation.png')])
    check('documentation screenshot works after on-demand activation', (base / 'documentation.png').stat().st_size > 100)
    control('stop')
    check('stop releases running processes', running() == set())
    control('start')
    check('start resumes the previously activated set', len(running()) == 5)
    check('database data survives stop/start', database('SELECT message FROM env_probe WHERE id=1') == 'preserved across lifecycle')
    check('Redis data survives graceful stop/start', run(['docker', 'exec', f'{project}-{name}-redis', 'redis-cli', 'GET', 'env-probe']) == 'preserved')
    check('local env and uncommitted files survive', before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in (envfile, sourcefile)])
    for service in ('api', 'site', 'docs'):
        logs = run(['docker', 'logs', f'{project}-{name}-{service}'])
        check(service + ' skips dependency reinstall on second boot', logs.count('envstack: preparando dependencias') == 1 and 'envstack: dependencias conferidas' in logs)
    # Regenerate through the public command, then exercise the real rebuild helper.
    # Infrastructure provisioning is outside this isolated lifecycle rehearsal.
    run(['bash', str(skill / 'scripts/update.sh'), name, 'docs'], env={'ENV_DRY_RUN': '1'})
    run(['bash', '-c', '''
set -euo pipefail
source "$1/lib.sh"
apply_docker_engine
source "$1/services.sh"
STATE_DIR="$2"
COMPOSE="$STATE_DIR/docker-compose.yml"
start_services update docs
''', 'env-lifecycle-test', str(skill / 'scripts'), str(compose.parent)])
    check('targeted update preserves database and running API', db_id == docker_compose('ps', '-q', 'mysql') and api_id == docker_compose('ps', '-q', 'api'))
    check('targeted update preserves local configuration and data', before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in (envfile, sourcefile)] and database('SELECT message FROM env_probe WHERE id=1') == 'preserved across lifecycle')
    report = {'checks': checks, 'count': len(checks), 'project': f'{project}-{name}'}
    (base / 'report.json').write_text(json.dumps(report, indent=2))
    print('REPORT ' + str(base / 'report.json'), flush=True)
except Exception:
    if compose.exists():
        logs = subprocess.run(['docker', 'compose', '-f', str(compose), 'logs', '--no-color'], env=run_environment, text=True, capture_output=True)
        (base / 'failure.log').write_text(logs.stdout + logs.stderr)
        print('DIAGNOSTICS ' + str(base / 'failure.log'), flush=True)
    raise
finally:
    if compose.exists():
        # This unique project contains only disposable fixtures created above.
        subprocess.run(['docker', 'compose', '-f', str(compose), 'down', '--volumes'], env=run_environment, cwd=repo, check=True, capture_output=True)
