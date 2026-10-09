#!/usr/bin/env bash
# ctl.sh — controla o ciclo de vida de um ambiente JA criado, sem recriar a
# worktree nem rebuildar. Age em TODOS os servicos do ambiente de uma vez.
#
# Uso: ctl.sh <start|stop|restart|status> <nome>
#
#   start    sobe/religa os containers (cria se nao existirem; NAO rebuilda)
#   stop     para os containers (preserva volumes e dados)
#   restart  reinicia os containers
#   status   mostra o estado dos containers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq docker

ACTION="${1:-}"; ENV_NAME="${2:-}"
case "$ACTION" in start|stop|restart|status) ;; *) fail "Acao invalida: '$ACTION'. Use start|stop|restart|status." ;; esac
validate_env_name "$ENV_NAME"

PROJECT="$(project_name)"
STATE_DIR="$SKILL_DIR/state/$PROJECT/$ENV_NAME"
COMPOSE="$STATE_DIR/docker-compose.yml"
[ -f "$COMPOSE" ] || fail "Ambiente '$ENV_NAME' nao foi iniciado (sem compose). Use: /env new $ENV_NAME"

dc() { docker compose -f "$COMPOSE" "$@"; }

# Containers de aplicacao (um por servico do manifesto) — para aguardar o boot.
app_containers() {
    local m; m="$(manifest_path)"; local n; n="$(yq -r '.services | length' "$m")"
    for i in $(seq 0 $((n - 1))); do
        echo "${PROJECT}-${ENV_NAME}-$(yq -r ".services[$i].folder" "$m")"
    done
}

case "$ACTION" in
    start)
        step "Iniciando '${ENV_NAME}'"
        # Garante o Traefik global de pe (sem reconfigurar DNS/certs).
        docker start "$ENVSTACK_TRAEFIK" >/dev/null 2>&1 || true
        dc up -d            # cria se faltar, religa parados; nao rebuilda
        ok "Servicos iniciados"
        # O start re-roda o boot (composer/npm + migrate) antes de servir — espera prontidao.
        wait_healthy 300 $(app_containers) && ok "Servicos no ar" || true
        dc ps ;;
    stop)
        step "Parando '${ENV_NAME}'"
        dc stop
        ok "Servicos parados (dados preservados)" ;;
    restart)
        step "Reiniciando '${ENV_NAME}'"
        dc restart
        ok "Servicos reiniciados"
        wait_healthy 300 $(app_containers) && ok "Servicos no ar" || true
        dc ps ;;
    status)
        step "Status '${ENV_NAME}'"
        dc ps ;;
esac
