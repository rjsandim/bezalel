#!/usr/bin/env bash
# destroy.sh — derruba TUDO de um ambiente: containers, volumes, imagens locais,
# rede interna, state efemero, worktree e branch. Um comando, apaga tudo.
#
# Uso: destroy.sh <nome> [--keep-worktree]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git docker

ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
KEEP_WT=false; [ "${2:-}" = "--keep-worktree" ] && KEEP_WT=true

ROOT="$(repo_root)"
PROJECT="$(project_name)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"

step "Destruindo ambiente '${ENV_NAME}' (projeto ${PROJECT})"

if [ -f "$COMPOSE" ]; then
    docker compose -f "$COMPOSE" down -v --rmi local --remove-orphans 2>/dev/null \
        && ok "Containers, volumes e rede interna removidos" || warn "Nada a derrubar via compose"
else
    warn "Compose nao encontrado — removendo por prefixo"
    docker ps -aq --filter "name=^${PROJECT}-${ENV_NAME}-" | xargs -r docker rm -f >/dev/null 2>&1 || true
    docker network rm "${PROJECT}-${ENV_NAME}-internal" >/dev/null 2>&1 || true
fi

[ -d "$STATE_DIR" ] && rm -rf "$STATE_DIR" && ok "State efemero removido"

if [ "$KEEP_WT" = false ] && [ -d "$WORKTREE_DIR" ]; then
    git -C "$ROOT" worktree remove "$WORKTREE_DIR" --force 2>/dev/null \
        && ok "Worktree removida" || warn "Falha ao remover worktree (arquivos nao commitados?)"
    if git -C "$ROOT" show-ref --verify --quiet "refs/heads/$ENV_NAME"; then
        git -C "$ROOT" branch -D "$ENV_NAME" >/dev/null 2>&1 && ok "Branch ${ENV_NAME} removida" || true
    fi
elif [ "$KEEP_WT" = true ]; then
    info "Worktree mantida (--keep-worktree): .worktrees/${ENV_NAME}"
fi

echo ""
echo -e "${GREEN}Ambiente '${ENV_NAME}' destruido.${NC}"
