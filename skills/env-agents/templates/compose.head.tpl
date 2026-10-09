# Gerado pela skill `env` — EFEMERO, nao commitar. projeto=${PROJECT} ambiente=${ENV_NAME}
name: ${PROJECT}-${ENV_NAME}
x-envstack:
  startup_services: ${STARTUP_SERVICES}
services:
