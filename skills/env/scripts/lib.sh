#!/usr/bin/env bash
# lib.sh — funcoes comuns das acoes da skill `env`.
# Carregado via `source` por init.sh / new.sh / update.sh / destroy.sh.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TPL_DIR="$SKILL_DIR/templates"

# Infra compartilhada por TODOS os projetos: um unico Traefik em 80/443 e uma
# unica rede proxy. Cada projeto so deposita seu cert + dynamic config nessa pasta.
ENVSTACK_PROXY="envstack-proxy"
ENVSTACK_TRAEFIK="envstack-traefik"
TRAEFIK_STATE="$SKILL_DIR/state/_traefik"

# ─── Cores / logging ───────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $1" >&2; exit 1; }
step()  { echo -e "\n${BOLD}━━━ $1 ━━━${NC}"; }

# ─── Pre-requisitos ────────────────────────────────────────────
require_tools() {
    for t in "$@"; do
        command -v "$t" >/dev/null 2>&1 || fail "Ferramenta necessaria nao encontrada: $t (instale via Homebrew)"
    done
}

# ─── Contexto do projeto ───────────────────────────────────────
# SEMPRE o repo principal, mesmo se chamado de dentro de uma worktree linkada
# (`--show-toplevel` retornaria a worktree, quebrando project_name/state/destroy).
# git-common-dir aponta para o .git compartilhado; seu pai e o repo principal.
repo_root() {
    local cdir
    cdir="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
    if [ -n "$cdir" ]; then dirname "$cdir"
    else git rev-parse --show-toplevel 2>/dev/null || fail "Nao esta dentro de um repositorio git."; fi
}
manifest_path(){ echo "$(repo_root)/.envstack/stack.yaml"; }

# Le um campo do manifesto via yq. Uso: manifest_get '.project'
manifest_get() {
    local m; m="$(manifest_path)"
    [ -f "$m" ] || fail "Manifesto nao encontrado: .envstack/stack.yaml — rode '/env init' primeiro."
    yq -r "$1 // \"\"" "$m"
}

# Nome-base do projeto: manifesto (se setado) senao basename do repo.
project_name() {
    local p=""; [ -f "$(manifest_path)" ] && p="$(manifest_get '.project')"
    [ -n "$p" ] || p="$(basename "$(repo_root)")"
    validate_env_name "$p"
    printf '%s\n' "$p"
}
project_tld() {
    local t=""; [ -f "$(manifest_path)" ] && t="$(manifest_get '.tld')"
    echo "${t:-local}"
}

# ─── Engine Docker (OrbStack | Docker Desktop) ─────────────────
# O manifesto pode fixar qual engine o projeto usa — util quando ha mais de um
# instalado. Mapeia o valor amigavel do manifesto p/ o nome do `docker context`.
engine_to_context() {
    case "$1" in
        orbstack)       echo "orbstack" ;;
        docker-desktop) echo "desktop-linux" ;;
        auto)           echo "" ;;
        *)              fail "Engine desconhecido no manifesto." ;;
    esac
}

# Engine ativo agora — usado pelo init p/ semear o manifesto. Tolerante a docker
# ausente -> 'auto'.
detect_docker_engine() {
    local ctx; ctx="$(docker context show 2>/dev/null || true)"
    case "$ctx" in
        orbstack)      echo "orbstack" ;;
        desktop-linux) echo "docker-desktop" ;;
        *)             echo "auto" ;;
    esac
}

# Engine declarado no manifesto (default auto = nao fixa nada).
project_engine() {
    local e=""; [ -f "$(manifest_path)" ] && e="$(manifest_get '.engine')"
    echo "${e:-auto}"
}

# Valida um destino explicito, sem fallback para o contexto ativo.
apply_docker_engine() {
    local engine ctx mapped
    engine="$(project_engine)"
    mapped="$(engine_to_context "$engine")"
    ctx="$(manifest_get '.docker_context')"
    [ -z "$mapped" ] || [ -z "$ctx" ] || [ "$mapped" = "$ctx" ] || fail "engine e docker_context divergem."
    ctx="${ctx:-$mapped}"
    [ -n "$ctx" ] || fail "Defina docker_context; nenhum contexto sera escolhido implicitamente."
    [[ "$ctx" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*$ ]] || fail "docker_context invalido."
    docker context inspect "$ctx" >/dev/null 2>&1 || fail "Contexto Docker configurado indisponivel; operacao cancelada."
    export DOCKER_CONTEXT="$ctx"
}

