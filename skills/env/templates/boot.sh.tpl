#!/bin/sh
# Instalacao somente quando manifests, dependencias instaladas ou runtime mudam.
# O marcador fica no volume do projeto; falha de instalacao nunca grava sucesso.
set -eu
runtime="$1"
shift

fingerprint() {
    case "$runtime" in
        node)
            node -p 'JSON.stringify([process.version, process.platform, process.arch])'
            for file in package.json package-lock.json npm-shrinkwrap.json .npmrc node_modules/.package-lock.json; do
                [ ! -f "$file" ] || sha256sum "$file"
            done ;;
        php)
            php -v
            php -m
            for file in composer.json composer.lock vendor/composer/installed.json; do
                [ ! -f "$file" ] || sha256sum "$file"
            done
            # Pacotes locais podem mudar a resolucao de dependencias.
            if [ -d packages ]; then
                find packages -name composer.json -type f -exec sha256sum '{}' \; | sort
            fi ;;
    esac
}

case "$runtime" in
    node) marker='node_modules/.envstack-deps.sha256' ;;
    php) marker='vendor/.envstack-deps.sha256' ;;
    *) echo "Runtime nao suportado: $runtime" >&2; exit 1 ;;
esac

current="$(fingerprint | sha256sum | cut -d ' ' -f 1)"
installed=''
[ ! -f "$marker" ] || installed="$(cat "$marker")"
if [ "$runtime" = 'php' ] && [ ! -f vendor/autoload.php ]; then
    installed=''
fi
if [ "$current" != "$installed" ]; then
    echo "envstack: preparando dependencias ($runtime)"
    case "$runtime" in
        node) npm install --no-audit --no-fund ;;
        php) composer install --no-interaction ;;
    esac
    mkdir -p "$(dirname "$marker")"
    fingerprint | sha256sum | cut -d ' ' -f 1 > "$marker"
else
    echo "envstack: dependencias conferidas ($runtime)"
fi

case "$runtime" in
    node)
        NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=${ENVSTACK_NODE_HEAP_MB:-512}}"
        export NODE_OPTIONS ;;
    php)
        # Migrations pendentes continuam sendo aplicadas; falha impede servir.
        php artisan migrate --force ;;
esac
exec "$@"
