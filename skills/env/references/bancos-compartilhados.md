# Bancos compartilhados de desenvolvimento

Vários ambientes podem reutilizar a mesma versão de MySQL ou PostgreSQL. Redis
continua exclusivo por ambiente, preservando filas, cache e sessões.

## Configuração versionada

```yaml
engine: orbstack
docker_context: orbstack
base_ref: origin/master
database: mysql
database_mode: shared
database_shared:
  pool: mysql-8-4
  image: mysql:8.4
  port: 35306
```

Para PostgreSQL, use `database: postgres`, outro pool, `image: postgres:17` e outra
porta, por exemplo `35432`. Imagens oficiais exigem versão explícita. Mudanças de
imagem/porta de um pool existente são recusadas: escolha outro pool. Não há upgrade
automático nem tuning de memória. PostgreSQL 18+ usa o novo ponto de montagem da
imagem oficial.

`database_mode: isolated` é o padrão de manifestos antigos. O modo compartilhado
exige contexto explícito. Cada serviço `database: true` recebe database e usuário
exclusivos por raiz do repositório, projeto, ambiente e serviço. No PostgreSQL a
separação é por database, com schema `public` interno da aplicação. No MySQL nomes
não usam curingas de permissões. Aplicações nunca recebem credenciais administrativas;
os usuários PostgreSQL não têm superuser, criação de bancos ou administração de
roles, e seus databases revogam acesso de `PUBLIC`.

## Geração e operação

`new` prepara identidades privadas. Iniciar um serviço que dependa do banco cria
ou retoma o pool, provisiona databases e verifica login. Documentação independente
não acorda o banco. Os comandos normais permanecem, com a autorização de
infraestrutura descrita no [guia de operação](operacao.md).

O pool tem Compose, rede e volume próprios em
`state/_databases/<contexto>/<pool>/`, com porta publicada somente em `127.0.0.1`.
O Compose da feature referencia a rede externa e não contém o servidor nem seu
volume. Apenas serviços com `database: true` entram na rede do pool.

Arquivos `.env` novos recebem a conexão correta mesmo quando o exemplo ainda usa
localhost. PHP usa `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`;
Node usa `DATABASE_URL`. Outros nomes podem ser declarados no serviço:

```yaml
database_env:
  host: PGHOST
  port: PGPORT
  db: PGDATABASE
  user: PGUSER
  password: PGPASSWORD
```

Campos aceitos: `host`, `port`, `db`, `user`, `password`, `url`. Placeholders
`${env:db.*}` e equivalentes do engine continuam disponíveis. `.env` existentes
são preservados; conexões divergentes bloqueiam o início. A IDE usa a porta do
pool e o database exclusivo. Senhas não aparecem no XML nem em `config`.

`stop` e `restart` afetam apenas a feature. `destroy` preserva pool, databases,
usuários e registros privados de vínculos. Essa retenção é intencional: remoção
SQL exige alvo exato, backup e autorização separados. Não há remoção automática do
pool nesta versão. Não apague registros privados para contornar conflitos.

## Migração de ambientes existentes

`update` não troca automaticamente um banco exclusivo pelo compartilhado. Planeje
uma janela local; identifique escritores e preserve Compose, `.env`, seleção ativa,
identidade Docker e dump consistente em pasta privada ignorada. Pare escritores
antes do dump final.

Após conferir origem/destino, `ENV_DATABASE_MIGRATION=<projeto>/<ambiente>` libera
somente a preparação de metadados para esse alvo. Não importa/exporta dados nem
comprova autorização humana. `ENV_DRY_RUN=1` prepara sem iniciar containers. Atualize
explicitamente a conexão a partir do estado privado e provisione/importe o dump
no database correto antes de retomar a aplicação.

Confira tabelas, contagens, integridade, login restrito e recusa de acesso a outro
database. Limpe caches de configuração da aplicação quando necessário e valide
endpoints. Preserve servidor/volume original parado e backup até aceitar a migração.
Não use `down -v`, `--remove-orphans` ou remoção por prefixo. Uma falha requer
diagnóstico e retomada ou rollback explícito.

Estados antigos sem `project-root`/`docker-context` exigem auditoria de origem,
Compose, containers e worktree antes de registrar a identidade, conforme `SKILL.md`.
Copiar a skill não migra esses estados.

## Limites e validação

Permissões separam dados, mas CPU, memória, I/O e disponibilidade são compartilhados.
Use instância exclusiva para carga, mudanças globais e configurações incompatíveis.
Dados e conexões em uso continuam consumindo memória.

Testes automatizados usam fixtures e Docker simulado; apenas `compose config` usa
CLI real, sem daemon. Cobrem identidades, preservação, versão/porta incompatível,
database ausente, namespace sem vínculo, falha SQL, retomada e geração dos engines.
Não comprovam integração real: registre à parte as verificações autorizadas.

Diagnósticos do Compose ficam em arquivos privados no estado local, pois avisos de
interpolação podem conter valores de `.env`. Falhas preservam o código de saída;
não copie esses diagnósticos para chats ou Git sem revisar/remover dados privados.
