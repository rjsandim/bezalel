  redis:
    image: redis:7-alpine
    container_name: ${PROJECT}-${ENV_NAME}-redis
    restart: unless-stopped
    networks: [internal]
