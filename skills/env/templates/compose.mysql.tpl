  mysql:
    image: mysql:8.4
    container_name: ${PROJECT}-${ENV_NAME}-mysql
    restart: unless-stopped
    ports:
      - "${DB_HOST_PORT}:3306"   # exposto no host p/ o IDE/DataGrip (porta deriva do nome do ambiente)
    environment:
      MYSQL_ROOT_PASSWORD: ${PG_PASS}
      MYSQL_DATABASE: ${PG_USER}
      MYSQL_USER: ${PG_USER}
      MYSQL_PASSWORD: ${PG_PASS}
    volumes:
      - dbdata:/var/lib/mysql
      - ${STATE_DIR}/initdb.sql:/docker-entrypoint-initdb.d/10-init.sql:ro
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "127.0.0.1", "-uroot", "-p${PG_PASS}"]
      interval: 5s
      timeout: 5s
      retries: 15
    networks: [internal]
