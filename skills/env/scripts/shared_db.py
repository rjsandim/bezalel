"""Bancos locais compartilhados: contrato, estado, Compose e provisionamento.

O ciclo de vida do pool é independente do ambiente. Este módulo nunca remove
containers, volumes, databases ou usuários e nunca imprime credenciais.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import time

SKILL = Path(__file__).resolve().parents[1]
STATE_FILE = "shared-database.json"


class SharedDatabaseError(RuntimeError):
    """Mensagem diagnóstica sem dados privados."""


def run(*args, input=None):
    result = subprocess.run(args, input=input, text=True, capture_output=True)
    if result.returncode:
        # Saídas de SQL/Compose podem conter credenciais e dados do aplicativo.
        raise SharedDatabaseError(f"Falha em {args[0]} (código {result.returncode}); operação interrompida, estado preservado.")
    return result.stdout


def read_json(path):
    return json.loads(Path(path).read_text())


def write_private(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(value if isinstance(value, str) else json.dumps(value, indent=2) + "\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def locked(directory):
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (directory / ".lock").open("a") as stream:
        deadline = time.monotonic() + 30
        while True:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise SharedDatabaseError("Pool ocupado por outra operação; tente novamente após sua conclusão.")
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def identity(*parts):
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()


def pool_spec(manifest, context):
    engine = manifest.get("database")
    shared = manifest.get("database_shared", {})
    pool = shared.get("pool", "")
    image = shared.get("image", "")
    port = shared.get("port")
    if engine not in ("mysql", "postgres"):
        raise SharedDatabaseError("Banco compartilhado exige database: mysql ou postgres.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", pool):
        raise SharedDatabaseError("database_shared.pool inválido.")
    if not re.fullmatch(engine + r":[0-9]+(?:\.[0-9]+)*(?:-alpine)?", image):
        raise SharedDatabaseError("Use imagem oficial com versão explícita e compatível com database.")
    if isinstance(port, bool) or not isinstance(port, int) or not 1024 <= port <= 65535:
        raise SharedDatabaseError("database_shared.port deve ser uma porta local explícita entre 1024 e 65535.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", context):
        raise SharedDatabaseError("Contexto Docker explícito obrigatório.")
    name = "envstack-db-" + pool + "-" + identity(context)[:8]
    return dict(engine=engine, pool=pool, image=image, port=port, context=context,
                compose_project=name, hostname=name, network=name + "-net", volume=name + "-data")


def pool_dir(spec):
    return SKILL / "state" / "_databases" / spec["context"] / spec["pool"]


def save_pool(spec):
    directory = pool_dir(spec)
    record = directory / "pool.json"
    if record.exists():
        if read_json(record) != spec:
            raise SharedDatabaseError("Pool já registrado com outra versão/configuração; escolha outro pool.")
        if not (directory / "admin.env").is_file():
            raise SharedDatabaseError("Credencial administrativa do pool ausente; recupere o arquivo original.")
        return
    # Não reutilize uma porta já atribuída a outro pool no mesmo contexto.
    for family in ("_databases", "_redis"):
        for other in (SKILL / "state" / family / spec["context"]).glob("*/pool.json"):
            if read_json(other)["port"] == spec["port"]:
                raise SharedDatabaseError("Porta já registrada para outro pool neste contexto.")
    password = secrets.token_hex(32)
    key = "MYSQL_ROOT_PASSWORD" if spec["engine"] == "mysql" else "POSTGRES_PASSWORD"
    write_private(directory / "admin.env", f"{key}={password}\n")
    write_private(record, spec)
    values = dict(spec, admin_file=str(directory / "admin.env"),
                  port_mapping=f"127.0.0.1:{spec['port']}:{3306 if spec['engine'] == 'mysql' else 5432}")
    major = int(spec["image"].split(":")[1].split(".")[0].split("-")[0])
    values["data_mount"] = "data:/var/lib/postgresql" if major >= 18 else "data:/var/lib/postgresql/data"
    template = (SKILL / "templates" / f"shared.{spec['engine']}.json.tpl").read_text()
    # Apenas os placeholders do template são substituídos; $$ do Compose fica intacto.
    rendered = re.sub(r"\$\{([a-z_]+)\}", lambda m: json.dumps(values[m[1]]), template)
    write_private(directory / "compose.json", json.loads(rendered))


def prepare(manifest_path, root, project, name, context, state):
    manifest = json.loads(run("yq", "-o=json", ".", manifest_path))
    mode = manifest.get("database_mode", "isolated")
    state = Path(state)
    saved = state / STATE_FILE
    if mode not in ("isolated", "shared"):
        raise SharedDatabaseError("database_mode deve ser isolated ou shared.")
    if mode == "isolated":
        if saved.exists():
            raise SharedDatabaseError("Ambiente compartilhado não pode voltar ao banco exclusivo via update; migre os dados explicitamente.")
        return
    spec = pool_spec(manifest, context)
    owner = dict(root=str(Path(root).resolve()), project=project, environment=name)
    folders = [s["folder"] for s in manifest["services"] if s.get("database") is True]
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", f) for f in folders):
        raise SharedDatabaseError("Serviço com banco exige nome simples em kebab-case.")
    if not saved.exists() and (state / "docker-compose.yml").exists():
        if os.environ.get("ENV_DATABASE_MIGRATION") != f"{project}/{name}":
            raise SharedDatabaseError("Ambiente existente requer backup e migração explícita; update não troca seu banco automaticamente.")
    with locked(SKILL / "state" / "_pools" / context):
        save_pool(spec)
        if saved.exists():
            data = read_json(saved)
            if data["pool"] != spec or data["owner"] != owner:
                raise SharedDatabaseError("Pool/contexto/proprietário diverge do ambiente salvo.")
            if set(data["connections"]) != set(folders):
                raise SharedDatabaseError("Lista de serviços com banco mudou; provisione a alteração explicitamente.")
            return
        connections = {}
        for folder in folders:
            service = next(s for s in manifest["services"] if s["folder"] == folder)
            fields = service.get("database_env", {"host": "DB_HOST", "port": "DB_PORT", "db": "DB_DATABASE", "user": "DB_USERNAME", "password": "DB_PASSWORD"} if service.get("type") == "php" else {"url": "DATABASE_URL"})
            if not fields or any(k not in ("host", "port", "db", "user", "password", "url") or not re.fullmatch(r"[A-Z_][A-Z0-9_]*", v) for k, v in fields.items()):
                raise SharedDatabaseError("Mapeamento database_env inválido.")
            digest = identity(owner, folder)
            # Sem '_' ou '%' no nome: GRANT do MySQL trata esses caracteres como curingas.
            readable = re.sub(r"[^a-z0-9]", "", project + name + folder)[:32]
            connections[folder] = dict(db="es" + readable + digest[:16], user="es" + digest[:28],
                                       password=secrets.token_hex(24), host=spec["hostname"],
                                       port="3306" if spec["engine"] == "mysql" else "5432", env_fields=fields)
        write_private(saved, dict(owner=owner, pool=spec, connections=connections))


def load_state(state):
    path = Path(state) / STATE_FILE
    if not path.exists():
        return None
    data = read_json(path)
    if data["pool"]["context"] != os.environ.get("DOCKER_CONTEXT"):
        raise SharedDatabaseError("Contexto difere do banco compartilhado registrado.")
    if read_json(pool_dir(data["pool"]) / "pool.json") != data["pool"]:
        raise SharedDatabaseError("Registro do pool diverge do ambiente.")
    return data


def configure(compose, state):
    data = load_state(state)
    if not data:
        return
    config = json.loads(run("yq", "-o=json", ".", compose))
    engine = data["pool"]["engine"]
    config["services"].pop(engine, None)
    config.get("volumes", {}).pop("dbdata", None)
    config["networks"]["shared-database"] = dict(external=True, name=data["pool"]["network"])
    for name, service in config["services"].items():
        deps = service.get("depends_on", {})
        if isinstance(deps, list):
            service["depends_on"] = [d for d in deps if d != engine]
        else:
            deps.pop(engine, None)
        if name in data["connections"]:
            networks = service.setdefault("networks", [])
            if isinstance(networks, list):
                networks.append("shared-database")
            else:
                networks["shared-database"] = None
    config.setdefault("x-envstack", {})["shared_database"] = True
    write_private(compose, config)


def sql(spec, statement):
    if spec["engine"] == "mysql":
        cmd = ["sh", "-c", 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql -uroot --batch --skip-column-names']
    else:
        cmd = ["psql", "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-At"]
    return run("docker", "exec", "-i", spec["hostname"], *cmd, input=statement)


def namespace_count(spec, connection):
    db, user = connection["db"], connection["user"]
    if spec["engine"] == "mysql":
        query = f"SELECT (SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='{db}') + (SELECT COUNT(*) FROM mysql.user WHERE user='{user}');"
    else:
        query = f"SELECT (SELECT COUNT(*) FROM pg_database WHERE datname='{db}') + (SELECT COUNT(*) FROM pg_roles WHERE rolname='{user}');"
    return int(sql(spec, query).strip())


def validate_identity(connection):
    for field in ("db", "user"):
        if not re.fullmatch(r"[a-z0-9]{1,63}", connection[field]):
            raise SharedDatabaseError("Identidade local inválida; estado preservado.")
    if not re.fullmatch(r"[a-f0-9]+", connection["password"]):
        raise SharedDatabaseError("Credencial local inválida; estado preservado.")


def provision(spec, connection):
    db, user, password = (connection[k] for k in ("db", "user", "password"))
    validate_identity(connection)
    if spec["engine"] == "mysql":
        statement = f"CREATE DATABASE IF NOT EXISTS `{db}`;\nCREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}';\nGRANT ALL PRIVILEGES ON `{db}`.* TO '{user}'@'%';\n"
    else:
        statement = fr"""SELECT 'CREATE ROLE {user} LOGIN PASSWORD ''{password}'' NOSUPERUSER NOCREATEDB NOCREATEROLE' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{user}')\gexec