base_ref() {
    local root ref="" candidate count=0
    root="$(repo_root)"
    [ ! -f "$(manifest_path)" ] || ref="$(manifest_get '.base_ref')"
    if [ -z "$ref" ]; then
        ref="$(git -C "$root" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null || true)"
    fi
    if [ -z "$ref" ]; then
        for candidate in main master; do
            if git -C "$root" show-ref --verify --quiet "refs/heads/$candidate"; then
                ref="$candidate"; count=$((count + 1))
            fi
        done
        [ "$count" -eq 1 ] || fail "Base ambigua ou ausente: configure base_ref no manifesto."
    fi
    git -C "$root" rev-parse --verify --end-of-options "${ref}^{commit}" >/dev/null 2>&1 || fail "base_ref nao resolve para um commit local."
    printf '%s\n' "$ref"
}

validate_state_owner() {
    local state="$1"
    [ -f "$state/project-root" ] && [ -f "$state/docker-context" ] || fail "Estado legado sem vinculo de projeto/contexto. Audite sua origem antes de operar."
    [ "$(cat "$state/project-root")" = "$(repo_root)" ] || fail "Estado pertence a outro repositorio."
    [ "$(cat "$state/docker-context")" = "$DOCKER_CONTEXT" ] || fail "Contexto diverge do registrado no ambiente."
}

require_shared_infra_authorization() {
    [ "${ENV_ALLOW_SHARED_INFRA:-0}" = 1 ] || fail "Infra compartilhada exige autorizacao explicita: ENV_ALLOW_SHARED_INFRA=1 somente para esta execucao."
}

validate_worktree() {
    local path="$1" branch="$2" registered
    if [ -n "${STATE_DIR:-}" ] && [ -f "$STATE_DIR/worktree-branch" ]; then
        branch="$(cat "$STATE_DIR/worktree-branch")"
    fi
    [ -d "$path" ] && [ ! -L "$path" ] || fail "Worktree esperada ausente ou vinculada por symlink."
    registered="$(git -C "$(repo_root)" worktree list --porcelain)"
    printf '%s\n' "$registered" | grep -Fxq "worktree $path" || fail "Worktree nao registrada neste repositorio."
    [ "$(git -C "$path" rev-parse --show-toplevel)" = "$path" ] || fail "Diretorio nao e a worktree esperada."
    [ "$(git -C "$path" symbolic-ref --quiet --short HEAD)" = "$branch" ] || fail "Branch da worktree difere do ambiente."
}

validate_env_name() {
    local name="$1"
    [ -n "$name" ] || fail "Nome do ambiente vazio."
    [[ "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || \
        fail "Nome invalido: '$name'. Use minusculas, numeros e traco (kebab-case)."
}

# ─── Deteccao ──────────────────────────────────────────────────
detect_folder_type() {
    local dir="$1"
    if [ -f "$dir/composer.json" ] || [ -f "$dir/artisan" ]; then echo "php"
    elif [ -f "$dir/package.json" ]; then echo "node"
    elif [ -f "$dir/index.html" ]; then echo "static"
    else echo "unknown"; fi
}

# Framework de uma pasta node: "next" (dep next) ou "vite" (default).
# Muda o flag do dev server (--host/--port no Vite vs -H/-p no Next) e o
# template de .env (VITE_API_URL vs NEXT_PUBLIC_API_URL).
detect_node_framework() {
    local dir="$1"
    [ -f "$dir/package.json" ] || { echo "vite"; return 0; }
    if jq -e '(.dependencies.next // .devDependencies.next) != null' "$dir/package.json" >/dev/null 2>&1; then
        echo "next"
    else
        echo "vite"
    fi
}

# Versao do runtime a partir dos manifests do projeto. Ecoa "" se nao detectar.
# Nunca falha: versao ausente e situacao normal (init.sh aplica um default).
detect_version() {
    local dir="$1" type="$2" v=""
    case "$type" in
        php)
            [ -f "$dir/composer.json" ] || { echo ""; return 0; }
            # require.php ">=8.2|^8.4|8.3.*" -> primeiro X.Y encontrado
            v="$(jq -r '.require.php // ""' "$dir/composer.json" 2>/dev/null \
                | grep -oE '[0-9]+\.[0-9]+' | head -1 || true)" ;;
        node)
            if [ -f "$dir/.nvmrc" ]; then
                v="$(grep -oE '[0-9]+' "$dir/.nvmrc" | head -1 || true)"
            elif [ -f "$dir/package.json" ]; then
                v="$(jq -r '.engines.node // ""' "$dir/package.json" 2>/dev/null | grep -oE '[0-9]+' | head -1 || true)"
            fi ;;
    esac
    echo "$v"
}

