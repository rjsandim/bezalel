#!/usr/bin/env bash
# Operacoes sobre o compose salvo: nunca regeneram .env, worktree ou volumes.
export COMPOSE_PARALLEL_LIMIT="${COMPOSE_PARALLEL_LIMIT:-2}"

dc() { docker compose -f "$COMPOSE" "$@"; }

running_services() { dc ps --status running --services; }

remember_services() {
    local active temporary
    active="$(running_services)"
    [ -n "$active" ] || return 0
    temporary="$(mktemp "$STATE_DIR/started-services.XXXXXX")"
    printf '%s\n' "$active" > "$temporary"
    mv "$temporary" "$STATE_DIR/started-services"
}

# Sem argumentos: retoma a selecao anterior, ou usa o padrao salvo do projeto.
# Projetos sem startup.services continuam iniciando todos os servicos.
select_services() {
    local available requested service defaults
    available="$(dc config --services)"
    if [ "$#" -gt 0 ]; then
        if [ "$1" = '--all' ]; then
            [ "$#" -eq 1 ] || fail "Use --all sem nomes de servicos."
            requested="$available"
        else
            requested="$(printf '%s\n' "$@")"
        fi
    else
        requested="$(running_services)"
        if [ -z "$requested" ] && [ -s "$STATE_DIR/started-services" ]; then
            requested="$(cat "$STATE_DIR/started-services")"
        fi
        if [ -z "$requested" ]; then
            defaults="$(yq -r '.x-envstack.startup_services[]' "$COMPOSE")"
            requested="${defaults:-$available}"
        fi
    fi
    SELECTED_SERVICES=()
    while IFS= read -r service; do
        [ -n "$service" ] || continue
        printf '%s\n' "$available" | grep -Fxq -- "$service" ||
            fail "Servico '$service' ausente no compose salvo. Revise o manifesto e use env update; nenhum servico foi alterado."
        SELECTED_SERVICES+=("$service")
    done <<< "$requested"
    [ "${#SELECTED_SERVICES[@]}" -gt 0 ] || fail "Nenhum servico selecionado."
}

start_services() {
    local mode="$1"
    shift
    select_services "$@"
    step "Iniciando: ${SELECTED_SERVICES[*]} (e dependencias)"
    if [ "$mode" = 'update' ]; then
        dc up -d --build --wait --wait-timeout 420 "${SELECTED_SERVICES[@]}"
    else
        # Um start aditivo nao recria containers com configuracoes locais alteradas.
        dc up -d --no-recreate --wait --wait-timeout 420 "${SELECTED_SERVICES[@]}"
    fi
    remember_services
    ok "Servicos solicitados e dependencias prontos"
    dc ps
}
