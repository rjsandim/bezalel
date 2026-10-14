#!/usr/bin/env bash
# new.sh — instancia um ambiente efemero a partir do manifesto versionado.
# Cria worktree (da base configurada/detectada), monta o compose, resolve os
# .env de cada pasta e inicia a selecao configurada no manifesto.
#
# Uso: new.sh <nome> [servico...|--all]
# Var: ENV_DRY_RUN=1  -> nao mexe em infra/containers (so gera artefatos)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
source "$SCRIPT_DIR/services.sh"
require_tools git yq jq envsubst docker python3

ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
shift
apply_docker_engine
[ "${ENV_DRY_RUN:-0}" = 1 ] || require_shared_infra_authorization

ROOT="$(repo_root)"
PROJECT="$(project_name)"; TLD="$(project_tld)"
PG_USER="$PROJECT"; PG_PASS="secret"
PROXY_NET="$ENVSTACK_PROXY"   # rede do Traefik global unico (compartilhada)
MANIFEST="$(manifest_path)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
[ ! -d "$STATE_DIR" ] || validate_state_owner "$STATE_DIR"

# Repetir new e aditivo, sem reescrever configuracoes de um ambiente existente.
if [ -f "$COMPOSE" ] && [ "${ENVSTACK_UPDATE:-0}" != '1' ]; then
    [ "${ENV_DRY_RUN:-0}" != '1' ] || { info "Compose existente preservado: $COMPOSE"; exit 0; }
    exec bash "$SCRIPT_DIR/ctl.sh" start "$ENV_NAME" "$@"
fi

COUNT="$(yq -r '.services | length' "$MANIFEST")"
[ "$COUNT" -gt 0 ] || fail "Manifesto sem servicos — rode '/env init'."

# Engine de banco do stack (manifesto .database). Default: postgres.
DB_ENGINE="$(manifest_get '.database')"
case "$DB_ENGINE" in mysql) DB_SERVICE="mysql";; *) DB_ENGINE="postgres"; DB_SERVICE="postgres";; esac

mkdir -p "$STATE_DIR"
printf '%s\n' "$ROOT" > "$STATE_DIR/project-root"
printf '%s\n' "$DOCKER_CONTEXT" > "$STATE_DIR/docker-context"
python3 "$SCRIPT_DIR/shared_db.py" prepare "$MANIFEST" "$ROOT" "$PROJECT" "$ENV_NAME" "$DOCKER_CONTEXT" "$STATE_DIR"
export ES_SHARED_DB_FILE="$STATE_DIR/shared-database.json"

# Lista "folder:type" de todos os servicos (para placeholders cruzados)
SERVICES=""
for i in $(seq 0 $((COUNT - 1))); do
    SERVICES+="$(yq -r ".services[$i].folder" "$MANIFEST"):$(yq -r ".services[$i].type" "$MANIFEST") "
done
export ES_PROJECT="$PROJECT" ES_NAME="$ENV_NAME" ES_TLD="$TLD" \
       ES_PG_USER="$PG_USER" ES_PG_PASS="$PG_PASS" ES_SERVICES="$SERVICES" ES_DB_ENGINE="$DB_ENGINE"

step "Ambiente '${ENV_NAME}' — projeto '${PROJECT}' (*.${PROJECT}.${TLD})"

# ─── 1. Worktree a partir de referencia local verificavel ──────
if [ ! -d "$WORKTREE_DIR" ]; then
    if git -C "$ROOT" show-ref --verify --quiet "refs/heads/$ENV_NAME"; then
        git -C "$ROOT" worktree add "$WORKTREE_DIR" "$ENV_NAME"
    else
        BASE_REF="$(base_ref)"
        git -C "$ROOT" worktree add "$WORKTREE_DIR" -b "$ENV_NAME" "$BASE_REF"
    fi
    ok "Worktree .worktrees/$ENV_NAME (branch $ENV_NAME)"
else ok "Worktree ja existe"; fi
validate_worktree "$WORKTREE_DIR" "$ENV_NAME"
mkdir -p "$STATE_DIR"
git -C "$WORKTREE_DIR" symbolic-ref --quiet --short HEAD > "$STATE_DIR/worktree-branch"

