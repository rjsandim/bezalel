#!/usr/bin/env bash
# detect.sh — ETAPA 1 do init. Detecta pastas/tipos/versoes e escreve um
# rascunho do manifesto em .envstack/stack.yaml. NAO gera Dockerfiles ainda —
# a ideia e voce (e a LLM) revisarem/ajustarem o manifesto antes de materializar.
#
# Uso: detect.sh [pasta ...]   (sem args = todas as pastas com composer.json/package.json)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq jq

ROOT="$(repo_root)"
PROJECT="$(basename "$ROOT")"
ENVSTACK="$ROOT/.envstack"
MANIFEST="$ENVSTACK/stack.yaml"
mkdir -p "$ENVSTACK"

# Pastas-alvo
FOLDERS=()
if [ "$#" -gt 0 ]; then FOLDERS=("$@")
else
    for d in "$ROOT"/*/; do
        d="$(basename "$d")"; [ "$d" = ".envstack" ] && continue
        t="$(detect_folder_type "$ROOT/$d")"; [ "$t" = "unknown" ] && continue
        FOLDERS+=("$d")
    done
fi
[ ${#FOLDERS[@]} -gt 0 ] || fail "Nenhuma pasta com projeto detectado (composer.json/package.json)."

# Manifesto base (a partir do template). Semeia o engine docker ativo agora
# (orbstack | docker-desktop | auto) — editavel depois no proprio manifesto.
ENGINE="$(detect_docker_engine)"
PROJECT="$PROJECT" ENGINE="$ENGINE" RENDER_VARS='${PROJECT} ${ENGINE}' \
    render_template stack.yaml.tpl "$MANIFEST"

# Preenche services[] via yq. Falha em uma pasta nunca aborta o init: a pasta
# e ignorada, registrada em IGNORED e reportada no fim.
IGNORED=()
ignore() { warn "$1 — pasta ignorada"; IGNORED+=("$2"); }

for folder in "${FOLDERS[@]}"; do
    [ -d "$ROOT/$folder" ] || { ignore "Pasta inexistente: $folder" "$folder"; continue; }
    type="$(detect_folder_type "$ROOT/$folder")"
    if [ "$type" = "unknown" ]; then
        ignore "Tipo de projeto nao reconhecido em '$folder' (sem composer.json/package.json)" "$folder"; continue
    fi
    version="$(detect_version "$ROOT/$folder" "$type" || true)"
    port="$(default_port_for_type "$type")"
    framework=""
    # Por padrao so o backend php (Laravel) ganha database; node costuma ser
    # frontend (Vite/Next) e nao acessa banco — flip p/ true no manifesto se for API.
    case "$type" in
        php)  has_db=true ;;
        node) has_db=false
              framework="$(detect_node_framework "$ROOT/$folder")"
              [ "$framework" = "next" ] && port=3000 ;;
        *)    has_db=false ;;
    esac

    if ! f="$folder" t="$type" v="$version" p="$port" db="$has_db" \
        yq -i '.services += [{
            "folder": strenv(f), "type": strenv(t),
            "version": strenv(v), "port": (strenv(p)|tonumber),
            "database": (strenv(db) == "true")
        }]' "$MANIFEST"; then
        ignore "Falha ao registrar '$folder' no manifesto" "$folder"; continue
    fi

    echo "  • $folder → type=$type${framework:+/$framework} version=${version:-?} port=$port db=$has_db"
done

echo ""
ok "Manifesto rascunho: .envstack/stack.yaml"
if [ ${#IGNORED[@]} -gt 0 ]; then
    warn "Ignoradas (${#IGNORED[@]}): ${IGNORED[*]} — nao entraram no manifesto"
fi
echo "Revise/ajuste versoes e portas. Depois materialize com: scripts/init.sh"
