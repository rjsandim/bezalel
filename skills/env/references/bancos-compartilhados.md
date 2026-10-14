# Bancos compartilhados de desenvolvimento

Vários ambientes podem reutilizar a mesma versão de MySQL, PostgreSQL ou Redis.
Cada recurso tem configuração, estado e ciclo de vida independentes da feature.

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

### Redis compartilhado

```yaml
redis_mode: shared
redis_shared:
  pool: redis-7-4
  image: redis:7.4-alpine
  port: 35379
  databases: 256
services:
  - folder: api
    type: php
    redis: true
```

Mescle esses campos ao manifesto existente; não substitua a lista de serviços.
`redis_mode` ausente ou `isolated` mantém o comportamento anterior. Somente
consumidores `redis: true` entram na rede externa. Versão e porta são imutáveis
para um pool; são aceitas imagens oficiais `redis:7.<minor>[.<patch>]-alpine`.
Redis 8/Cluster não está certificado por esse contrato.

Cada serviço recebe um usuário, senha aleatória, prefixo exclusivo e dois índices
distintos: um para filas/sessões e outro para cache. A reserva é persistente em
`state/_redis/<contexto>/<pool>/allocations.json` e não é reciclada por `destroy`.
O padrão de 256 bancos comporta 127 pares. Quando esgotado, crie outro pool.
Novos `.env` PHP recebem `REDIS_HOST`, `REDIS_PORT`, `REDIS_USERNAME`,
`REDIS_PASSWORD`, `REDIS_DB`, `REDIS_CACHE_DB`, `REDIS_PREFIX` e `CACHE_PREFIX`.
Se já houver `REDIS_URL` no template, ela é substituída por URL autenticada sem
path, para não sobrepor os dois índices no Laravel. Os placeholders
`${env:redis.*}` seguem os nomes `host`, `port`, `user`, `password`, `db`,
`cache_db`, `prefix`, `cache_prefix` e `url`. `.env` existente continua preservado
e a conexão é conferida antes de iniciar.

Node/outros clientes precisam declarar `redis_env` com os campos correspondentes,
incluindo `prefix` e `url`, ou `host/port/user/password/db`. A aplicação deve aplicar
o prefixo às chaves/canais e usar autenticação ACL; o gerador não adapta bibliotecas.
Teste os consumidores reais antes de migrar.

As ACLs permitem `SELECT` somente para o par reservado e acesso a chaves/canais
do prefixo. Comandos globais e de cópia/movimentação entre bancos são bloqueados.
`FLUSHDB` fica disponível para a limpeza nativa do Laravel no banco selecionado,
sem alcançar os bancos de outro ambiente. O início confere todas as seleções
proibidas por `ACL DRYRUN` e autentica as duas conexões; versão incompatível ou
permissão divergente causa erro. Scripts Lua da aplicação continuam sujeitos às ACLs.

**Limite do Redis 7:** a permissão por primeiro argumento de `SELECT` é um recurso
legado/depreciado. Toda conexão nasce no banco zero; por isso zero fica reservado,
sem dados de aplicação. Uma conexão que ignore o índice configurado pode operar
nesse banco. Isso é isolamento operacional para desenvolvimento local confiável,
não segurança para clientes hostis. Nunca reutilize conexões entre usuários.
Instâncias exclusivas continuam disponíveis quando esse contrato não servir.

O pool usa AOF, volume próprio, ACLs persistidas e porta somente em localhost.
`stop`, `restart` e `destroy` não removem o servidor, usuários ou dados do pool.
Backup deve preservar dados, ACLs, credenciais administrativas e alocações.

Para migrar Redis existente, preserve Compose, `.env`, estado e um RDB consistente;
pause todos os escritores. `ENV_REDIS_MIGRATION=<projeto>/<ambiente>` libera apenas
a preparação dos metadados desse alvo, não copia dados. Importe chaves para os
índices atribuídos, traduza prefixos e preserve tipos, valores e vencimentos
absolutos. Não recrie como permanentes chaves expiradas. Confira acesso cruzado,
limpeza de cache, operações de filas/locks e a configuração efetiva do aplicativo.
Mantenha os servidores e volumes originais parados para recuperação.

### Recursos e evidências

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