default_port_for_type() {
    case "$1" in php) echo 8000;; node) echo 5173;; static) echo 80;; *) echo 8080;; esac
}

# Porta deterministica do banco no host (para o IDE/DataGrip conectar de fora do
# Docker). Derivada do nome do ambiente -> mesmo valor em new.sh e ide.sh, sem
# estado em arquivo. Faixa 33000-34999 (baixa chance de colisao entre ambientes).
db_host_port() {
    local n; n=$(printf '%s' "$1" | cksum | cut -d' ' -f1)
    echo $(( 33000 + n % 2000 ))
}

# ─── Readiness: esperar os servicos realmente subirem ──────────────────────────
# O 1o boot de cada container roda `composer install`/`npm install` + migrations
# ANTES de servir a porta. Sem esperar, a skill anuncia "pronto" e o usuario bate
# num 502 do Traefik (upstream ainda nao escuta). Estas funcoes dao o sinal real.

# Porta de servico de um container = 1a porta declarada em EXPOSE no Dockerfile.
_container_port() {
    docker inspect --format '{{range $p,$_ := .Config.ExposedPorts}}{{$p}} {{end}}' "$1" 2>/dev/null \
        | tr ' ' '\n' | grep -oE '^[0-9]+' | head -1
}

# Pronto = healthcheck "healthy"; se o container nao tiver healthcheck (ambiente
# antigo, criado antes desta versao), faz fallback: precisa estar rodando E
# responder HTTP na porta exposta. Retorna 0 se pronto, 1 caso contrario.
_container_ready() {
    local c="$1"
    if [ -n "$(docker inspect --format '{{if .Config.Healthcheck}}1{{end}}' "$c" 2>/dev/null)" ]; then
        [ "$(docker inspect --format '{{.State.Health.Status}}' "$c" 2>/dev/null)" = "healthy" ]
        return
    fi
    [ "$(docker inspect --format '{{.State.Running}}' "$c" 2>/dev/null)" = "true" ] || return 1
    local port; port="$(_container_port "$c")"
    [ -n "$port" ] || return 0   # sem porta conhecida -> basta estar rodando
    docker exec "$c" sh -c "curl -s -o /dev/null http://127.0.0.1:${port}/" >/dev/null 2>&1
}

# Espera uma lista de containers ficar pronta, com barra de progresso e timeout.
# Uso: wait_healthy <timeout_seg> <container...>   (containers inexistentes sao ignorados)
# Retorna 0 se todos prontos; 1 (com aviso) se estourar o timeout.
wait_healthy() {
    local timeout="$1"; shift
    [ "$#" -gt 0 ] || return 0
    local cs=("$@") deadline=$(( SECONDS + timeout )) drew=0
    while :; do
        local still=()
        for c in "${cs[@]}"; do
            docker inspect "$c" >/dev/null 2>&1 || continue
            _container_ready "$c" || still+=("$c")
        done
        if [ "${#still[@]}" -eq 0 ]; then
            [ "$drew" -eq 1 ] && printf '\r\033[K' >&2
            return 0
        fi
        if [ "$SECONDS" -ge "$deadline" ]; then
            [ "$drew" -eq 1 ] && printf '\r\033[K' >&2
            warn "Ainda subindo apos ${timeout}s: ${still[*]} — veja os logs (docker logs <container>)"
            return 1
        fi
        printf '\r\033[K  aguardando boot (deps + migrations): %s' "${still[*]}" >&2
        drew=1
        sleep 3
    done
}

# ─── Render de template (envsubst com lista controlada) ────────
# Substitui apenas ${VARS} listadas em RENDER_VARS (exportadas no ambiente).
# Cifroes fora da lista (e ${env:...}) passam intactos.
render_template() {
    local tpl="$TPL_DIR/$1" dst="$2"
    [ -f "$tpl" ] || fail "Template ausente: $tpl"
    if [ "$dst" = /dev/stdout ] || [ "$dst" = - ]; then
        envsubst "$RENDER_VARS" < "$tpl"
    else
        envsubst "$RENDER_VARS" < "$tpl" > "$dst"
    fi
}

