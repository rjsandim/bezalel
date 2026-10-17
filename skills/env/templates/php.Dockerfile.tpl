# Gerado pela skill `env` (init). Ajuste a vontade — este arquivo E versionado.
# Imagem de desenvolvimento para PHP/Laravel. Codigo entra por volume (bind mount),
# entao nao ha COPY do projeto aqui — so runtime + extensoes.
FROM php:${VERSION}-cli

# Extensoes cobrindo o que um Laravel tipico exige:
#  - pdo_mysql/pdo_pgsql/pgsql: bancos      - zip/bcmath/intl: base do framework
#  - gd: manipulacao de imagem + PDFs (DomPDF/PHPWord/FPDF)
#  - sockets: pest browser / websockets / clientes que abrem socket
# Se o projeto nao usa algo (ex.: intl/gd compilam devagar), remova daqui.
# pecl: channel-update + retry tornam o build resiliente a hiccup de rede.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev libzip-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev unzip git \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install pdo_mysql pdo_pgsql pgsql zip bcmath intl gd sockets \
    && pecl channel-update pecl.php.net \
    && (pecl install redis || pecl install redis) \
    && (pecl install xdebug || pecl install xdebug) \
    && docker-php-ext-enable redis xdebug \
    && rm -rf /var/lib/apt/lists/*

# Xdebug instalado mas DESLIGADO por padrao (mode=off = zero overhead).
# Ligue/desligue em runtime com: /env xdebug on|off <ambiente>
RUN { \
      echo "xdebug.mode=off"; \
      echo "xdebug.client_host=host.docker.internal"; \
      echo "xdebug.client_port=9003"; \
      echo "xdebug.start_with_request=yes"; \
    } > /usr/local/etc/php/conf.d/zz-xdebug.ini

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app
COPY boot.sh /usr/local/bin/envstack-boot
EXPOSE ${PORT}
CMD ["sh", "/usr/local/bin/envstack-boot", "php", "php", "artisan", "serve", "--host=0.0.0.0", "--port=${PORT}"]
