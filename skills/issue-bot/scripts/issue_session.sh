#!/usr/bin/env bash
# issue_session.sh — sessão tmux por issue, com janelas `codex` e `claude` interativas.
# Não implementa nem revisa: cria a sessão, liga o log, envia texto e lê o painel.
#
# Uso:
#   issue_session.sh create  --project-name <nome> --issue <n> --cwd <pasta> [--log-dir <pasta>]
#   issue_session.sh send    --session <s> --window codex|claude --text-file <arquivo>
#   issue_session.sh capture --session <s> --window codex|claude [--lines <n>]
#   issue_session.sh hint    --session <s>
#   issue_session.sh logs    --session <s> --window codex|claude [--lines <n>] [--log-dir <pasta>]
#   issue_session.sh destroy --session <s>
#   issue_session.sh status  --session <s>
# Saída: 0 ok; 1 erro (tmux ausente, nome inválido, CLI sem login de conta, janela morta).
set -euo pipefail

WINDOWS=(codex claude)
SHELLS=" bash zsh sh fish dash ksh tcsh -bash -zsh -sh "
# Chaves de API nunca autenticam os CLIs: são removidas do ambiente de cada janela.
API_KEY_VARS=(OPENAI_API_KEY CODEX_API_KEY ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN)
# Flags conferidas em codex-cli 0.163 e Claude Code 2.1 (ver references/sessao-tmux.md).
# Codex: sem prompts de aprovação, com sandbox de escrita restrito à pasta e rede para gh/git.
CODEX_FLAGS=(-s workspace-write -a never -c sandbox_workspace_write.network_access=true)
CLAUDE_FLAGS=(--dangerously-skip-permissions)

fail() { echo "issue_session: $1" >&2; exit 1; }

ACTION="${1:-}"
[ -n "$ACTION" ] || fail "Informe a ação: create, send, capture, hint, logs, destroy ou status."
shift
PROJECT_NAME="" ISSUE="" CWD="" LOG_DIR="" SESSION="" WINDOW="" TEXT_FILE="" LINES_WANTED=200
while [ "$#" -gt 0 ]; do
    [ "$#" -ge 2 ] || fail "Opção sem valor: $1"
    case "$1" in
        --project-name) PROJECT_NAME="$2" ;;
        --issue) ISSUE="$2" ;;
        --cwd) CWD="$2" ;;
        --log-dir) LOG_DIR="$2" ;;
        --session) SESSION="$2" ;;
        --window) WINDOW="$2" ;;
        --text-file) TEXT_FILE="$2" ;;
        --lines) LINES_WANTED="$2" ;;
        *) fail "Opção desconhecida: $1" ;;
    esac
    shift 2
done

command -v tmux >/dev/null 2>&1 || fail "tmux não encontrado; instale-o (no Mac: brew install tmux)."
[[ "$LINES_WANTED" =~ ^[1-9][0-9]{0,5}$ ]] || fail "--lines deve ser inteiro positivo."

valid_session() {
    [[ "$1" =~ ^[a-z0-9][a-z0-9-]*-[1-9][0-9]*$ ]] || fail "Sessão inválida: use <projeto>-<issue> em minúsculas (ex.: rcastello-122)."
}

valid_window() {
    case "$1" in codex|claude) ;; *) fail "Janela inválida: use codex ou claude." ;; esac
}

session_exists() { tmux has-session -t "=$1" 2>/dev/null; }

option() { tmux show-options -v -t "=$SESSION:" "$1" 2>/dev/null || true; }

pane() { tmux display-message -p -t "=$SESSION:$1" "$2" 2>/dev/null; }

cli_running() {
    local current
    current="$(pane "$1" '#{pane_current_command}')" || return 1
    [ "$(pane "$1" '#{pane_dead}')" = 0 ] || return 1
    [ -n "$current" ] && [[ "$SHELLS" != *" $current "* ]]
}

without_keys() {
    local unset=() var
    for var in "${API_KEY_VARS[@]}"; do unset+=(-u "$var"); done
    env "${unset[@]}" "$@"
}

