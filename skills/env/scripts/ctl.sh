#!/usr/bin/env bash
# Uso: ctl.sh <start|ensure|stop|restart|status> <nome> [servico...|--all]
#      ctl.sh ensure <nome> [--branch <branch-existente>] [--issue <n>] [servico...|--all]
#      ctl.sh ensure --issue <n> [--branch <branch-existente>] [servico...|--all]   (nome issue-<n>)
#      ctl.sh status <nome> [servico...] --json
# start/ensure acrescentam servicos; stop/restart operam no ambiente ativo.
# ensure com --branch/--issue cria o ambiente (via new.sh) quando ainda nao existe.
# status --json: 0 pronto; 5 existe mas nao esta pronto; 1 erro.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
source "$SCRIPT_DIR/services.sh"
require_tools git yq docker python3

ACTION="${1:-}"
case "$ACTION" in start|ensure|stop|restart|status) ;; *) fail "Acao invalida: '$ACTION'." ;; esac
shift
parse_target_args "$@"
set -- ${SERVICE_ARGS[@]+"${SERVICE_ARGS[@]}"}
case "$ACTION" in
    ensure) ;;
    *) [ -z "$TARGET_BRANCH$TARGET_ISSUE" ] || fail "--branch/--issue sao aceitos por ensure (ou new)." ;;
esac
[ "$TARGET_JSON" = 0 ] || [ "$ACTION" = status ] || fail "--json e aceito apenas por status."
case "$ACTION" in
    start|ensure) ;;
    status) [ "$#" -eq 0 ] || [ "$TARGET_JSON" = 1 ] || fail "status sem --json opera no ambiente inteiro." ;;
    *) [ "$#" -eq 0 ] || fail "$ACTION opera no ambiente; selecao de servicos e aceita por start/ensure." ;;
esac

PROJECT="$(project_name)"
apply_docker_engine
ROOT="$(repo_root)"
WORKTREE_DIR="$ROOT/.worktrees/$ENV_NAME"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
if [ ! -f "$COMPOSE" ] && [ "$ACTION" = ensure ] && [ -n "$TARGET_BRANCH$TARGET_ISSUE" ]; then
    target=()
    [ -z "$TARGET_BRANCH" ] || target+=(--branch "$TARGET_BRANCH")
    [ -z "$TARGET_ISSUE" ] || target+=(--issue "$TARGET_ISSUE")
    exec bash "$SCRIPT_DIR/new.sh" "$ENV_NAME" "${target[@]}" "$@"
fi
[ -f "$COMPOSE" ] || fail "Ambiente '$ENV_NAME' sem compose salvo. Use env new."
validate_state_owner "$STATE_DIR"
check_target_binding

case "$ACTION" in
    start|ensure)
        select_services "$@"
        require_shared_infra_authorization
        [ -z "$TARGET_ISSUE" ] || [ -f "$STATE_DIR/issue" ] || printf '%s\n' "$TARGET_ISSUE" > "$STATE_DIR/issue"
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
    status)
        if [ "$TARGET_JSON" = 0 ]; then dc ps --all; exit; fi
        # Pedidos explicitos, senao o conjunto ativo/lembrado. Sem segredos nem conteudo de .env.
        requested="$(printf '%s\n' "$@")"
        if [ "$#" -eq 0 ]; then
            requested="$(running_services)"
            if [ -z "$requested" ] && [ -s "$STATE_DIR/started-services" ]; then requested="$(cat "$STATE_DIR/started-services")"; fi
        fi
        db_engine="$(manifest_get '.database')"; [ "$db_engine" = mysql ] || db_engine=postgres
        db_port="$(db_host_port "$ENV_NAME")"
        if [ -f "$STATE_DIR/shared-database.json" ]; then
            db_port="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["pool"]["port"])' "$STATE_DIR/shared-database.json")"
        fi
        ps_json="$(dc ps --all --format json)"
        ES_PROJECT="$PROJECT" ES_NAME="$ENV_NAME" ES_TLD="$(project_tld)" ES_WORKTREE="$WORKTREE_DIR" \
        ES_CONTEXT="$DOCKER_CONTEXT" ES_DB_ENGINE="$db_engine" ES_DB_PORT="$db_port" ES_REQUESTED="$requested" \
        ES_STATE_DIR="$STATE_DIR" ES_PS="$ps_json" ES_SERVICES="$(yq -o=json -I=0 '.services' "$(manifest_path)")" \
            python3 "$SCRIPT_DIR/status_json.py" ;;
esac
