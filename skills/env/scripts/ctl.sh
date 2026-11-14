#!/usr/bin/env bash
# Uso: ctl.sh <start|ensure|stop|restart|status|check> <nome> [servico...|--all]
# start/ensure acrescentam servicos; stop/restart operam no ambiente ativo.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
source "$SCRIPT_DIR/services.sh"
require_tools git yq docker python3
validate_operation_root

ACTION="${1:-}"
case "$ACTION" in start|ensure|stop|restart|status|check) ;; *) fail "Acao invalida: '$ACTION'." ;; esac
shift
ORIGINAL_ARGS=("$@")
parse_environment_args "$@"
set -- ${SERVICE_ARGS[@]+"${SERVICE_ARGS[@]}"}
[ "$STATUS_JSON" = 0 ] || { [ "$ACTION" = status ] || [ "$ACTION" = check ]; } || fail "--json so se aplica ao status."
case "$ACTION" in
    start|ensure) ;;
    *) [ "$#" -eq 0 ] || fail "$ACTION opera no ambiente; selecao de servicos e aceita por start/ensure." ;;
esac

PROJECT="$(project_name)"
apply_docker_engine
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
if [ ! -f "$COMPOSE" ] && [ "$ACTION" = ensure ]; then
    exec bash "$SCRIPT_DIR/new.sh" "${ORIGINAL_ARGS[@]}"
fi
if [ ! -f "$COMPOSE" ] && [ "$ACTION" = status ] && [ "$STATUS_JSON" = 1 ]; then
    python3 -c 'import json,sys; print(json.dumps({"project":sys.argv[1],"environment":sys.argv[2],"ready":False,"status":"absent"}))' "$PROJECT" "$ENV_NAME"
    exit 5
fi
[ -f "$COMPOSE" ] || fail "Ambiente '$ENV_NAME' sem compose salvo. Use env new."
validate_state_owner "$STATE_DIR"
validate_requested_branch "$(repo_root)/.worktrees/$ENV_NAME"

case "$ACTION" in
    start|ensure)
        select_services "$@"
        require_shared_infra_authorization
        if [ "$(manifest_get '.access')" != tailnet ]; then
            docker start "$ENVSTACK_TRAEFIK" >/dev/null
        fi
        start_services start "${SELECTED_SERVICES[@]}" ;;
    stop)
        remember_services
        dc stop --timeout 60
        ok "Servicos parados; containers, volumes e arquivos preservados" ;;
    restart)
        active="$(running_services)"
        [ -n "$active" ] || fail "Ambiente parado. Use env start para retomar."
        select_services
        dc restart --timeout 60 "${SELECTED_SERVICES[@]}"
        start_services start "${SELECTED_SERVICES[@]}" ;;
    check)
        python3 "$SCRIPT_DIR/tailnet.py" check --root "$(repo_root)" --state "$STATE_DIR" --environment "$ENV_NAME" ;;
    status)
        if [ "$STATUS_JSON" = 1 ]; then
            python3 "$SCRIPT_DIR/status.py" "$(repo_root)" "$STATE_DIR" "$ENV_NAME" "$DOCKER_CONTEXT"
        else dc ps --all; fi ;;
esac
