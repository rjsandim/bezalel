#!/usr/bin/env bash
# Uso: destroy.sh <nome> --confirm <projeto>/<nome> [--keep-worktree]
# Falhas preservam o registro local; nunca remove por prefixo ou usa --force.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq docker python3
ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
shift
KEEP_WT=false
CONFIRM=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --keep-worktree) KEEP_WT=true; shift ;;
        --confirm)
            [ "$#" -ge 2 ] || fail "Informe o alvo depois de --confirm."
            CONFIRM="$2"; shift 2 ;;
        *) fail "Opcao desconhecida. Use --confirm projeto/ambiente e, opcionalmente, --keep-worktree." ;;
    esac
done
ROOT="$(repo_root)"
PROJECT="$(project_name)"
[ "$CONFIRM" = "$PROJECT/$ENV_NAME" ] || fail "Confirme explicitamente a exclusao com --confirm $PROJECT/$ENV_NAME."
apply_docker_engine
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
[ -f "$COMPOSE" ] || fail "Compose salvo ausente; nenhuma remocao por prefixo sera tentada."
validate_state_owner "$STATE_DIR"

# Preflight antes dos volumes: nao descarta arquivos locais ou commits.
if [ "$KEEP_WT" = false ]; then
    validate_worktree "$WORKTREE_DIR" "$ENV_NAME"
    [ -z "$(git -C "$WORKTREE_DIR" status --porcelain --untracked-files=all --ignored=matching)" ] || fail "Worktree tem arquivos alterados, nao rastreados ou ignorados. Preserve-os ou use --keep-worktree."
    WORKTREE_BRANCH="$(git -C "$WORKTREE_DIR" symbolic-ref --quiet --short HEAD)"
    BASE_REF="$(base_ref)"
    git -C "$ROOT" merge-base --is-ancestor "$WORKTREE_BRANCH" "$BASE_REF" || fail "Branch contem commits nao integrados na base. Preserve a worktree."
fi
docker compose -f "$COMPOSE" config --quiet
python3 "$SCRIPT_DIR/check_destroy.py" "$COMPOSE" "$PROJECT-$ENV_NAME"
step "Removendo ambiente confirmado: $PROJECT/$ENV_NAME"
docker compose -f "$COMPOSE" down -v
if [ "$KEEP_WT" = false ]; then
    git -C "$ROOT" worktree remove "$WORKTREE_DIR"
    git -C "$ROOT" branch -d "$WORKTREE_BRANCH"
else
    info "Worktree e branch preservadas; volumes do ambiente removidos."
fi
if [ -f "$STATE_DIR/shared-database.json" ]; then
    info "Database/usuário compartilhados preservados no registro do pool; nenhuma exclusão SQL executada."
fi
if [ -f "$STATE_DIR/shared-redis.json" ]; then
    info "Redis compartilhado, dados, usuários e alocações preservados no pool."
fi
rm -rf "$STATE_DIR"
ok "Ambiente removido; todas as etapas solicitadas concluiram sem erro."