# ─── Resolucao de placeholders ${env:...} nos .env ─────────────
# Uso: resolve_env <src> <dst> <folder> <type>
# Requer exportadas: ES_PROJECT ES_NAME ES_TLD ES_PG_USER ES_PG_PASS ES_SERVICES
# Opcional: ES_DB_ENGINE (postgres|mysql, default postgres) — define os db.* genericos.
resolve_env() {
    local src="$1" dst="$2" folder="$3" ftype="$4" aliases="${5:-}"
    ES_FOLDER="$folder" ES_FTYPE="$ftype" ES_ALIASES="$aliases" ES_SRC="$src" ES_DST="$dst" python3 - <<'PY'
import os, re, sys, json
project = os.environ["ES_PROJECT"]; name = os.environ["ES_NAME"]; tld = os.environ["ES_TLD"]
folder = os.environ["ES_FOLDER"]; pg_user = os.environ["ES_PG_USER"]; pg_pass = os.environ["ES_PG_PASS"]
engine = os.environ.get("ES_DB_ENGINE", "postgres")
pairs = [s.split(":") for s in os.environ.get("ES_SERVICES", "").split() if s]
services = [p[0] for p in pairs]
backend = next((p[0] for p in pairs if len(p) > 1 and p[1] == "php"), None)  # 1o servico php
aliases = os.environ.get("ES_ALIASES", "").split()  # dominios extras deste servico
# Host de UM nivel (traco), p/ um unico wildcard *.<projeto>.<tld> cobrir tudo.
def host(f): return f"{name}-{f}.{project}.{tld}"
def url(f):  return f"https://{host(f)}"
flat = {
    "project": project, "name": name,
    "postgres.host": "postgres", "postgres.port": "5432", "postgres.db": folder,
    "postgres.user": pg_user, "postgres.password": pg_pass,
    "postgres.url": f"postgresql://{pg_user}:{pg_pass}@postgres:5432/{folder}",
    "mysql.host": "mysql", "mysql.port": "3306", "mysql.db": folder,
    "mysql.user": pg_user, "mysql.password": pg_pass,
    "mysql.url": f"mysql://{pg_user}:{pg_pass}@mysql:3306/{folder}",
    "redis.host": "redis", "redis.port": "6379", "redis.url": "redis://redis:6379",
    "redis.user": "default", "redis.password": "", "redis.db": "0", "redis.cache_db": "1",
    "redis.prefix": f"{project}:{name}:{folder}:", "redis.cache_prefix": "cache:",
    "url.self": url(folder), "host.self": host(folder), "internal.self": folder,
}
shared_file = os.environ.get("ES_SHARED_DB_FILE", "")
if shared_file and os.path.isfile(shared_file):
    shared = json.load(open(shared_file))
    connection = shared["connections"].get(folder)
    if connection:
        for key in ("host", "port", "db", "user", "password"):
            flat[f"{engine}.{key}"] = connection[key]
        scheme = "mysql" if engine == "mysql" else "postgresql"
        flat[f"{engine}.url"] = f"{scheme}://{connection['user']}:{connection['password']}@{connection['host']}:{connection['port']}/{connection['db']}"
# db.* generico = espelho do engine selecionado (db.connection no formato Laravel).
redis_connection = None
redis_file = os.environ.get("ES_SHARED_REDIS_FILE", "")
if redis_file and os.path.isfile(redis_file):
    sys.path.insert(0, os.environ["ES_SCRIPT_DIR"])
    from shared_redis import connection_values
    redis_connection = json.load(open(redis_file))["connections"].get(folder)
    if redis_connection:
        for key, value in connection_values(redis_connection).items():
            flat[f"redis.{key}"] = value
_engine = "mysql" if engine == "mysql" else "postgres"
flat["db.connection"] = "mysql" if _engine == "mysql" else "pgsql"
for k in ("host", "port", "db", "user", "password", "url"):
    flat[f"db.{k}"] = flat[f"{_engine}.{k}"]
for s in services:
    flat[f"url.{s}"] = url(s); flat[f"host.{s}"] = host(s); flat[f"internal.{s}"] = s
# backend = 1o servico php (aponta o frontend p/ a API sem hardcode da pasta).
if backend:
    flat["url.backend"] = url(backend); flat["host.backend"] = host(backend); flat["internal.backend"] = backend
# aliases deste servico: dominios extras roteando p/ o mesmo container.
for a in aliases:
    ah = f"{name}-{folder}-{a}.{project}.{tld}"
    flat[f"alias.{a}.host"] = ah
    flat[f"alias.{a}.url"]  = f"https://{ah}"
def repl(m):
    k = m.group(1).strip()
    if k in flat: return flat[k]
    sys.stderr.write(f"[WARN] placeholder desconhecido: ${{env:{k}}} (mantido)\n"); return m.group(0)
text = re.sub(r"\$\{env:([^}]+)\}", repl, open(os.environ["ES_SRC"]).read())
# Somente arquivos NOVOS chegam ao resolver. Conexões compartilhadas sempre
# recebem as variáveis declaradas, mesmo quando o exemplo ainda usa localhost.
if shared_file and os.path.isfile(shared_file) and connection:
    updates = {variable: flat[f"{engine}.{field}"] for field, variable in connection["env_fields"].items()}
    if "DB_HOST" in updates:
        updates["DB_CONNECTION"] = "mysql" if engine == "mysql" else "pgsql"
        for variable in ("DB_URL", "DATABASE_URL"):
            if re.search(r"^" + variable + "=", text, flags=re.M):
                updates[variable] = flat[f"{engine}.url"]
    for variable, value in updates.items():
        pattern = r"^" + variable + r"=.*$"
        if re.search(pattern, text, flags=re.M):
            text = re.sub(pattern, lambda m: variable + "=" + value, text, flags=re.M)
        else:
            text = text.rstrip("\n") + "\n" + variable + "=" + value + "\n"
if redis_connection:
    updates = {variable: flat[f"redis.{field}"] for field, variable in redis_connection["env_fields"].items()}
    if re.search(r"^REDIS_URL=", text, flags=re.M):
        updates["REDIS_URL"] = flat["redis.url"]
    for variable, value in updates.items():
        pattern = r"^" + variable + r"=.*$"
        if re.search(pattern, text, flags=re.M):
            text = re.sub(pattern, lambda m: variable + "=" + value, text, flags=re.M)
        else:
            text = text.rstrip("\n") + "\n" + variable + "=" + value + "\n"
open(os.environ["ES_DST"], "w").write(text)
os.chmod(os.environ["ES_DST"], 0o600)
PY
}

