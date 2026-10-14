#!/usr/bin/env bash
# vars.sh — lista os placeholders ${env:...} que a skill resolve nos .env.example.
# Mostra exemplos ja resolvidos com os nomes reais do projeto (do manifesto), com
# <env> = nome passado no `new` e <pasta> = a pasta do servico onde o .env vive.
#
# Uso: vars.sh   (alias do subcomando '/env config')

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq

MANIFEST="$(manifest_path)"
[ -f "$MANIFEST" ] || fail "Manifesto nao encontrado — rode '/env init' primeiro."

ROOT="$(repo_root)"
PROJECT="$(project_name)"; TLD="$(project_tld)"
DOMAIN="${PROJECT}.${TLD}"
DB_ENGINE="$(manifest_get '.database')"; case "$DB_ENGINE" in mysql) ;; *) DB_ENGINE="postgres";; esac
if [ "$DB_ENGINE" = "mysql" ]; then
    DB_CONN="mysql"; DB_HOST="mysql"; DB_PORT="3306"; DB_URL="mysql://${PROJECT}:secret@mysql:3306/<pasta>"
else
    DB_CONN="pgsql"; DB_HOST="postgres"; DB_PORT="5432"; DB_URL="postgresql://${PROJECT}:secret@postgres:5432/<pasta>"
fi

DB_NAME_EXAMPLE='<pasta>   (1 database por servico com database:true)'
DB_USER_EXAMPLE="$PROJECT"; DB_PASS_EXAMPLE='secret'
if [ "$(manifest_get '.database_mode')" = 'shared' ]; then
    DB_HOST='<host do pool salvo no estado local>'
    DB_NAME_EXAMPLE='<database exclusivo de projeto/ambiente/servico>'
    DB_USER_EXAMPLE='<usuario exclusivo do servico>'
    DB_PASS_EXAMPLE='<gerada localmente; nunca exibida>'
    DB_URL='<DSN exclusiva gerada localmente; nunca exibida>'
fi

# Primeiro servico php (= backend) e lista de pastas.
COUNT="$(yq -r '.services | length' "$MANIFEST")"
BACKEND=""; FOLDERS=""
for i in $(seq 0 $((COUNT - 1))); do
    f="$(yq -r ".services[$i].folder" "$MANIFEST")"; t="$(yq -r ".services[$i].type" "$MANIFEST")"
    FOLDERS+="$f "; [ -z "$BACKEND" ] && [ "$t" = "php" ] && BACKEND="$f"
done

p() { printf "  ${BLUE}%-26s${NC} %s\n" "$1" "$2"; }

step "Placeholders \${env:...} — projeto '${PROJECT}' (dominio *.${DOMAIN})"
echo "Use nos .env.example (em .envstack/<pasta>.env.example ou na pasta do app)."
echo "<env> = nome passado no '/env new'   ·   <pasta> = a pasta deste servico."

echo -e "\n${BOLD}Infra do ambiente${NC}"
p '${env:project}'        "$PROJECT"
p '${env:name}'           "<env>"
p '${env:db.connection}'  "$DB_CONN"
p '${env:db.host}'        "$DB_HOST"
p '${env:db.port}'        "$DB_PORT"
p '${env:db.db}'          "$DB_NAME_EXAMPLE"
p '${env:db.user}'        "$DB_USER_EXAMPLE"
p '${env:db.password}'    "$DB_PASS_EXAMPLE"
p '${env:db.url}'         "$DB_URL"
p '${env:redis.host}'     "redis"
p '${env:redis.port}'     "6379"
p '${env:redis.url}'      "redis://redis:6379"

echo -e "\n${BOLD}Este servico (self)${NC}"
p '${env:url.self}'       "https://<env>-<pasta>.${DOMAIN}"
p '${env:host.self}'      "<env>-<pasta>.${DOMAIN}"
p '${env:internal.self}'  "<pasta>"

if [ -n "$BACKEND" ]; then
    echo -e "\n${BOLD}Backend (1o servico php = ${BACKEND})${NC}"
    p '${env:url.backend}'      "https://<env>-${BACKEND}.${DOMAIN}"
    p '${env:host.backend}'     "<env>-${BACKEND}.${DOMAIN}"
    p '${env:internal.backend}' "$BACKEND"
fi

echo -e "\n${BOLD}Por servico${NC} (1 por pasta: ${FOLDERS})"
p '${env:url.<pasta>}'      "https://<env>-<pasta>.${DOMAIN}"
p '${env:host.<pasta>}'     "<env>-<pasta>.${DOMAIN}"
p '${env:internal.<pasta>}' "<pasta>"

# Aliases declarados em algum servico.
HAS_ALIAS=false
for i in $(seq 0 $((COUNT - 1))); do
    f="$(yq -r ".services[$i].folder" "$MANIFEST")"
    al="$(yq -r ".services[$i].aliases // [] | join(\" \")" "$MANIFEST")"
    [ -z "$al" ] && continue
    $HAS_ALIAS || { echo -e "\n${BOLD}Aliases (multi-dominio)${NC} — em services[].aliases"; HAS_ALIAS=true; }
    echo -e "  ${YELLOW}${f}:${NC} ${al}"
    for a in $al; do
        p "\${env:alias.${a}.url}"  "https://<env>-${f}-${a}.${DOMAIN}"
        p "\${env:alias.${a}.host}" "<env>-${f}-${a}.${DOMAIN}"
    done
done
$HAS_ALIAS || echo -e "\n${BOLD}Aliases${NC}: nenhum. Adicione 'aliases: [unidades, admin]' a um servico no manifesto."

# ─── Defaults por tipo: o que o `init` semeia em cada .env.example novo ────────
echo -e "\n${BOLD}Defaults por tipo de servico${NC} (semeados pelo '/env init' em .env.example novo)"
SEEN_TPLS=""   # bash 3.2 (macOS) nao tem array associativo — dedup por string
for i in $(seq 0 $((COUNT - 1))); do
    f="$(yq -r ".services[$i].folder" "$MANIFEST")"; t="$(yq -r ".services[$i].type" "$MANIFEST")"
    case "$t" in
        php)  label="php (Laravel)"; tpl="env.php.tpl" ;;
        node) fw="$(detect_node_framework "$ROOT/$f")"
              if [ "$fw" = "next" ]; then label="node / Next.js"; tpl="env.next.tpl"
              else label="node / Vite"; tpl="env.node.tpl"; fi ;;
        *)    continue ;;
    esac
    case "$SEEN_TPLS" in *"|$tpl|"*) continue ;; esac
    SEEN_TPLS="${SEEN_TPLS}|$tpl|"
    echo -e "\n  ${YELLOW}${label}${NC}  →  ${tpl}"
    grep -vE '^[[:space:]]*#|^[[:space:]]*$' "$TPL_DIR/$tpl" | while IFS= read -r line; do
        key="${line%%=*}"; val="${line#*=}"
        printf "    %-38s = %s\n" "$key" "$val"
    done
done
echo ""