SELECT 'CREATE DATABASE {db} OWNER {user}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='{db}')\gexec
REVOKE ALL ON DATABASE {db} FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE {db} TO {user};
"""
    sql(spec, statement)


def verify_login(spec, connection):
    validate_identity(connection)
    if spec["engine"] == "mysql":
        command = 'IFS= read -r MYSQL_PWD; export MYSQL_PWD; exec mysql -h127.0.0.1 -u "$1" "$2" --batch --skip-column-names -e "SELECT 1"'
    else:
        command = 'IFS= read -r PGPASSWORD; export PGPASSWORD; exec psql -h127.0.0.1 -U "$1" -d "$2" -v ON_ERROR_STOP=1 -At -c "SELECT 1"'
    output = run("docker", "exec", "-i", spec["hostname"], "sh", "-c", command, "login-check", connection["user"], connection["db"], input=connection["password"] + "\n")
    if output.strip() != "1":
        raise SharedDatabaseError("Login do ambiente no pool não foi validado.")


def verify_resources(spec):
    project = spec["compose_project"]
    checks = [("volume", spec["volume"]), ("network", spec["network"])]
    for kind, name in checks:
        existing = run("docker", kind, "ls", "--format", "{{.Name}}").splitlines()
        if name in existing:
            labels = json.loads(run("docker", kind, "inspect", name, "--format", "{{json .Labels}}")) or {}
            if labels.get("com.docker.compose.project") != project:
                raise SharedDatabaseError("Recurso do pool existe sem propriedade comprovada.")
    containers = run("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    if spec["hostname"] in containers:
        detail = json.loads(run("docker", "inspect", spec["hostname"], "--format", "{{json .Config}}"))
        if detail.get("Labels", {}).get("com.docker.compose.project") != project or detail["Image"] != spec["image"]:
            raise SharedDatabaseError("Container do pool tem proprietário ou imagem divergente.")
    marker = pool_dir(spec) / "initialized"
    if marker.exists() and spec["volume"] not in run("docker", "volume", "ls", "--format", "{{.Name}}").splitlines():
        raise SharedDatabaseError("Volume de um pool inicializado ausente; restaure os dados antes de iniciar.")


def connection_values(connection, engine):
    values = dict(connection)
    scheme = "mysql" if engine == "mysql" else "postgresql"
    values["url"] = f"{scheme}://{values['user']}:{values['password']}@{values['host']}:{values['port']}/{values['db']}"
    return values


def validate_connections(data, selected):
    owner = data["owner"]
    for folder in selected.intersection(data["connections"]):
        path = Path(owner["root"]) / ".worktrees" / owner["environment"] / folder / ".env"
        env = {}
        for line in path.read_text().splitlines():
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", line):
                key, value = line.split("=", 1)
                env[key] = value.strip().strip("\"'")
        connection = data["connections"][folder]
        values = connection_values(connection, data["pool"]["engine"])
        if "DB_HOST" in connection["env_fields"].values():
            for url_key in ("DB_URL", "DATABASE_URL"):
                if env.get(url_key) and env[url_key] != values["url"]:
                    raise SharedDatabaseError(f"{url_key} de {folder} diverge da conexão compartilhada.")
        if any(env.get(variable) != values[field] for field, variable in connection["env_fields"].items()):
            raise SharedDatabaseError(f"Conexão de {folder}/.env diverge do banco compartilhado; migre/configure explicitamente antes de iniciar.")


def ensure(state, compose, selected):
    data = load_state(state)
    if not data:
        return
    config = json.loads(run("yq", "-o=json", ".", compose))
    needed = set()
    def visit(name):
        if name in needed:
            return
        needed.add(name)
        for dep in config["services"][name].get("depends_on", {}):
            visit(dep)
    for service in selected:
        visit(service)
    if not needed.intersection(data["connections"]):
        return
    validate_connections(data, needed)
    if os.environ.get("ENV_ALLOW_SHARED_INFRA") != "1":
        raise SharedDatabaseError("Iniciar banco compartilhado exige autorização para infraestrutura compartilhada.")
    spec = data["pool"]
    directory = pool_dir(spec)
    with locked(directory):
        verify_resources(spec)
        run("docker", "compose", "-f", str(directory / "compose.json"), "up", "-d", "--no-recreate", "--wait", "--wait-timeout", "240", spec["engine"])
        write_private(directory / "initialized", "1\n")
        member = directory / "members" / (identity(data["owner"]) + ".json")
        record = read_json(member) if member.exists() else None
        if record and (record["data"] != data or record.get("status") not in ("pending", "ready")):
            raise SharedDatabaseError("Vínculo anterior do ambiente diverge; recupere o estado original.")
        for connection in data["connections"].values():
            validate_identity(connection)
            count = namespace_count(spec, connection)
            if record is None and count != 0:
                raise SharedDatabaseError("Namespace já existe sem vínculo; operação interrompida.")
            if record and record["status"] == "ready" and count != 2:
                raise SharedDatabaseError("Database/usuário anteriormente provisionado ausente; restaure antes de iniciar.")
        if record is None:
            write_private(member, dict(data=data, status="pending"))
        for connection in data["connections"].values():
            if record is None or record["status"] != "ready":
                provision(spec, connection)
            verify_login(spec, connection)
        write_private(member, dict(data=data, status="ready"))
    print("Pool compartilhado pronto; databases e usuários exclusivos conferidos.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "configure", "ensure"])
    parser.add_argument("arguments", nargs="*")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(*args.arguments)
    elif args.action == "configure":
        configure(*args.arguments)
    else:
        ensure(args.arguments[0], args.arguments[1], args.arguments[2:])


if __name__ == "__main__":
    try:
        main()
    except SharedDatabaseError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        # Nenhuma exceção de parsers/SQL deve vazar conteúdo privado.
        print("Falha no banco compartilhado; configuração, propriedade, conexão ou pré-requisito inválido. Estado preservado.", file=sys.stderr)
        sys.exit(1)