# O binário verificado é o mesmo iniciado na janela: o shell da janela pode reordenar o PATH.
resolve_cli() {
    local path
    path="$(command -v "$1" 2>/dev/null)" || fail "$1 não encontrado no PATH."
    [[ "$path" = /* ]] || fail "$1 precisa ser um executável no PATH, não alias ou função."
    printf '%s' "$path"
}

check_codex_login() {
    local out
    out="$(without_keys "$1" login status 2>&1)" || fail "Codex sem login. Rode 'codex login' com a conta ChatGPT."
    # A saída pode citar parte da chave; nunca é repetida.
    grep -q 'ChatGPT' <<<"$out" || fail "Codex não está autenticado pela conta ChatGPT (chave de API não é aceita). Rode 'codex login'."
}

check_claude_login() {
    local out
    out="$(without_keys "$1" auth status --json 2>/dev/null)" || fail "Claude Code sem login. Rode 'claude auth login' com a conta claude.ai."
    python3 -c 'import json,sys
d = json.loads(sys.argv[1])
sys.exit(0 if d.get("loggedIn") is True and d.get("authMethod") == "claude.ai" else 1)' "$out" 2>/dev/null \
        || fail "Claude Code não está autenticado pela conta claude.ai (chave de API não é aceita). Rode 'claude auth login'."
}

launch_command() {
    local window="$1" binary="$2" part quoted=""
    local cmd=(env)
    local var
    for var in "${API_KEY_VARS[@]}"; do cmd+=(-u "$var"); done
    if [ "$window" = codex ]; then cmd+=("$binary" -C "$CWD" "${CODEX_FLAGS[@]}"); else cmd+=("$binary" "${CLAUDE_FLAGS[@]}"); fi
    for part in "${cmd[@]}"; do quoted+="$(printf '%q' "$part") "; done
    printf '%s' "${quoted% }"
}

print_hint() {
    echo "tmux attach -t $SESSION"
    echo "Ctrl+b e depois n troca de janela (codex/claude); Ctrl+b e depois d sai sem encerrar."
    echo "Você pode digitar diretamente na janela para intervir."
}

json_status() {
    local exists=false items=() window current alive log logdir cwd
    if session_exists "$SESSION"; then exists=true; fi
    logdir="${LOG_DIR:-}"; cwd=""
    if [ "$exists" = true ]; then
        logdir="${logdir:-$(option @bezalel_log_dir)}"
        cwd="$(option @bezalel_cwd)"
    fi
    for window in "${WINDOWS[@]}"; do
        current=""; alive=false
        if [ "$exists" = true ]; then
            current="$(pane "$window" '#{pane_current_command}' || true)"
            if cli_running "$window"; then alive=true; fi
        fi
        log=""; [ -z "$logdir" ] || log="$logdir/$SESSION-$window.log"
        items+=("$window" "$current" "$alive" "$log")
    done
    python3 -c 'import json,sys
a = sys.argv[1:]
windows = [{"name": a[i], "command": a[i+1] or None, "cli_alive": a[i+2] == "true", "log": a[i+3] or None}
           for i in range(5, len(a), 4)]
print(json.dumps({"session": a[0], "exists": a[1] == "true", "cwd": a[2] or None, "log_dir": a[3] or None,
                  "attach": a[4], "windows": windows}, ensure_ascii=False, indent=2))' \
        "$SESSION" "$exists" "$cwd" "$logdir" "tmux attach -t $SESSION" "${items[@]}"
}

case "$ACTION" in
    create)
        PROJECT_NAME="$(printf '%s' "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]_]+/-/g')"
        [[ "$PROJECT_NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]] || fail "--project-name inválido: use letras, números e hífens."
        [[ "$ISSUE" =~ ^[1-9][0-9]*$ ]] || fail "--issue deve ser inteiro positivo."
        SESSION="$PROJECT_NAME-$ISSUE"
        [ -n "$CWD" ] && [ -d "$CWD" ] && [ ! -L "$CWD" ] || fail "--cwd deve ser uma pasta existente (sem symlink)."
        CWD="$(cd "$CWD" && pwd -P)"
        # A pasta precisa ser a raiz do projeto ou de uma worktree registrada dele.
        TOP="$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" || fail "--cwd não é um repositório Git."
        [ "$(cd "$TOP" && pwd -P)" = "$CWD" ] || fail "--cwd deve ser a raiz do projeto ou da worktree da issue."
        MAIN="$(git -C "$CWD" worktree list --porcelain | sed -n '1s/^worktree //p')"
        [ -n "$MAIN" ] || fail "Checkout principal não identificado."
        LOG_DIR="${LOG_DIR:-$MAIN/.bezalel/logs}"
        [[ "$LOG_DIR" = /* ]] || fail "--log-dir deve ser absoluto."
        [[ "$LOG_DIR$CWD" != *"'"* ]] || fail "Caminhos com aspas simples não são aceitos."
        [ ! -L "$LOG_DIR" ] || fail "--log-dir não pode ser symlink."
        mkdir -p "$LOG_DIR"
        if session_exists "$SESSION"; then
            existing="$(option @bezalel_cwd)"
            [ -z "$existing" ] || [ "$existing" = "$CWD" ] || fail "A sessão $SESSION já usa outra pasta; encerre-a ou use a mesma --cwd."
        else
            tmux new-session -d -s "$SESSION" -n codex -c "$CWD"
        fi
        present="$(tmux list-windows -t "=$SESSION" -F '#{window_name}')"
        for window in "${WINDOWS[@]}"; do
            grep -Fxq "$window" <<<"$present" || tmux new-window -d -t "=$SESSION:" -n "$window" -c "$CWD"
        done
        tmux set-option -t "=$SESSION:" @bezalel_cwd "$CWD" >/dev/null
        tmux set-option -t "=$SESSION:" @bezalel_log_dir "$LOG_DIR" >/dev/null
        for window in "${WINDOWS[@]}"; do
            # -o só abre o pipe se ainda não houver um: repetir create não duplica nem trunca o log.
            tmux pipe-pane -o -t "=$SESSION:$window" "cat >> '$LOG_DIR/$SESSION-$window.log'"
        done
        for window in "${WINDOWS[@]}"; do
            cli_running "$window" && continue
            binary="$(resolve_cli "$window")"
            if [ "$window" = codex ]; then check_codex_login "$binary"; else check_claude_login "$binary"; fi
            tmux send-keys -t "=$SESSION:$window" -l "$(launch_command "$window" "$binary")"
            tmux send-keys -t "=$SESSION:$window" Enter
        done
        print_hint ;;
    send)
        valid_session "$SESSION"; valid_window "$WINDOW"
        session_exists "$SESSION" || fail "Sessão $SESSION inexistente."
        [ -f "$TEXT_FILE" ] && [ ! -L "$TEXT_FILE" ] && [ -s "$TEXT_FILE" ] || fail "--text-file deve ser um arquivo comum não vazio."
        [ "$(LC_ALL=C tr -d '\000' < "$TEXT_FILE" | wc -c)" -eq "$(wc -c < "$TEXT_FILE")" ] || fail "--text-file não parece texto."
        cli_running "$WINDOW" || fail "Janela $WINDOW sem CLI ativo; rode create novamente."
        buffer="bezalel-$SESSION-$WINDOW"
        tmux load-buffer -b "$buffer" "$TEXT_FILE"
        # Colagem delimitada (-p) evita que quebras de linha enviem o prompt pela metade.
        tmux paste-buffer -p -d -b "$buffer" -t "=$SESSION:$WINDOW"
        tmux send-keys -t "=$SESSION:$WINDOW" Enter
        echo "Enviado para $SESSION:$WINDOW." ;;
    capture)
        valid_session "$SESSION"; valid_window "$WINDOW"
        session_exists "$SESSION" || fail "Sessão $SESSION inexistente."
        tmux capture-pane -p -J -t "=$SESSION:$WINDOW" -S "-$LINES_WANTED" ;;
    hint)
        valid_session "$SESSION"
        print_hint ;;
    logs)
        valid_session "$SESSION"; valid_window "$WINDOW"
        if [ -z "$LOG_DIR" ] && session_exists "$SESSION"; then LOG_DIR="$(option @bezalel_log_dir)"; fi
        [ -n "$LOG_DIR" ] || fail "Sessão encerrada: informe --log-dir para ler o log preservado."
        log="$LOG_DIR/$SESSION-$WINDOW.log"
        [ -f "$log" ] || fail "Log ainda não existe: $log"
        tail -n "$LINES_WANTED" "$log" ;;
    destroy)
        valid_session "$SESSION"
        session_exists "$SESSION" || fail "Sessão $SESSION inexistente."
        logdir="$(option @bezalel_log_dir)"
        tmux kill-session -t "=$SESSION"
        echo "Sessão $SESSION encerrada. Logs preservados${logdir:+ em $logdir}; ambiente env não foi alterado." ;;
    status)
        valid_session "$SESSION"
        json_status ;;
    *) fail "Ação desconhecida: $ACTION" ;;
esac
