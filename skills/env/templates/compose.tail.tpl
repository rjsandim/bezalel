volumes:
  dbdata:
networks:
  internal:
    name: ${PROJECT}-${ENV_NAME}-internal
  proxy:
    name: ${PROXY_NET}
    external: true
