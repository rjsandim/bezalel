#!/usr/bin/env bash
# Uso: ctl.sh <start|ensure|stop|restart|status> <nome> [servico...|--all]
# start/ensure acrescentam servicos; stop/restart operam no ambiente ativo.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
source "$SCRIPT_DIR/services.sh"
require_tools git yq docker

ACTION="${1:-}"; ENV_NAME="${2:-}"
case "$ACTION" in start|ensure|stop|restart|status) ;; *) fail "Acao invalida: '$ACTION'." ;; esac
validate_env_name "$ENV_NAME"
shift 2
case "$ACTION" in
    start|ensure) ;;
    *) [ "$#" -eq 0 ] || fail "$ACTION opera no ambiente; selecao de servicos e aceita por start/ensure." ;;
esac

PROJECT="$(project_name)"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
[ -f "$COMPOSE" ] || fail "Ambiente '$ENV_NAME' sem compose salvo. Use env new."

case "$ACTION" in
    start|ensure)
        select_services "$@"
        docker start "$ENVSTACK_TRAEFIK" >/dev/null
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
    status) dc ps --all ;;
esac
