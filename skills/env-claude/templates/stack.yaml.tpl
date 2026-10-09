# Manifesto do stack — gerado pela skill `env` (init) e VERSIONADO.
# Descreve como cada ambiente (env new <nome>) deve ser montado.
# Edite a vontade: versoes, portas, comandos. Um `env new` le este arquivo.
project: ${PROJECT}      # base dos nomes (rede, dominio, db). Default: nome da pasta do repo.
tld: local               # dominio: <env>.<pasta>.<project>.<tld>
engine: ${ENGINE}        # docker engine deste projeto: orbstack | docker-desktop | auto (usa o contexto ativo)
database: postgres        # banco compartilhado do ambiente
services: []             # preenchido pelo detect; cada item: {folder, type, version, port, database}
# Campo opcional por servico: aliases. Gera dominios extras p/ o mesmo container
# (ex.: aliases: [unidades, admin] -> <env>-<pasta>-unidades e <env>-<pasta>-admin).
# Use ${env:alias.<nome>.host} / ${env:alias.<nome>.url} no .env.example p/ referenciar.
