#!/usr/bin/env bash
# xdebug.sh — liga/desliga o Xdebug nos servicos PHP de um ambiente, em runtime.
# Escreve/remove um .ini e reinicia so os containers PHP (nao recria, nao toca no banco).
#
# Uso: xdebug.sh <on|off|status> <nome>
#
# Pre-requisito: imagem PHP com Xdebug instalado (o template da skill ja inclui).
# O IDE deve escutar a porta 9003 com path mapping /app -> <pasta do servico>.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq docker

ACTION="${1:-}"; ENV_NAME="${2:-}"
case "$ACTION" in on|off|status) ;; *) fail "Acao invalida: '$ACTION'. Use on|off|status." ;; esac
validate_env_name "$ENV_NAME"
apply_docker_engine

PROJECT="$(project_name)"
validate_state_owner "$SKILL_DIR/state/$PROJECT/$ENV_NAME"
MANIFEST="$(manifest_path)"
# Override do mode=off da imagem. PRECISA ordenar DEPOIS do zz-xdebug.ini da imagem
# (o PHP carrega o conf.d em ordem alfabetica e o ultimo vence). 'zzz-' > 'zz-.'
# porque no 3o caractere '-'(0x2D) < 'z'(0x7A). Com 'zz-xdebug-mode.ini' o mode=off
# vencia (bug) — '.'(0x2E) > '-'(0x2D), entao zz-xdebug.ini carregava por ultimo.
INI="/usr/local/etc/php/conf.d/zzz-xdebug-mode.ini"
INI_LEGACY="/usr/local/etc/php/conf.d/zz-xdebug-mode.ini"  # nome antigo (bug) — limpar sempre

# Servicos PHP do manifesto
PHP_FOLDERS=()
COUNT="$(yq -r '.services | length' "$MANIFEST")"
for i in $(seq 0 $((COUNT - 1))); do
    [ "$(yq -r ".services[$i].type" "$MANIFEST")" = "php" ] && PHP_FOLDERS+=("$(yq -r ".services[$i].folder" "$MANIFEST")")
done
[ ${#PHP_FOLDERS[@]} -gt 0 ] || fail "Nenhum servico PHP no manifesto — nada a fazer."

step "Xdebug ${ACTION} — ambiente '${ENV_NAME}'"
for folder in "${PHP_FOLDERS[@]}"; do
    c="${PROJECT}-${ENV_NAME}-${folder}"
    docker inspect "$c" >/dev/null 2>&1 || { warn "${c} nao esta rodando — pulado"; continue; }
    case "$ACTION" in
        on)
            docker exec "$c" sh -c "rm -f $INI_LEGACY; printf 'xdebug.mode=debug\n' > $INI" \
                && docker restart "$c" >/dev/null \
                && ok "${folder}: Xdebug LIGADO (mode=debug, porta 9003)"
            # O restart re-roda o boot (composer/npm + migrate) antes de servir — espera voltar.
            wait_healthy 180 "$c" && ok "${folder}: servico no ar de novo" \
                || warn "${folder}: ainda reiniciando (boot: deps + migrations)"
            ;;
        off)
            docker exec "$c" sh -c "rm -f $INI $INI_LEGACY" \
                && docker restart "$c" >/dev/null \
                && ok "${folder}: Xdebug DESLIGADO"
            wait_healthy 180 "$c" && ok "${folder}: servico no ar de novo" \
                || warn "${folder}: ainda reiniciando (boot: deps + migrations)"
            ;;
        status)
            if docker exec "$c" test -f "$INI" 2>/dev/null; then
                echo -e "  ${folder}: ${GREEN}ON${NC}"
            else
                echo -e "  ${folder}: ${YELLOW}off${NC}"
            fi
            ;;
    esac
done

[ "$ACTION" = "on" ] && echo -e "  ${BLUE}IDE:${NC} escute a porta 9003 e mapeie /app -> a pasta do servico."
exit 0
