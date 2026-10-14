# Manifesto do stack — gerado pela skill `env` (init) e VERSIONADO.
# Descreve como cada ambiente (env new <nome>) deve ser montado.
# Edite a vontade: versoes, portas, comandos. Um `env new` le este arquivo.
project: ${PROJECT}      # base dos nomes (rede, dominio, db). Default: nome da pasta do repo.
tld: local               # dominio: <env>.<pasta>.<project>.<tld>
engine: ${ENGINE}        # orbstack | docker-desktop | auto (usa docker_context explicito)
docker_context: ${DOCKER_CONTEXT_NAME} # contexto capturado no detect; revisar antes de operar
base_ref: ${BASE_REF}    # referencia local usada para criar novas branches
database: postgres        # banco compartilhado do ambiente
database_mode: isolated   # shared exige database_shared; ver references/bancos-compartilhados.md
services: []             # preenchido pelo detect; cada item: {folder, type, version, port, database}
# Campo opcional por servico: aliases. Gera dominios extras p/ o mesmo container
# (ex.: aliases: [unidades, admin] -> <env>-<pasta>-unidades e <env>-<pasta>-admin).
# Use ${env:alias.<nome>.host} / ${env:alias.<nome>.url} no .env.example p/ referenciar.
