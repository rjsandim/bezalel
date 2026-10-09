#!/usr/bin/env bash
# update.sh — regenera o compose e reconstroi os servicos selecionados.
# Preserva .env, worktree e volumes. Edite .env existentes explicitamente.
#
# Uso: update.sh <nome> [servico...|--all]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq envsubst docker

ENV_NAME="${1:-}"; validate_env_name "$ENV_NAME"
ROOT="$(repo_root)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
[ -d "$WORKTREE_DIR" ] || fail "Ambiente '$ENV_NAME' nao existe. Use: /env new $ENV_NAME"

# Regerar tudo a partir do manifesto e re-subir (new.sh e idempotente).
shift
export ENVSTACK_UPDATE=1
exec bash "$SCRIPT_DIR/new.sh" "$ENV_NAME" "$@"