# ─── Infra do PROJETO (DNS wildcard + certificado) — new/update autorizado ──
# Por-projeto e duradoura: wildcard DNS *.<projeto>.<tld>, resolver do macOS e o
# CERTIFICADO wildcard *.<projeto>.<tld> que cobre TODOS os ambientes/subdominios
# do projeto. O cert vai na pasta compartilhada do Traefik global (via dynamic
# config com watch). Requer sudo na 1a vez (dnsmasq/resolver). Idempotente.
ensure_project_infra() {
    require_shared_infra_authorization
    local project="$1" tld="$2"
    local domain="${project}.${tld}"
    local certs_dir="$TRAEFIK_STATE/certs" dyn_dir="$TRAEFIK_STATE/dynamic"
    mkdir -p "$certs_dir" "$dyn_dir"
    step "Infra do projeto (${domain})"

    command -v dnsmasq >/dev/null 2>&1 || { info "Instalando dnsmasq..."; brew install dnsmasq; }
    local conf; conf="$(brew --prefix)/etc/dnsmasq.conf"
    if ! grep -q "address=/${domain}/127.0.0.1" "$conf" 2>/dev/null; then
        echo "address=/${domain}/127.0.0.1" >> "$conf"
        info "Reiniciando dnsmasq (sudo, porta 53)"; sudo brew services restart dnsmasq
        ok "Wildcard *.${domain} -> 127.0.0.1"
    else ok "Wildcard *.${domain} ja configurado"; fi

    if [ ! -f "/etc/resolver/${domain}" ]; then
        info "Criando /etc/resolver/${domain} (sudo)"
        sudo mkdir -p /etc/resolver
        sudo sh -c "echo 'nameserver 127.0.0.1' > /etc/resolver/${domain}"
        ok "Resolver criado"
    fi

    command -v mkcert >/dev/null 2>&1 || { info "Instalando mkcert..."; brew install mkcert; }
    # (Re)gera o cert + o dynamic do projeto se faltar QUALQUER um dos dois. O
    # dynamic e o que poe o cert no pool de SNI do Traefik (sem ele -> default cert
    # = "certificado invalido" no navegador). Generico: deriva de ${project}/${domain}.
    if [ ! -f "$certs_dir/${project}.pem" ] || [ ! -f "$dyn_dir/${project}.yml" ]; then
        mkcert -install
        [ -f "$certs_dir/${project}.pem" ] || \
            ( cd "$certs_dir" && mkcert -cert-file "${project}.pem" -key-file "${project}-key.pem" "*.${domain}" "${domain}" )
        CERT_FILE="/certs/${project}.pem" KEY_FILE="/certs/${project}-key.pem" \
        RENDER_VARS='${CERT_FILE} ${KEY_FILE}' render_template traefik.dynamic.yml.tpl "$dyn_dir/${project}.yml"
        ok "Certificado *.${domain} pronto (cobre todos os ambientes/subdominios do projeto)"
        # macOS: o file-watch do Traefik sobre bind mount NAO recebe eventos de
        # inotify (limitacao do FS de VM — vale p/ OrbStack e Docker Desktop). Se o
        # Traefik global ja estiver de pe, ele nunca carrega o cert novo -> recarrega
        # explicitamente. No-op se ainda nao existe (o ensure_traefik sobe depois e le o /dynamic no boot).
        local running
        running="$(docker ps --format '{{.Names}}')"
        if printf '%s\n' "$running" | grep -Fxq "$ENVSTACK_TRAEFIK"; then
            docker restart "$ENVSTACK_TRAEFIK" >/dev/null
            ok "Traefik recarregado (cert no pool de SNI)"
        fi
    else ok "Certificado *.${domain} ja existe"; fi
}

