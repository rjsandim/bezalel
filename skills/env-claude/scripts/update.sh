#!/usr/bin/env bash
# update.sh — re-resolve os .env e re-sobe um ambiente existente, sem recriar
# a worktree. Use apos editar um .env.example, um Dockerfile ou o manifesto.
#
# Uso: update.sh <nome>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq envsubst docker

ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
ROOT="$(repo_root)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
[ -d "$WORKTREE_DIR" ] || fail "Ambiente '$ENV_NAME' nao existe. Use: /env new $ENV_NAME"

# Regerar tudo a partir do manifesto e re-subir (new.sh e idempotente).
exec "$SCRIPT_DIR/new.sh" "$ENV_NAME"