# ─── 2. Infra ──────────────────────────────────────────────────
# DNS + certificado do projeto sao criados no `init`. Aqui so garantimos o
# Traefik global de pe. Fallback: se a infra do projeto faltar, configura agora.
if [ "${ENV_DRY_RUN:-0}" = "1" ]; then
    warn "DRY-RUN: pulando infra"
else
    if [ ! -f "$TRAEFIK_STATE/certs/${PROJECT}.pem" ]; then
        warn "Infra do projeto ausente — rode '/env init'. Configurando agora..."
        ensure_project_infra "$PROJECT" "$TLD"
    fi
    ensure_traefik
fi

# ─── 3. Compose efemero (concatena templates renderizados) ─────
step "Montando stack"
mkdir -p "$STATE_DIR"
printf '%s\n' "$ROOT" > "$STATE_DIR/project-root"
printf '%s\n' "$DOCKER_CONTEXT" > "$STATE_DIR/docker-context"
COMPOSE_DEST="$COMPOSE"
COMPOSE="$(mktemp "$STATE_DIR/compose.pending.XXXXXX")"
INITDB_PENDING="$(mktemp "$STATE_DIR/initdb.pending.XXXXXX")"
trap 'rm -f "$COMPOSE" "$INITDB_PENDING"' EXIT
DB_HOST_PORT="$(db_host_port "$ENV_NAME")"
if [ -f "$ES_SHARED_DB_FILE" ]; then
    DB_HOST_PORT="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["pool"]["port"])' "$ES_SHARED_DB_FILE")"
fi   # porta do banco no host (IDE conecta por aqui)
export PROJECT ENV_NAME PG_USER PG_PASS PROXY_NET STATE_DIR WORKTREE_DIR ROOT DB_SERVICE DB_HOST_PORT
COMMON_VARS='${PROJECT} ${ENV_NAME} ${PG_USER} ${PG_PASS} ${PROXY_NET} ${STATE_DIR} ${WORKTREE_DIR} ${ROOT} ${DB_HOST_PORT}'
export STARTUP_SERVICES="$(yq -o=json -I=0 '.startup.services // []' "$MANIFEST")"
COMMON_VARS+=' ${STARTUP_SERVICES}'

: > "$COMPOSE"
RENDER_VARS="$COMMON_VARS" render_template compose.head.tpl          /dev/stdout >> "$COMPOSE"
RENDER_VARS="$COMMON_VARS" render_template "compose.${DB_SERVICE}.tpl" /dev/stdout >> "$COMPOSE"
RENDER_VARS="$COMMON_VARS" render_template compose.redis.tpl         /dev/stdout >> "$COMPOSE"

# initdb: um database por servico com database:true
: > "$INITDB_PENDING"
for i in $(seq 0 $((COUNT - 1))); do
    folder="$(yq -r ".services[$i].folder" "$MANIFEST")"
    type="$(yq -r ".services[$i].type" "$MANIFEST")"
    port="$(yq -r ".services[$i].port" "$MANIFEST")"
    has_db="$(yq -r ".services[$i].database" "$MANIFEST")"
    aliases="$(yq -r ".services[$i].aliases // [] | join(\" \")" "$MANIFEST")"
    SVC_HOST="${ENV_NAME}-${folder}.${PROJECT}.${TLD}"

    # Regra Traefik: host principal + cada alias (mesmo container, dominios extras).
    SVC_RULE="Host(\`${SVC_HOST}\`)"
    for a in $aliases; do
        SVC_RULE="${SVC_RULE} || Host(\`${ENV_NAME}-${folder}-${a}.${PROJECT}.${TLD}\`)"
    done

    export FOLDER="$folder" PORT="$port" SVC_HOST="$SVC_HOST" SVC_RULE="$SVC_RULE"
    RENDER_VARS="${COMMON_VARS} \${FOLDER} \${PORT} \${SVC_HOST} \${SVC_RULE} \${DB_SERVICE}" \
        render_template compose.service.tpl /dev/stdout >> "$COMPOSE"

    # Override explicito; ausencia preserva DB + Redis dos manifestos antigos.
    if yq -e ".services[$i] | has(\"depends_on\")" "$MANIFEST" >/dev/null; then
        export SERVICE_DEPS="$(yq -o=json -I=0 ".services[$i].depends_on" "$MANIFEST")"
        yq -i '.services[strenv(FOLDER)].depends_on = (strenv(SERVICE_DEPS) | from_json)' "$COMPOSE"
    fi

    # Um database por servico com database:true (sintaxe conforme o engine).
    if [ "$has_db" = "true" ]; then
        if [ "$DB_SERVICE" = "mysql" ]; then
            printf 'CREATE DATABASE IF NOT EXISTS `%s`;\nGRANT ALL PRIVILEGES ON `%s`.* TO '\''%s'\''@'\''%%'\'';\n' \
                "$folder" "$folder" "$PG_USER" >> "$INITDB_PENDING"
        else
            echo "SELECT 'CREATE DATABASE \"${folder}\"' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${folder}')\\gexec" >> "$INITDB_PENDING"
        fi
    fi
