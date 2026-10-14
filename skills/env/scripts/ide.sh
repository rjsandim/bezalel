#!/usr/bin/env bash
# ide.sh — gera config de IDE na worktree do ambiente:
#   .idea/php.xml         -> um PHP Server (path mapping /app -> pasta) por servico
#                            PHP, deixando o PhpStorm pronto p/ Xdebug.
#   .idea/dataSources.xml -> uma conexao de banco (DataGrip/JetBrains) por servico
#                            com database:true, apontando p/ localhost:<porta>.
# A worktree e efemera, entao os arquivos sao sobrescritos.
#
# Uso: ide.sh <nome>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq envsubst

ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
ROOT="$(repo_root)"; PROJECT="$(project_name)"; TLD="$(project_tld)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
MANIFEST="$(manifest_path)"
[ -d "$WORKTREE_DIR" ] || fail "Ambiente '$ENV_NAME' nao existe."

# Varre servicos: PHP (p/ php.xml) e os com database:true (p/ dataSources.xml)
PHP_FOLDERS=(); PHP_LEVEL=""; DB_FOLDERS=()
COUNT="$(yq -r '.services | length' "$MANIFEST")"
for i in $(seq 0 $((COUNT - 1))); do
    [ "$(yq -r ".services[$i].database" "$MANIFEST")" = "true" ] && \
        DB_FOLDERS+=("$(yq -r ".services[$i].folder" "$MANIFEST")")
    [ "$(yq -r ".services[$i].type" "$MANIFEST")" = "php" ] || continue
    PHP_FOLDERS+=("$(yq -r ".services[$i].folder" "$MANIFEST")")
    [ -n "$PHP_LEVEL" ] || PHP_LEVEL="$(yq -r ".services[$i].version // \"8.3\"" "$MANIFEST")"
done

IDEA="$WORKTREE_DIR/.idea"; mkdir -p "$IDEA"

# ─── dataSources.xml: uma conexao por database, em localhost:<porta> ───
if [ ${#DB_FOLDERS[@]} -gt 0 ]; then
    DB_ENGINE="$(manifest_get '.database')"
    case "$DB_ENGINE" in
        mysql) DRIVER_REF="mysql.8"; JDBC_DRIVER="com.mysql.cj.jdbc.Driver"; JDBC_SCHEME="mysql";;
        *)     DRIVER_REF="postgresql"; JDBC_DRIVER="org.postgresql.Driver"; JDBC_SCHEME="postgresql";;
    esac
    DB_HOST_PORT="$(db_host_port "$ENV_NAME")"
    PG_USER="$(project_name)"
    DSXML="$IDEA/dataSources.xml"
    export PG_USER DRIVER_REF JDBC_DRIVER
    RENDER_VARS='' render_template phpstorm.datasource.head.tpl /dev/stdout > "$DSXML"
    for folder in "${DB_FOLDERS[@]}"; do
        DB_NAME="$folder"
        shared="$SKILL_DIR/state/$PROJECT/$ENV_NAME/shared-database.json"
        if [ -f "$shared" ]; then
            read -r DB_HOST_PORT DB_NAME PG_USER < <(python3 - "$shared" "$folder" <<'PYSHARED'
import json, sys
s = json.load(open(sys.argv[1])); c = s["connections"][sys.argv[2]]
print(s["pool"]["port"], c["db"], c["user"])
PYSHARED
            )
        fi
        export DS_NAME="${ENV_NAME}-${folder}@localhost" \
               DS_UUID="$(uuidgen | tr '[:upper:]' '[:lower:]')" \
               JDBC_URL="jdbc:${JDBC_SCHEME}://localhost:${DB_HOST_PORT}/${DB_NAME}"
        RENDER_VARS='${DS_NAME} ${DS_UUID} ${DRIVER_REF} ${JDBC_DRIVER} ${JDBC_URL} ${PG_USER}' \
            render_template phpstorm.datasource.tpl /dev/stdout >> "$DSXML"
    done
    RENDER_VARS='' render_template phpstorm.datasource.tail.tpl /dev/stdout >> "$DSXML"
    ok "DataGrip: .idea/dataSources.xml (${#DB_FOLDERS[@]} conexao(oes) -> localhost:${DB_HOST_PORT}, user ${PG_USER})"
