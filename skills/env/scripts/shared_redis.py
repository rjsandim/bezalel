"""Redis local compartilhado com usuários e pares de bancos por serviço.

Redis 7 mantém SELECT por primeiro argumento nas ACLs. O banco zero fica
reservado: toda conexão nasce nele, mesmo com SELECT restrito. Não usamos isso
como isolamento entre clientes hostis; o alvo são ambientes locais confiáveis.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

from shared_db import SharedDatabaseError, identity, locked, read_json, run, write_private

SKILL = Path(__file__).resolve().parents[1]
STATE_FILE = "shared-redis.json"
Error = SharedDatabaseError
FIELDS = {"host": "REDIS_HOST", "port": "REDIS_PORT", "user": "REDIS_USERNAME",
          "password": "REDIS_PASSWORD", "db": "REDIS_DB", "cache_db": "REDIS_CACHE_DB",
          "prefix": "REDIS_PREFIX", "cache_prefix": "CACHE_PREFIX"}


def pool_spec(manifest, context):
    shared = manifest.get("redis_shared", {})
    pool, image, port = (shared.get(key) for key in ("pool", "image", "port"))
    count = shared.get("databases", 256)
    if not isinstance(pool, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", pool):
        raise Error("redis_shared.pool inválido.")
    if not isinstance(image, str) or not re.fullmatch(r"redis:7\.[0-9]+(?:\.[0-9]+)?-alpine", image):
        raise Error("Redis compartilhado exige imagem redis:7.<minor>[-patch]-alpine; outras versões não foram certificadas.")
    if type(port) is not int or not 1024 <= port <= 65535:
        raise Error("redis_shared.port deve ser uma porta local explícita entre 1024 e 65535.")
    if type(count) is not int or not 3 <= count <= 1024:
        raise Error("redis_shared.databases deve estar entre 3 e 1024.")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", context):
        raise Error("Contexto Docker explícito obrigatório.")
    name = "envstack-redis-" + pool + "-" + identity(context)[:8]
    return dict(pool=pool, image=image, port=port, databases=count, context=context,
                compose_project=name, hostname=name, network=name + "-net", volume=name + "-data")


def pool_dir(spec):
    return SKILL / "state" / "_redis" / spec["context"] / spec["pool"]


def save_pool(spec):
    directory = pool_dir(spec)
    record = directory / "pool.json"
    if record.exists():
        if read_json(record) != spec:
            raise Error("Pool Redis já registrado com outra versão/configuração; escolha outro pool.")
        if any(not (directory / name).is_file() for name in ("admin.env", "bootstrap.acl", "compose.json", "allocations.json")):
            raise Error("Estado do pool Redis incompleto; recupere os arquivos originais.")
        return
    for family in ("_redis", "_databases"):
        for other in (SKILL / "state" / family / spec["context"]).glob("*/pool.json"):
            if read_json(other)["port"] == spec["port"]:
                raise Error("Porta já registrada para outro pool neste contexto.")
    password = secrets.token_hex(32)
    write_private(directory / "admin.env", f"REDISCLI_AUTH={password}\n")
    digest = hashlib.sha256(password.encode()).hexdigest()
    write_private(directory / "bootstrap.acl", f"user default off\nuser envstack-admin on #{digest} ~* &* +@all\n")
    values = dict(spec, admin_file=str(directory / "admin.env"),
                  bootstrap_mount=str(directory / "bootstrap.acl") + ":/envstack-bootstrap.acl:ro",
                  port_mapping=f"127.0.0.1:{spec['port']}:6379", databases=str(spec["databases"]))
    template = (SKILL / "templates/shared.redis.json.tpl").read_text()
    rendered = re.sub(r"\$\{([a-z_]+)\}", lambda m: json.dumps(values[m[1]]), template)
    write_private(directory / "compose.json", json.loads(rendered))
    write_private(directory / "allocations.json", {})
    write_private(record, spec)


def prepare(manifest_path, root, project, name, context, state):
    manifest = json.loads(run("yq", "-o=json", ".", manifest_path))
    mode = manifest.get("redis_mode", "isolated")
    state = Path(state)
    saved = state / STATE_FILE
    if mode not in ("isolated", "shared"):
        raise Error("redis_mode deve ser isolated ou shared.")
    if mode == "isolated":
        if saved.exists():
            raise Error("Redis compartilhado não pode voltar ao exclusivo via update; migre explicitamente.")
        return
    spec = pool_spec(manifest, context)
    owner = dict(root=str(Path(root).resolve()), project=project, environment=name)
    services = [s for s in manifest["services"] if s.get("redis") is True]
    if not services or any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", s["folder"]) for s in services):
        raise Error("Declare redis: true nos serviços consumidores com nome simples em kebab-case.")
    if not saved.exists() and (state / "docker-compose.yml").exists():
        if os.environ.get("ENV_REDIS_MIGRATION") != f"{project}/{name}":
            raise Error("Redis existente requer backup e migração explícita; update não transfere cache, sessões ou filas.")
    with locked(SKILL / "state" / "_pools" / context):
        save_pool(spec)
        if saved.exists():
            data = read_json(saved)
            if data["pool"] != spec or data["owner"] != owner or set(data["connections"]) != {s["folder"] for s in services}:
                raise Error("Pool/contexto/proprietário/serviços divergem do Redis salvo.")
            return
        allocations_file = pool_dir(spec) / "allocations.json"
        allocations = read_json(allocations_file)
        connections = {}
        for service in services:
            fields = service.get("redis_env", FIELDS if service.get("type") == "php" else None)
            if not isinstance(fields, dict) or not fields or any(k not in {*FIELDS, "url"} or not re.fullmatch(r"[A-Z_][A-Z0-9_]*", v) for k, v in fields.items()):
                raise Error("Mapeamento redis_env inválido; Node exige configuração explícita.")
            if "prefix" not in fields or not ({"host", "port", "user", "password", "db"} <= fields.keys() or "url" in fields):
                raise Error("redis_env precisa mapear prefix e uma conexão autenticada com banco lógico.")
            key = identity(owner, service["folder"])
            if key in allocations:
                raise Error("Alocação Redis existe sem estado do ambiente; recupere o estado original.")
            used = {number for pair in allocations.values() for number in pair}
            available = [n for n in range(1, spec["databases"]) if n not in used]
            if len(available) < 2:
                raise Error("Pool Redis sem pares livres; escolha outro pool. Alocações antigas não são recicladas.")
            pair = available[:2]
            allocations[key] = pair
            connections[service["folder"]] = dict(host=spec["hostname"], port="6379", user="es" + key[:28],
                password=secrets.token_hex(24), db=str(pair[0]), cache_db=str(pair[1]),
                prefix="es:" + key[:32] + ":", cache_prefix="cache:", env_fields=fields)
        # Reserva persistida primeiro; falhas não permitem reutilizar índices alheios.
        write_private(allocations_file, allocations)
        write_private(saved, dict(owner=owner, pool=spec, connections=connections))


def load_state(state):
    path = Path(state) / STATE_FILE
    if not path.exists():
        return None
    data = read_json(path)
    spec = data["pool"]
    if spec["context"] != os.environ.get("DOCKER_CONTEXT") or read_json(pool_dir(spec) / "pool.json") != spec:
        raise Error("Contexto/registro diverge do Redis compartilhado.")
    allocations = read_json(pool_dir(spec) / "allocations.json")
    for folder, connection in data["connections"].items():
        if allocations.get(identity(data["owner"], folder)) != [int(connection["db"]), int(connection["cache_db"])]:
            raise Error("Alocação Redis diverge; recupere o estado original.")
    return data


def configure(compose, state):
    data = load_state(state)
    if not data:
        return
    config = json.loads(run("yq", "-o=json", ".", compose))
    config["services"].pop("redis", None)
    config["networks"]["shared-redis"] = dict(external=True, name=data["pool"]["network"])
    for folder, service in config["services"].items():
        deps = service.get("depends_on", {})
        if isinstance(deps, list):
            service["depends_on"] = [dep for dep in deps if dep != "redis"]
        else:
            deps.pop("redis", None)
        if folder in data["connections"]:
            networks = service.setdefault("networks", [])
            if isinstance(networks, list):
                if "shared-redis" not in networks:
                    networks.append("shared-redis")
            else:
                networks["shared-redis"] = None
    config.setdefault("x-envstack", {})["shared_redis"] = True
    write_private(compose, config)


def connection_values(connection):
    values = dict(connection)
    # Laravel usa a mesma REDIS_URL nas duas conexões: um path sobrescreveria
    # REDIS_CACHE_DB. Clientes com URL única recebem o índice no path.
    path = "" if "cache_db" in connection["env_fields"] else "/" + connection["db"]
    values["url"] = f"redis://{connection['user']}:{connection['password']}@{connection['host']}:{connection['port']}{path}"
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
        values = connection_values(connection)
        if any(env.get(variable) != values[field] for field, variable in connection["env_fields"].items()) or (env.get("REDIS_URL") and env["REDIS_URL"] != values["url"]):
            raise Error(f"Conexão de {folder}/.env diverge do Redis compartilhado; migre/configure antes de iniciar.")


def commands(spec, commands, connection=None):
    """Uma sessão CLI por lote; senha e comandos trafegam por stdin, nunca argv."""
    if connection:
        password, user = connection["password"], connection["user"]
    else:
        password = (pool_dir(spec) / "admin.env").read_text().strip().split("=", 1)[1]
        user = "envstack-admin"
    script = 'IFS= read -r REDISCLI_AUTH; export REDISCLI_AUTH; exec redis-cli --user "$1" --json'
    payload = password + "\n" + "\n".join(" ".join(json.dumps(str(arg)) for arg in command) for command in commands) + "\n"
    output = run("docker", "exec", "-i", spec["hostname"], "sh", "-c", script, "redis", user, input=payload)
    lines = output.splitlines()
    if len(lines) != len(commands) or any(line.startswith("error:") for line in lines):
        raise Error("Comando Redis recusado; estado preservado, credenciais e dados omitidos.")
    return [json.loads(line) for line in lines]


def acl_rules(connection):
    if not re.fullmatch(r"es[a-f0-9]{28}", connection["user"]) or not re.fullmatch(r"[a-f0-9]{48}", connection["password"]) or not re.fullmatch(r"es:[a-f0-9]{32}:", connection["prefix"]):
        raise Error("Identidade Redis inválida.")
    if any(not re.fullmatch(r"[1-9][0-9]*", connection[key]) for key in ("db", "cache_db")):
        raise Error("Banco Redis zero é reservado e nunca pode ser alocado.")
    digest = hashlib.sha256(connection["password"].encode()).hexdigest()
    return ["reset", "on", "#" + digest, "~" + connection["prefix"] + "*", "&" + connection["prefix"] + "*",
            "+@read", "+@write", "+@transaction", "+@scripting", "+@connection", "+@pubsub",
            "-@admin", "-@dangerous", "-copy", "-move", "-pubsub", "-function", "-script",
            "+script|load", "+script|exists", "-select",
            "+select|" + connection["db"], "+select|" + connection["cache_db"], "+flushdb"]


def verify_permissions(spec, connection):
    prefix = connection["prefix"]
    allowed = [["SELECT", connection["db"]], ["SELECT", connection["cache_db"]],
               ["GET", prefix + "probe"], ["SET", prefix + "probe", "value"], ["FLUSHDB"]]
    forbidden = [["SELECT", str(number)] for number in range(spec["databases"])
                 if str(number) not in (connection["db"], connection["cache_db"])]
    forbidden += [["FLUSHALL"], ["SWAPDB", "0", connection["db"]],
                 ["COPY", prefix + "probe", prefix + "copy", "DB", "0"], ["MOVE", prefix + "probe", "0"],
                 ["GET", "other:probe"], ["SET", "other:probe", "value"], ["CONFIG", "GET", "*"],
                 ["ACL", "LIST"], ["PUBLISH", "other:channel", "value"], ["SCRIPT", "FLUSH"],
                 ["FUNCTION", "FLUSH"], ["SHUTDOWN"], ["REPLICAOF", "NO", "ONE"]]
    results = commands(spec, [["ACL", "DRYRUN", connection["user"], *command] for command in allowed + forbidden])
    if any(value != "OK" for value in results[:len(allowed)]) or any(value == "OK" for value in results[len(allowed):]):
        raise Error("Permissões Redis não preservam o isolamento esperado; inicialização bloqueada.")
    if commands(spec, [["SELECT", connection["db"]], ["SELECT", connection["cache_db"]], ["PING"]], connection) != ["OK", "OK", "PONG"]:
        raise Error("Login Redis do ambiente não validado.")


def verify_resources(spec):
    project = spec["compose_project"]
    for kind, name in (("volume", spec["volume"]), ("network", spec["network"])):
        existing = run("docker", kind, "ls", "--format", "{{.Name}}").splitlines()
        if name in existing:
            labels = json.loads(run("docker", kind, "inspect", name, "--format", "{{json .Labels}}")) or {}
            if labels.get("com.docker.compose.project") != project:
                raise Error("Recurso Redis existe sem propriedade comprovada.")
        elif kind == "volume" and (pool_dir(spec) / "initialized").exists():
            raise Error("Volume Redis inicializado ausente; restaure os dados antes de iniciar.")
    if spec["hostname"] in run("docker", "ps", "-a", "--format", "{{.Names}}").splitlines():
        detail = json.loads(run("docker", "inspect", spec["hostname"], "--format", "{{json .Config}}"))
        if detail.get("Labels", {}).get("com.docker.compose.project") != project or detail["Image"] != spec["image"]:
            raise Error("Container Redis tem proprietário ou imagem divergente.")


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
    provision_pool(data)


def provision_pool(data):
    """Provisiona o destino de um ambiente; a migração explícita importa depois."""
    if os.environ.get("ENV_ALLOW_SHARED_INFRA") != "1":
        raise Error("Iniciar Redis compartilhado exige autorização para infraestrutura compartilhada.")
    spec = data["pool"]
    directory = pool_dir(spec)
    with locked(directory):
        verify_resources(spec)
        run("docker", "compose", "-f", str(directory / "compose.json"), "up", "-d", "--no-recreate", "--wait", "--wait-timeout", "120", "redis")
        write_private(directory / "initialized", "1\n")
        member = directory / "members" / (identity(data["owner"]) + ".json")
        record = read_json(member) if member.exists() else None
        if record and (record["data"] != data or record.get("status") not in ("pending", "ready")):
            raise Error("Vínculo Redis anterior diverge; recupere o estado original.")
        for connection in data["connections"].values():
            acl_rules(connection)
            exists = commands(spec, [["ACL", "GETUSER", connection["user"]]])[0] is not None
            if not record and exists:
                raise Error("Usuário Redis existe sem vínculo; operação interrompida.")
            if not record:
                counts = commands(spec, [["SELECT", connection["db"]], ["DBSIZE"],
                                         ["SELECT", connection["cache_db"]], ["DBSIZE"]])
                if counts != ["OK", 0, "OK", 0]:
                    raise Error("Banco lógico Redis já contém dados sem vínculo; operação interrompida.")
            if record and record["status"] == "ready" and not exists:
                raise Error("Usuário Redis anteriormente provisionado ausente; restaure o estado.")
        if not record:
            write_private(member, dict(data=data, status="pending"))
        for connection in data["connections"].values():
            if not record or record["status"] != "ready":
                commands(spec, [["ACL", "SETUSER", connection["user"], *acl_rules(connection)], ["ACL", "SAVE"]])
            verify_permissions(spec, connection)
        write_private(member, dict(data=data, status="ready"))
    print("Redis compartilhado pronto; bancos lógicos e permissões exclusivos conferidos.")


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
    except Error as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        print("Falha no Redis compartilhado; configuração, conexão ou pré-requisito inválido. Estado preservado.", file=sys.stderr)
        sys.exit(1)
