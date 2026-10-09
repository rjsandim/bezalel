  postgres:
    image: postgres:17
    container_name: ${PROJECT}-${ENV_NAME}-postgres
    restart: unless-stopped
    ports:
      - "${DB_HOST_PORT}:5432"   # exposto no host p/ o IDE/DataGrip (porta deriva do nome do ambiente)
    environment:
      POSTGRES_USER: ${PG_USER}
      POSTGRES_PASSWORD: ${PG_PASS}
      POSTGRES_DB: ${PG_USER}
    volumes:
      - dbdata:/var/lib/postgresql/data
      - ${STATE_DIR}/initdb.sql:/docker-entrypoint-initdb.d/10-init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${PG_USER}"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks: [internal]