fi

# ─── Xdebug (servicos PHP) ───
# IMPORTANTE: o PhpStorm guarda os PHP Servers (com path mapping) e a porta de
# debug no **workspace.xml**, nao no php.xml. Se o server nao estiver la, o debug
# conecta mas falha com "Server with name '<env>-<pasta>' doesn't exist". Entao:
#   php.xml       -> so o language level.
#   workspace.xml -> PhpServers (1 por servico PHP) + PhpDebugGeneral (porta 9003).
# O server e casado pelo NOME enviado em PHP_IDE_CONFIG=serverName=<env>-<pasta>
# (fixo por container) — cobre o dominio principal e todos os aliases.
if [ ${#PHP_FOLDERS[@]} -gt 0 ]; then
    export PHP_LEVEL
    RENDER_VARS='${PHP_LEVEL}' render_template phpstorm.php.tpl /dev/stdout > "$IDEA/php.xml"

    # Monta o bloco PhpServers (1 server por servico PHP, path mapping /app -> pasta)
    SERVERS_FILE="$(mktemp)"
    RENDER_VARS='' render_template phpstorm.servers.head.tpl /dev/stdout > "$SERVERS_FILE"
    for folder in "${PHP_FOLDERS[@]}"; do
        export FOLDER="$folder" \
               SVC_HOST="${ENV_NAME}-${folder}.${PROJECT}.${TLD}" \
               SERVER_NAME="${ENV_NAME}-${folder}" \
               SERVER_ID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
        RENDER_VARS='${FOLDER} ${SVC_HOST} ${SERVER_NAME} ${SERVER_ID}' \
            render_template phpstorm.server.tpl /dev/stdout >> "$SERVERS_FILE"
    done
    RENDER_VARS='' render_template phpstorm.servers.tail.tpl /dev/stdout >> "$SERVERS_FILE"

    # Splice no workspace.xml: troca o PhpServers pelo nosso e garante o
    # PhpDebugGeneral (porta 9003 = a que o container disca). Preserva o resto do
    # arquivo (estado do PhpStorm). Cria do zero se nao existir.
    WS="$IDEA/workspace.xml"; XDEBUG_PORT=9003
    python3 - "$WS" "$SERVERS_FILE" "$XDEBUG_PORT" <<'PY'
import sys, re
ws, servers_file, port = sys.argv[1], sys.argv[2], sys.argv[3]
servers = open(servers_file).read().rstrip('\n') + '\n'
try:
    s = open(ws).read()
except FileNotFoundError:
    s = '<?xml version="1.0" encoding="UTF-8"?>\n<project version="4">\n</project>\n'
# remove qualquer PhpServers existente (sera substituido pelo nosso)
s = re.sub(r'[ \t]*<component name="PhpServers">.*?</component>\n?', '', s, flags=re.S)
add = servers
if 'name="PhpDebugGeneral"' not in s:   # so adiciona a porta de debug se faltar
    add += (f'  <component name="PhpDebugGeneral">\n'
            f'    <xdebug_debug_ports port="{port}" />\n  </component>\n')
i = s.rfind('</project>')
s = (s[:i] + add + s[i:]) if i != -1 else \
    '<?xml version="1.0" encoding="UTF-8"?>\n<project version="4">\n' + add + '</project>\n'
open(ws, 'w').write(s)
PY
    rm -f "$SERVERS_FILE"
    ok "PhpStorm: php.xml + workspace.xml (PhpServers ${#PHP_FOLDERS[@]} + porta de debug ${XDEBUG_PORT})"
    echo "  Abra a worktree, clique em 'Start Listening for PHP Debug Connections' (porta ${XDEBUG_PORT}) e ponha o breakpoint."
else
    info "Sem servicos PHP — php.xml/Xdebug nao se aplica."
fi
