  ${FOLDER}:
    build:
      context: ${ROOT}/.envstack
      dockerfile: ${FOLDER}.Dockerfile
    container_name: ${PROJECT}-${ENV_NAME}-${FOLDER}
    restart: unless-stopped
    env_file:
      - ${WORKTREE_DIR}/${FOLDER}/.env
    volumes:
      - ${WORKTREE_DIR}/${FOLDER}:/app
    extra_hosts:
      - host.docker.internal:host-gateway   # Xdebug conecta de volta no IDE do host
    healthcheck:
      # Pronto = o dev server (php artisan serve / npm run dev) ja responde HTTP.
      # Cobre o gap do 1o boot (composer/npm install + migrate): ate ficar "healthy"
      # o Traefik nao roteia (evita 502) e os scripts da skill aguardam aqui.
      # curl existe nas imagens base (php-cli e node-bookworm). Qualquer resposta
      # HTTP conta como pronto (nao usamos -f: 302/404/500 = servidor de pe).
      test: ["CMD-SHELL", "curl -s -o /dev/null http://127.0.0.1:${PORT}/ || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 6
      start_period: 300s   # 1o boot baixa dependencias — nao marca unhealthy nesse periodo
    depends_on:
      ${DB_SERVICE}: { condition: service_healthy }
      redis: { condition: service_started }
    labels:
      - traefik.enable=true
      - traefik.docker.network=${PROXY_NET}
      - "traefik.http.routers.${PROJECT}-${ENV_NAME}-${FOLDER}.rule=${SVC_RULE}"
      - traefik.http.routers.${PROJECT}-${ENV_NAME}-${FOLDER}.entrypoints=websecure
      - traefik.http.routers.${PROJECT}-${ENV_NAME}-${FOLDER}.tls=true
      - traefik.http.services.${PROJECT}-${ENV_NAME}-${FOLDER}.loadbalancer.server.port=${PORT}
    networks: [internal, proxy]