# ─── Traefik GLOBAL unico (rede + container) — leve, sem sudo ──────────────
# Compartilhado por TODOS os projetos, sempre em 80/443. Criado uma unica vez.
# Le os certs/dynamic da pasta compartilhada (watch), entao basta o cert do
# projeto existir ali para o HTTPS daquele projeto funcionar.
ensure_traefik() {
    require_shared_infra_authorization
    local certs_dir="$TRAEFIK_STATE/certs" dyn_dir="$TRAEFIK_STATE/dynamic"
    mkdir -p "$certs_dir" "$dyn_dir"
    local networks containers
    networks="$(docker network ls --format '{{.Name}}')"
    if ! printf '%s\n' "$networks" | grep -Fxq "$ENVSTACK_PROXY"; then
        docker network create "$ENVSTACK_PROXY" >/dev/null
        ok "Rede $ENVSTACK_PROXY criada"
    fi
    containers="$(docker ps -a --format '{{.Names}}')"
    if printf '%s\n' "$containers" | grep -Fxq "$ENVSTACK_TRAEFIK"; then
        docker start "$ENVSTACK_TRAEFIK" >/dev/null
        ok "Traefik global de pe (${ENVSTACK_TRAEFIK})"
    else
        if lsof -nP -iTCP:443 -sTCP:LISTEN >/dev/null 2>&1; then
            warn "Porta 443 em uso. Se for um proxy proprio do projeto, pare-o para o Traefik global assumir 80/443."
        fi
        info "Iniciando Traefik global (${ENVSTACK_TRAEFIK})..."
        docker run -d --name "$ENVSTACK_TRAEFIK" --restart unless-stopped \
            --network "$ENVSTACK_PROXY" -p 80:80 -p 443:443 \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            -v "$certs_dir:/certs:ro" -v "$dyn_dir:/dynamic:ro" \
            traefik:v3 \
            --providers.docker=true --providers.docker.exposedbydefault=false \
            --entrypoints.web.address=:80 --entrypoints.websecure.address=:443 \
            --providers.file.directory=/dynamic --providers.file.watch=true >/dev/null \
            && ok "Traefik global iniciado" \
            || fail "Falha ao iniciar Traefik global (porta 80/443 ocupada?). Pare o que estiver usando e rode de novo."
    fi
}

# Infra completa, somente sob autorizacao explicita.
ensure_infra() { ensure_project_infra "$1" "$2"; ensure_traefik; }
