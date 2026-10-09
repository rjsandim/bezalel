# Gerado pela skill `env` (init). Os placeholders no formato env:CHAVE sao
# resolvidos a cada `env new`/`update`. Edite o que precisar — arquivo versionado.
APP_NAME=${env:project}
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=${env:url.self}

DB_CONNECTION=${env:db.connection}
DB_HOST=${env:db.host}
DB_PORT=${env:db.port}
DB_DATABASE=${env:db.db}
DB_USERNAME=${env:db.user}
DB_PASSWORD=${env:db.password}

REDIS_HOST=${env:redis.host}
REDIS_PORT=${env:redis.port}
CACHE_STORE=redis
QUEUE_CONNECTION=redis
SESSION_DRIVER=redis

# Casa a conexao Xdebug com o PHP Server gerado em .idea/php.xml (mesmo nome).
PHP_IDE_CONFIG=serverName=${env:name}-${env:internal.self}
