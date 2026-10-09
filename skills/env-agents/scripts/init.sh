#!/usr/bin/env bash
# init.sh — ETAPA 2 do init. Le .envstack/stack.yaml (ja revisado) e materializa
# os artefatos VERSIONADOS: um Dockerfile por servico, .env.example faltantes,
# um .envstack/.gitignore (ignora *.env.example) e a entrada .worktrees/ no
# .gitignore da raiz. Idempotente.
#
# Uso: init.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"
require_tools git yq envsubst

ROOT="$(repo_root)"
ENVSTACK="$ROOT/.envstack"
MANIFEST="$ENVSTACK/stack.yaml"
[ -f "$MANIFEST" ] || fail "Manifesto nao encontrado. Rode scripts/detect.sh primeiro."

PROJECT="$(project_name)"
COUNT="$(yq -r '.services | length' "$MANIFEST")"
[ "$COUNT" -gt 0 ] || fail "Manifesto sem servicos. Edite .envstack/stack.yaml."

step "Materializando config versionada (.envstack/)"
if [ ! -f "$ENVSTACK/boot.sh" ]; then
    cp "$TPL_DIR/boot.sh.tpl" "$ENVSTACK/boot.sh"
fi

for i in $(seq 0 $((COUNT - 1))); do
    folder="$(yq -r ".services[$i].folder" "$MANIFEST")"
    type="$(yq -r ".services[$i].type" "$MANIFEST")"
    version="$(yq -r ".services[$i].version // \"\"" "$MANIFEST")"
    port="$(yq -r ".services[$i].port" "$MANIFEST")"

    # Defaults de versao se vazio
    [ -n "$version" ] || case "$type" in php) version="8.3";; node) version="20";; esac

    # Framework do node (next|vite) define o CMD do dev server e o template de env.
    framework=""; [ "$type" = "node" ] && framework="$(detect_node_framework "$ROOT/$folder")"

    # Dockerfile por servico (a partir do template do tipo)
    case "$type" in
        php)
            export VERSION="$version" PORT="$port"
            RENDER_VARS='${VERSION} ${PORT}' render_template php.Dockerfile.tpl "$ENVSTACK/${folder}.Dockerfile"
            ok "Dockerfile: .envstack/${folder}.Dockerfile (php ${version}, porta ${port})" ;;
        node)
            # Next nao aceita as flags do Vite — monta o comando certo por framework.
            case "$framework" in
                next) dev_cmd="npm run dev -- -H 0.0.0.0 -p ${port}" ;;
                *)    dev_cmd="npm run dev -- --host 0.0.0.0 --port ${port}" ;;
            esac
            export VERSION="$version" PORT="$port" DEV_CMD="$dev_cmd"
            RENDER_VARS='${VERSION} ${PORT} ${DEV_CMD}' render_template node.Dockerfile.tpl "$ENVSTACK/${folder}.Dockerfile"
            ok "Dockerfile: .envstack/${folder}.Dockerfile (node ${version}/${framework}, porta ${port})" ;;
        *) warn "Tipo '${type}' (pasta ${folder}) sem template de Dockerfile — pulado" ;;
    esac

    # Template de env (com placeholders ${env:...}) versionado em .envstack/.
    # Next usa env.next.tpl (NEXT_PUBLIC_*); demais node/php usam env.<type>.tpl.
    env_tpl="env.${type}.tpl"
    [ "$framework" = "next" ] && [ -f "$TPL_DIR/env.next.tpl" ] && env_tpl="env.next.tpl"

    # Nunca sobrescreve nem toca no .env.example real da pasta do projeto.
    envex="$ENVSTACK/${folder}.env.example"
    if [ -f "$envex" ]; then
        ok ".envstack/${folder}.env.example ja existe — preservado"
    elif [ -f "$TPL_DIR/$env_tpl" ]; then
        cp "$TPL_DIR/$env_tpl" "$envex"
        ok ".envstack/${folder}.env.example criado (template ${env_tpl}) — revise os placeholders"
    fi
done

# .gitignore proprio de .envstack/: os *.env.example materializados podem conter
# segredos reais do app (copiados do .env) — nao commitar. Versiona-se apenas
# stack.yaml + os *.Dockerfile. O proprio .gitignore e commitado.
ESGI="$ENVSTACK/.gitignore"
if [ ! -f "$ESGI" ]; then
    printf '# Gerado pela skill env: os env.example podem conter segredos reais — nao commitar.\n# Versionado em .envstack/: apenas stack.yaml e *.Dockerfile.\n*.env.example\n' > "$ESGI"
    ok ".envstack/.gitignore criado (ignora *.env.example)"
else
    ok ".envstack/.gitignore ja existe — preservado"
fi

# .gitignore: worktrees nunca sao commitadas
GI="$ROOT/.gitignore"
if ! grep -qxF ".worktrees/" "$GI" 2>/dev/null; then
    printf '\n# Ambientes efemeros da skill env\n.worktrees/\n' >> "$GI"
    ok ".worktrees/ adicionado ao .gitignore"
else
    ok ".worktrees/ ja no .gitignore"
fi

echo ""
ok "Config materializada. Revise os Dockerfiles em .envstack/ e os .env.example."

# ─── Variaveis de .env a ajustar antes do `new` ───────────────────────────────
# Lista, por servico, o que precisa de valor (vazias) e o que conferir (literais).
# Placeholders ${env:...} sao resolvidos pela skill — nao aparecem aqui.
step "Variaveis de .env a ajustar antes do '/env new'"
ENVSTACK="$ENVSTACK" python3 - <<'PY'
import os, glob
found = False
for f in sorted(glob.glob(os.environ["ENVSTACK"] + "/*.env.example")):
    name = os.path.basename(f)[:-len(".env.example")]
    empties = auto = literals = 0; empty_keys = []
    for line in open(f):
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        k, v = k.strip(), v.strip()
        if "${env:" in v:          # resolvido automaticamente pela skill
            auto += 1
        elif v == "":
            empties += 1; empty_keys.append(k)
        else:
            literals += 1
    extra = f"({literals} com valor padrao, {auto} auto)" if (literals or auto) else ""
    if empty_keys:
        found = True
        print(f"  \033[1m{name}\033[0m — preencher: " + ", ".join(empty_keys) + (f"  {extra}" if extra else ""))
    elif auto or literals:
        print(f"  \033[1m{name}\033[0m — nada obrigatorio {extra}")
if not found:
    print("  (sem variaveis vazias — tudo com default ou resolvido por placeholder)")
print("\n  Dica: '/env config' lista os placeholders ${env:...} disponiveis.")
PY

# ─── Infra do projeto: DNS wildcard + certificado *.<projeto> + Traefik global.
# O certificado e gerado UMA vez aqui e cobre todos os ambientes/subdominios.
require_tools docker
ensure_infra "$(project_name)" "$(project_tld)"

echo ""
ok "Projeto pronto. Crie ambientes com '/env new <nome>' e commite .envstack/ + .gitignore."