done

RENDER_VARS="$COMMON_VARS" render_template compose.tail.tpl /dev/stdout >> "$COMPOSE"
python3 "$SCRIPT_DIR/shared_db.py" configure "$COMPOSE" "$STATE_DIR"
ok "Compose preparado para validacao"

# ─── 4. Resolver .env de cada pasta ────────────────────────────
step "Resolvendo .env (\${env:...})"
for i in $(seq 0 $((COUNT - 1))); do
    folder="$(yq -r ".services[$i].folder" "$MANIFEST")"
    type="$(yq -r ".services[$i].type" "$MANIFEST")"
    aliases="$(yq -r ".services[$i].aliases // [] | join(\" \")" "$MANIFEST")"
    # Fonte do env (com placeholders ${env:...}): preferir o template versionado
    # em .envstack/<pasta>.env.example; senao, o .env.example real da pasta.
    if [ -f "$ROOT/.envstack/$folder.env.example" ]; then
        example="$ROOT/.envstack/$folder.env.example"
    else
        example="$ROOT/$folder/.env.example"
    fi
    if [ -f "$WORKTREE_DIR/$folder/.env" ]; then
        ok "${folder}/.env existente preservado"
    elif [ -f "$example" ]; then
        mkdir -p "$WORKTREE_DIR/$folder"
        resolve_env "$example" "$WORKTREE_DIR/$folder/.env" "$folder" "$type" "$aliases"
        ok "${folder}/.env  (fonte: ${example#$ROOT/})"
    else warn "${folder}: sem .env.example (nem em .envstack/ nem na pasta) — pulado"; fi
done

# ─── 4b. Config do PhpStorm (path mappings) p/ servicos PHP ────
bash "$SCRIPT_DIR/ide.sh" "$ENV_NAME" || warn "Falha ao gerar config do PhpStorm (ignorado)"

# ─── 5. Validar e subir somente o necessario ────────────────────
dc config --quiet
mv "$COMPOSE" "$COMPOSE_DEST"
mv "$INITDB_PENDING" "$STATE_DIR/initdb.sql"
printf '%s\n' "$ROOT" > "$STATE_DIR/project-root"
printf '%s\n' "$DOCKER_CONTEXT" > "$STATE_DIR/docker-context"
trap - EXIT
COMPOSE="$COMPOSE_DEST"
if [ "${ENV_DRY_RUN:-0}" = "1" ]; then warn "DRY-RUN: nao subindo containers. Compose em $COMPOSE"; exit 0; fi
start_services update "$@"

echo ""
echo -e "${GREEN}━━━ Ambiente '${ENV_NAME}': URLs disponiveis ao iniciar cada servico ━━━${NC}"
for i in $(seq 0 $((COUNT - 1))); do
    folder="$(yq -r ".services[$i].folder" "$MANIFEST")"
    echo -e "  ${BLUE}${folder}:${NC} https://${ENV_NAME}-${folder}.${PROJECT}.${TLD}"
    aliases="$(yq -r ".services[$i].aliases // [] | join(\" \")" "$MANIFEST")"
    for a in $aliases; do
        echo -e "      ${BLUE}↳ ${a}:${NC} https://${ENV_NAME}-${folder}-${a}.${PROJECT}.${TLD}"
    done
done
echo -e "  ${BLUE}${DB_SERVICE}:${NC} localhost:${DB_HOST_PORT} — conexao da IDE em .idea/dataSources.xml"
echo -e "  ${YELLOW}Ligar todos:${NC} /env start ${ENV_NAME} --all"
echo -e "  ${YELLOW}Parar preservando trabalho:${NC} /env stop ${ENV_NAME}"
echo ""
