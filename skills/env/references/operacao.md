# Skill `env` — ambientes isolados genericos

Dois momentos distintos:

1. **`init`** (uma vez por projeto, resultado **versionado**): detecta as pastas, tipos e versoes e gera a config em `.envstack/`. Voce revisa e **commita**.
2. **`new`/`update`/`destroy`** (por feature, **efemero**): usam a config commitada para criar/derrubar ambientes. Nao detectam nada.

`<projeto>` = nome da pasta raiz do repo git (ou `.project` do manifesto). Nada de hardcode.

## Manifesto e raiz por worktree

Todos os comandos usam `git rev-parse --show-toplevel` da worktree atual,
mesmo quando chamados de uma subpasta. `detect`/`init` gravam `.envstack/` e
`.gitignore` somente nessa raiz; não consultam nem alteram os arquivos do checkout
principal. Versione a configuração desejada na branch antes de criar ambientes.

`new`/`ensure` criam `.worktrees/<nome>/` sob essa raiz e usam seus templates de
`.env` e Dockerfiles. `update`, IDE e status seguem a mesma raiz. O fallback do
nome do projeto é o nome dessa pasta; declare `project` para manter o nome estável
entre worktrees. Estado continua em `$SKILL_DIR/state/<projeto>/<nome>/`, com
`project-root` apontando para a raiz que criou o ambiente. Opere um ambiente a
partir dessa raiz; colisão com estado de outra raiz é recusada, sem reescrever ou
adotar seu vínculo. Ambientes existentes criados no checkout principal continuam
operando a partir dele. Não copie nem edite o estado para contornar a recusa.

`new`, `ctl`, `update` e `destroy` recusam a execução dentro de uma worktree já
vinculada a um ambiente no estado da skill (inclusive em subpastas). Isso evita
criar estado/Compose e worktree aninhada para uma identidade duplicada, mesmo sem
`project` no manifesto. A mensagem orienta a operar a partir da raiz registrada
em `project-root`; a verificação não lê os arquivos de trabalho dessa raiz.
`detect`/`init` continuam tratando os artefatos da worktree atual.

Pools, alocações e infraestrutura compartilhada continuam no estado global da
skill, fora dos checkouts. A identidade dos databases/usuários inclui a raiz
proprietária, preservando a separação entre ambientes. Regras de Git (base e
registro de worktrees) consultam os metadados compartilhados, sem ler arquivos de
trabalho do checkout principal e sem fetch automático.

## Imagem PostgreSQL

No modo exclusivo (`database_mode` ausente ou `isolated`):

```yaml
database: postgres
database_image: pgvector/pgvector:pg17
```

`database_image` é opcional, com padrão `postgres:17`. A allowlist aceita apenas
`postgres:<versão>[-alpine]` (ex.: `17`, `16.4`) e `pgvector/pgvector:pg<major>`
(ex.: `pg17`), com versão numérica explícita. pgvector não aceita minor/patch,
como `pg17.2`; não aceita `latest`, registros alternativos ou
outros sufixos. A mesma validação é usada em `database_shared.image` para pools
PostgreSQL; nesse modo, `database_image` não se aplica e gera aviso apontando para
`database_shared.image`. O campo também gera aviso em MySQL, cuja imagem permanece
inalterada.
PostgreSQL 18+ monta o volume em `/var/lib/postgresql`; versões anteriores usam
`/var/lib/postgresql/data`, também para pgvector.

A imagem disponibiliza a extensão; este procedimento não cria `CREATE EXTENSION`
nem altera o schema da aplicação. Troca de imagem/major em dados existentes exige
planejamento e migração explícitos; `update` não migra dados. Pools recusam mudança
de imagem/configuração e containers com imagem divergente; escolha outro pool.

## Arquitetura (importante para manutencao)

- **Nada de gerar arquivos com `echo` no script.** Tudo sai de **templates** em `templates/*.tpl`, renderizados com `envsubst` (so as `${VARS}` listadas em `RENDER_VARS`). Para mudar o formato de um Dockerfile/compose, edite o `.tpl`.
- Manifesto lido/escrito com `yq`. `.env` resolvidos com `resolve_env` (python, placeholders `${env:...}`).
- `$SKILL_DIR` é a pasta desta skill na instalação carregada; os scripts ficam em `$SKILL_DIR/scripts/`.
- **Readiness.** `new`/`update`/`start`/`ensure` usam Compose `--wait` e propagam falhas. Só anuncie os serviços realmente prontos. URLs de serviços ainda desligados continuam disponíveis para ativação posterior.
- **Sob demanda.** O compose sempre contém o ambiente completo. `startup.services` no manifesto define o conjunto inicial; ausente/vazio mantém o comportamento anterior (todos). `start`/`ensure <nome> <serviço...>` acrescentam serviços e dependências sem recriar os existentes. `--all` liga tudo. Build/start têm paralelismo padrão 2, ajustável por `COMPOSE_PARALLEL_LIMIT`.
- **Preservação.** Ligar um serviço não deve chamar `update` ou `new` para recriar o ambiente. O controle usa o compose salvo e preserva `.env`, worktree, volumes e serviços já ativos. `update` também preserva `.env` existentes; mudanças nesses arquivos devem ser explícitas. Não use `destroy`, `down -v` ou limpeza de volumes para economizar memória.
- **Preparação das etapas.** Antes de teste, captura ou documentação, identifique os serviços necessários e rode `ensure` com eles; espere disponibilidade antes de continuar. Em dúvida, use `--all`. Serviço desligado não justifica pular uma etapa obrigatória. Não pare ambientes por temporizador/ausência de HTTP: testes, filas e importações podem continuar ativos.
- **Boot.** Imagens novas usam `.envstack/boot.sh`, materializado de `templates/boot.sh.tpl`. Composer/npm só reinstalam quando muda a assinatura dos manifests, dependências instaladas ou runtime. Migrations PHP continuam sendo verificadas a cada boot, com falhas propagadas. Ambientes antigos só ganham esse boot após atualização dos Dockerfiles/boot.sh e `env update`.

```
.envstack/              # VERSIONADO (commitar)
  stack.yaml            # manifesto: project, tld, engine, database, services[]
  <pasta>.Dockerfile    # um por servico (versao + extensoes)
  boot.sh               # inicializacao e verificacao de dependencias
  .gitignore            # ignora *.env.example (podem ter segredos do app) — gerado pelo init
  <pasta>.env.example   # GITIGNORED — template de .env (pode conter segredos reais do app)
.worktrees/<nome>/      # EFEMERO (gitignored) — a worktree (inclui .idea/ gerado: php.xml + dataSources.xml)
$SKILL_DIR/state/<projeto>/<nome>/         # EFEMERO — compose gerado + initdb
```

> **Segredos:** os `*.env.example` em `.envstack/` podem ser preenchidos com a config real do app (copiada do `.env`), entao o `init` gera um `.envstack/.gitignore` que os ignora. Versionam-se `stack.yaml`, `boot.sh`, os `*.Dockerfile` e o proprio `.gitignore`.

## Bancos compartilhados entre ambientes

O modo opcional `database_mode: shared` reutiliza MySQL/PostgreSQL com databases
e usuários separados. `redis_mode: shared` habilita um pool Redis com bancos
lógicos e usuários por serviço. Leia [configuração e migração](bancos-compartilhados.md)
antes de habilitar. As convenções de banco abaixo descrevem o modo `isolated`.

## Convencoes
- Dominio: `https://<nome>-<pasta>.<projeto>.local` (1 subdominio por pasta)
- Rede: `envstack-proxy` · Traefik: `envstack-traefik` (compartilhados)
- 1 Postgres/MySQL + 1 Redis por ambiente, compartilhados. 1 database por pasta backend (nome = pasta), user = `<projeto>`, senha `secret`. O banco e exposto no host numa **porta deterministica por ambiente** (33000-34999) p/ o IDE/DataGrip conectar.
- Para criar, escolha uma descrição curta em minúsculas, sem acentos, com palavras
  separadas por hífens: `corrigir-login`, `ajustar-cadastro-empresa`. Números são
  permitidos quando significativos, como `migrar-php-84`; não acrescente sufixos
  aleatórios ou prefixos de agente/tipo como `codex/`, `codex-` ou `feat/`.
- Passe esse nome completo a `new`: branch, `.worktrees/<nome>`, nome do ambiente
  e seu registro de estado usam a mesma identificação. Confira colisões; não
  reutilize uma branch/ambiente alheio apenas porque o nome coincide.
- O CLI valida caracteres compatíveis (`^[a-z0-9][a-z0-9-]*$`); a escolha de uma
  descrição significativa cabe ao agente. Ele não acrescenta nem remove prefixos.
  Para ambientes preexistentes, confira `worktree-branch` e preserve nomes/dados;
  atualizar o Bezalel não renomeia recursos existentes.

## Placeholders no `.env.example`
| Placeholder | Resolve |
|---|---|
| `${env:project}` / `${env:name}` | projeto / ambiente |
| `${env:postgres.host\|port\|db\|user\|password\|url}` | `postgres` / `5432` / nome da pasta / `<projeto>` / `secret` / DSN |
| `${env:redis.host\|port\|url}` | `redis` / `6379` / `redis://redis:6379` |
| `${env:url.self}` / `${env:host.self}` | URL/host publico desta pasta |
| `${env:url.<pasta>}` / `${env:host.<pasta>}` / `${env:internal.<pasta>}` | URL/host publico / hostname interno de outra pasta |
| `${env:url.backend}` / `${env:host.backend}` / `${env:internal.backend}` | idem, do **1o servico php** do stack (aponta frontend->API sem hardcode da pasta) |
| `${env:alias.<nome>.url}` / `${env:alias.<nome>.host}` | URL/host de um alias deste servico (ver `aliases` no manifesto) |

> O comando `config` (`bash "$SKILL_DIR/scripts/vars.sh"`) imprime esta tabela ja resolvida com os nomes reais do projeto. Use antes de editar os `.env.example`.

---

## Roteiro: `init` (conduza EM ETAPAS, validando com o usuario)

Revise o manifesto e os artefatos antes de operar. Detect/init geram arquivos locais; new exige autorização para infraestrutura compartilhada.

1. **Detectar.** Rode `bash "$SKILL_DIR/scripts/detect.sh"`. Mostre ao usuario o `.envstack/stack.yaml` gerado (pastas/tipos/versoes/portas). Para o que nao foi detectado (versao vazia, banco), pergunte e **edite o manifesto** (via yq ou Edit).
2. **Materializar.** Rode `bash "$SKILL_DIR/scripts/init.sh"`. Mostre os Dockerfiles gerados em `.envstack/` e os `.env.example`. Ajuste extensoes/comandos nos `.tpl` ou nos arquivos gerados se necessario (ex.: o projeto precisa de `gd`, `soap`, etc.).
3. **Validar ponta-a-ponta.** Use um ambiente de validação com nome explícito, como `validar-env`, e confira antes que esse nome não existe (`git branch --list validar-env`, `git worktree list`). Para checar só a geração, sem DNS/containers/sudo, use `ENV_DRY_RUN=1 bash "$SKILL_DIR/scripts/new.sh" validar-env`. Somente se autorizado a alterar infraestrutura compartilhada, use `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/new.sh" validar-env` e verifique que cada URL responde. Se algo quebrar (extensão faltando, porta errada), ajuste o `.tpl`/manifesto e rode `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/update.sh" validar-env`. Repita até subir limpo.
4. **Remover o ambiente de validação.** Com autorização de remoção, rode `bash "$SKILL_DIR/scripts/destroy.sh" validar-env --confirm <projeto>/validar-env --keep-worktree` (sem a opção, o destroy recusa a worktree porque ela contém `.env` e `.idea/` gerados). Revise `git -C .worktrees/validar-env status --short --ignored`: sem trabalho a preservar, remova a worktree e a branch com `git worktree remove .worktrees/validar-env` e `git branch -d validar-env`, sem força. Se o Git recusar por arquivo não rastreado gerado pela skill, apague esse arquivo e repita. Confirme com `git worktree list` e `git branch --list validar-env` que nada restou. Em dry-run não há containers: pule o destroy e remova só a worktree, a branch e `$SKILL_DIR/state/<projeto>/validar-env/`.
5. **Commitar.** Instrua o usuario a commitar `.envstack/` (`stack.yaml`, `boot.sh`, `*.Dockerfile` e `.envstack/.gitignore`) + o `.gitignore` da raiz. Os `*.env.example` ficam de fora (gitignored pelo `.envstack/.gitignore`, pois podem ter segredos do app); as worktrees tambem.

## Roteiro: `new <nome> [serviço...|--all]`
1. Escolha a descrição curta conforme as convenções e confira o nome exato da branch, worktree e ambiente; não crie uma worktree paralela com prefixo do aplicativo.
2. `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/new.sh" <nome>` (variável só nesta execução autorizada) inicia o padrão do manifesto; argumentos selecionam outros serviços. Repetir `new` em ambiente existente delega ao start, sem regenerar arquivos.
3. Relate o que está ativo e como ligar os serviços restantes. O catálogo de URLs não significa que todas estejam atendendo.

### Manifesto de ativação
```yaml
startup:
  services: [api]
services:
  - folder: api
    # Demais campos normais (type, port, database...).
  - folder: site
    depends_on: [api]
  - folder: docs
    depends_on: []
```
`depends_on` é opcional e aceita a sintaxe de dependências do Compose. Ausente preserva DB + Redis para compatibilidade; `[]` declara independência. Mantenha todas as pastas no manifesto. Nos modos compartilhados, dependências do servidor local são retiradas e somente consumidores declarados entram na rede do pool. Não ajuste caches ou imponha limites de RAM baixos sem medir o workload.

## Roteiro: `config` (lista os placeholders `${env:...}`)
- `bash "$SKILL_DIR/scripts/vars.sh"` — imprime os placeholders disponiveis ja resolvidos com os nomes reais do projeto (project, db engine, pastas, backend, aliases). Use para saber o que pode escrever nos `.env.example` antes de commitar/rodar o `new`.

## Roteiro: `start`/`ensure`/`stop`/`restart`/`status <nome>`
- `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/ctl.sh" start <nome>` — retoma serviços ativos/lembrados; sem histórico, usa o padrão salvo.
- `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/ctl.sh" ensure <nome> <serviço...>` — garante os serviços e suas dependências; pode ser chamado novamente. `start` com nomes tem o mesmo comportamento.
- `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/ctl.sh" start <nome> --all` — garante todo o ambiente.
- `bash "$SKILL_DIR/scripts/ctl.sh" stop <nome>` — guarda a seleção e para com prazo de 60s para encerramento; preserva containers, volumes e arquivos.
- `bash "$SKILL_DIR/scripts/ctl.sh" restart <nome>` — reinicia só o que já está ativo; não acorda serviços desligados.
- `bash "$SKILL_DIR/scripts/ctl.sh" status <nome>` — mostra também containers parados.

A seleção é aditiva. `ensure` não desligará outros serviços. A prontidão HTTP/healthcheck não substitui os testes funcionais da tarefa. Compose antigo que não contém um serviço solicitado exige `update`; o controle falha sem regenerar configurações automaticamente.

## Roteiro: `xdebug on|off|status <nome>` (servicos PHP)
- `bash "$SKILL_DIR/scripts/xdebug.sh" on <nome>` — liga o Xdebug (mode=debug) e reinicia so os containers PHP.
- `bash "$SKILL_DIR/scripts/xdebug.sh" off <nome>` — desliga (remove o .ini) e reinicia.
- `bash "$SKILL_DIR/scripts/xdebug.sh" status <nome>` — mostra on/off por servico.
- O Xdebug vem instalado mas off (zero overhead). host.docker.internal ja esta no compose; porta 9003.
- Ambientes criados antes desta versao precisam de `update <nome>` (rebuild) para ganhar o Xdebug na imagem.

### Config da IDE: Xdebug + Databases (automatica)
O `new` gera, na worktree, dois arquivos `.idea/` (via `ide.sh` — regerar a qualquer momento com `bash "$SKILL_DIR/scripts/ide.sh" <nome>`):

- **`.idea/workspace.xml`** (Xdebug — onde o PhpStorm REALMENTE guarda isto, NAO no php.xml):
  - **PhpServers**: um **PHP Server por servico PHP** (`port=443`, path mapping `/app` -> pasta). O container exporta `PHP_IDE_CONFIG=serverName=<env>-<pasta>`, que casa com esse server pelo NOME. Sem o server aqui, o debug conecta mas falha com *"Server with name '...' doesn't exist"*. **Aliases nao precisam de config extra** — o `serverName` e fixo por container (independe do host da request), entao um unico server cobre o dominio principal e todos os aliases.
  - **PhpDebugGeneral**: porta de debug `9003` (= a que o container disca). Sem isso o projeto usa o default global do IDE, que pode estar em outra porta — e o breakpoint nunca conecta.
  - O `ide.sh` faz *splice* (troca o PhpServers, garante o PhpDebugGeneral) **sem reescrever o resto** do `workspace.xml` — preserva o estado do PhpStorm.
- **`.idea/php.xml`**: so o `php_language_level`.

> ⚠️ O PhpStorm e dono do `.idea/` quando o projeto esta ABERTO — ele sobrescreve ao salvar/fechar. Gere a config com a worktree FECHADA (o `new` ja faz, antes do 1o open). Se editou com ela aberta, feche e reabra.
- **`.idea/dataSources.xml`** (DataGrip/DB tool): uma **conexao por servico `database:true`** apontando para `localhost:<porta>/<db>` (user = `<projeto>`). A porta do banco no host e **deterministica por ambiente** (`db_host_port` em `lib.sh`, faixa 33000-34999) e exposta no compose (`compose.<engine>.tpl` -> `ports: <porta>:3306|5432`). A senha (`secret`) e pedida no 1o connect (o IntelliJ guarda no keychain — nao da pra pre-injetar via XML com seguranca).

No PhpStorm: abra a **worktree** (`.worktrees/<nome>`) como projeto. A conexao de banco ja aparece no painel Database. Para Xdebug, garanta a porta 9003 (Settings > PHP > Debug, default ja e 9003), clique em **Start Listening for PHP Debug Connections** e rode `bash "$SKILL_DIR/scripts/xdebug.sh" on <nome>`.

> Ambientes criados antes desta versao nao tem a porta do banco exposta nem o `dataSources.xml` — rode `update <nome>` (recria o compose + regenera `.idea/`).

## Roteiro: `update <nome>`
- `ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/update.sh" <nome> [serviço...|--all]` — regenera o compose e reconstrói a seleção ativa/lembrada, ou a seleção explícita. Preserva `.env` existentes, worktree e volumes; só resolve `.env` ausentes. Use após mudar manifesto/Dockerfile/boot.sh; alterações de configuração local são feitas explicitamente no `.env`.

## Roteiro: `destroy <nome>`
- A autorização deve identificar projeto e ambiente. Use `bash "$SKILL_DIR/scripts/destroy.sh" <nome> --confirm <projeto>/<nome>`; `--keep-worktree` preserva worktree e branch, mas não os volumes. Sem a opção, arquivos locais (inclusive ignorados), commits não integrados ou divergências bloqueiam a remoção antes de tocar nos volumes. Não há --force, remoção por prefixo ou exclusão automática de imagens. Falhas preservam o registro de estado e retornam erro.

## Pre-requisitos da maquina
Python 3.9+, Bash, Homebrew, yq de Mike Farah v4, Docker com Compose que suporte `up --wait --wait-timeout`, Git com `--path-format` e `--end-of-options`, `jq`, `envsubst` (gettext). macOS-first (usa `brew services` + resolver do macOS para o DNS wildcard; `mkcert`/`dnsmasq`/Traefik sao configurados pelo `new`/`update`).

## HTTPS / certificados (mkcert + Traefik)
Cert wildcard `*.<projeto>.<tld>` por projeto (mkcert, confiavel pela CA do `mkcert -install`), cobre **todos** os hosts de label unico — inclusive os aliases (`<env>-<pasta>-<alias>...`). O `ensure_project_infra` (`lib.sh`) gera o cert + um `dynamic/<projeto>.yml` (que poe o cert no pool de SNI do Traefik). **Gotcha macOS:** o `--providers.file.watch` do Traefik sobre bind mount **nao recebe eventos** de inotify (limitacao do FS de VM — vale p/ OrbStack e Docker Desktop), entao um cert adicionado depois que o Traefik global ja roda nunca entra no pool → o Traefik serve o **default cert** (`CN=TRAEFIK DEFAULT CERT`) = "certificado invalido" no navegador. Por isso o `ensure_project_infra`: (1) regenera o `dynamic/<projeto>.yml` se faltar (mesmo com o cert ja existindo) e (2) da `docker restart` no Traefik global quando (re)escreve o cert/dynamic — assim o cert entra no pool. Generico (deriva de `${project}/${domain}`).

## Notas por runtime
- **Vite (node):** atras do proxy o dev server bloqueia hosts desconhecidos (403). A skill resolve **sozinha**: o `env.node.tpl` injeta `__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS=${env:host.self}` no `.env`, que o Vite (7+/8) soma a `server.allowedHosts` sem tocar no `vite.config`. So nao funciona se o config usar `allowedHosts: true` (ai ja libera tudo). Nada a editar no app — ideal p/ apps gerenciados por Lovable.
- **Next.js (node):** detectado por dependencia `next`. O `init` gera o CMD com as flags do Next (`-H 0.0.0.0 -p <porta>`, nao `--host/--port` do Vite), usa porta default 3000 e o `env.next.tpl` (`NEXT_PUBLIC_API_URL`).
- **Laravel (php):** o template ja inclui `pdo_mysql`, `pdo_pgsql`, `pgsql`, `zip`, `bcmath`, `intl`, `gd` (PDFs: DomPDF/PHPWord/FPDF), `sockets` (pest browser/websockets), `redis` e `xdebug`. `pecl` roda `channel-update` + retry (resiliente a hiccup de rede). `intl`/`gd` compilam devagar; se o projeto nao usa, remova do `<pasta>.Dockerfile`.
- **Database:** so o php (Laravel) ganha `database: true` por padrao no detect; node assume frontend (sem banco). Se a pasta node for uma API, vire `database: true` no manifesto.
- **Contexto Docker:** `engine: orbstack` e `docker-desktop` têm contextos conhecidos. Para `auto`, `docker_context` é obrigatório. Um contexto explícito precisa existir; conflito entre os campos ou divergência do contexto registrado no ambiente interrompe a operação. Não há fallback para contexto ativo, nem alteração do contexto global.

## Extensao
- Novo tipo de runtime: adicione `templates/<tipo>.Dockerfile.tpl` e `templates/env.<tipo>.tpl`, e um caso em `detect_version`/`default_port_for_type` no `lib.sh`.
- Framework node (ex.: novo flag de dev server): ajuste `detect_node_framework` no `lib.sh` e o `case` de `DEV_CMD` no `init.sh`.
- Mudar formato do stack: edite os `templates/compose.*.tpl`.

## Verificação da skill
- Os testes de manutenção da skill estão em [manutenção](manutencao.md).

## Vínculo explícito de branch e status público

```sh
bash "$SK/new.sh" issue-122 --branch corrigir-filtro --issue 122
bash "$SK/ctl.sh" ensure --issue 122 --branch corrigir-filtro
bash "$SK/ctl.sh" status issue-122 --json
```

`--branch` exige branch/ref de tracking local existente, sem fetch ou criação a
partir de base. Tracking (ex.: origin/corrigir-filtro) cria a branch local do
ambiente exatamente nessa ref. `--issue` sem nome implica issue-N e registra a
issue; sem --branch preserva a resolução habitual pelo nome/base do ambiente.
As duas opções podem ser combinadas para registrar o vínculo. Sem essas flags,
a criação antiga continua usando branch de mesmo nome ou base_ref. Repetir new
preserva Compose/env/arquivos e retoma serviços; troca de vínculo falha antes de
iniciar serviços. Branch, origem e issue ficam registrados no estado local.

Status JSON lista serviços, URLs, portas, aliases, branch, worktree, contexto,
banco sem credenciais e ready. Considera serviços ativos/lembrados ou padrão salvo
e suas dependências; serviços não selecionados podem estar parados. Health ausente
exige processo running; health presente precisa ser healthy. Não substitui teste
funcional humano. Saída 0 pronto, 5 existente mas não pronto, 1 erro.

O restore de dados é opcional pelo env-up do modo issue-bot, após ready, usando
project.json schema 3. A ENV clássica não passa a executar restore automaticamente.
Comando do projeto precisa validar destino isolado e recusar produção; cwd não é
prova da conexão usada pelo comando. Infra compartilhada continua exigindo
ENV_ALLOW_SHARED_INFRA=1 só na invocação autorizada.

## Tailnet: acesso privado no iPhone

Opte por serviço ou ambiente no `.envstack/stack.yaml`. Exemplo (mantenha também
project, base_ref, docker_context, banco e demais campos próprios):

```yaml
startup:
  services: [api, web]
access: tailnet  # só-tailnet; omita para continuar também com .local/Traefik
tailnet:
  primary: web
  services: [api, web]
  port_start: 41000
  port_end: 41999
  environments:
    corrigir-login:
      primary: web
services:
  - folder: api
    type: php
    port: 8000
    database: true
    tailnet:
      probe_path: /health
      probe_statuses: [200, 401, 403]
      checks:
        api: /api/health
        health: /health
        redirect: /private
        login: /login
  - folder: web
    type: node
    port: 5173
    database: false
    tailnet:
      checks:
        static: /src/main.js
        websocket: /ws
```

`services[].tailnet: true` também expõe o serviço; um mapa permite declarar
checks. `tailnet.primary` escolhe `iphone_url`; sem primary, vale o primeiro
serviço exposto na ordem do manifesto. `tailnet.environments.<nome>` sobrescreve
as opções desse ambiente. `access: tailnet` exige seleção explícita e elimina
rede/labels do proxy, DNS dnsmasq/resolver, certificado mkcert e sudo. Não
inicializa nem reinicia Traefik; bindings de bancos exclusivos ficam em loopback.
Pools continuam com seus próprios limites.
Tailscale deve estar conectado por conta, com HTTPS disponível. O binário vem de
`ENV_TAILSCALE_BIN` ou PATH (`command -v tailscale`); wrappers do app macOS são
aceitos. Nunca use chave de API ou Funnel.

A partir da raiz proprietária do ambiente e da pasta real da skill carregada:

```sh
ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/new.sh" corrigir-login
ENV_ALLOW_SHARED_INFRA=1 bash "$SKILL_DIR/scripts/ctl.sh" ensure corrigir-login
bash "$SKILL_DIR/scripts/ctl.sh" status corrigir-login --json
bash "$SKILL_DIR/scripts/ctl.sh" check corrigir-login
```

A autorização temporária continua necessária para publicação/infra compartilhada.
Não exporte permanentemente a variável. `new/update` reservam uma porta por
serviço e publicam após up; `start/ensure` recuperam a publicação dos serviços
ativos. `stop` preserva reserva e Serve; `destroy --confirm projeto/ambiente`
tenta liberar só os vínculos exatos, depois do preflight. Se Tailscale estiver
indisponível, hostname mudar ou houver alvo alheio, avisa em stderr e continua
com `docker compose down -v`; a reserva fica no registro global. Depois de
reconectar/diagnosticar, consulte `tailnet.py list` e `tailscale serve status --json`
(somente leitura) e execute `tailnet.py release --root <raiz> --project <projeto>
--environment <nome> --service <pasta>` para cada serviço. Divergências continuam
recusadas; nunca desligue outro alvo nem edite Serve manualmente. Alteração de seleção com
vínculos existentes é recusada: preserve dados e use destroy confirmado com
`--keep-worktree` antes de regenerar a seleção. Isso remove volumes exclusivos;
faça backup e obtenha a autorização concreta antes dessa operação. Não edite o
registro para contornar divergências. Falha mantém o estado para diagnóstico.

Cada URL é `https://<Self.DNSName>:<P>/`, encaminhada pelo Serve diretamente ao
binding Compose `127.0.0.1:P:<porta-container>`. O registro global fica em
`${ENV_TAILNET_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/envstack/tailnet}/registry.json`,
com lock exclusivo `flock`, escrita atômica e modo 0600. A identidade inclui raiz,
projeto, ambiente e serviço. Hash determinístico e sondagem linear pulam reservas,
Serve e listeners locais. Cópias diferentes da skill compartilham esse registro.
Não troque o diretório global entre bots da mesma máquina.

`tailnet.py allocate|publish|release` recebe `--root`, `--project`,
`--environment` e `--service`; `allocate` aceita `--start/--end`.
`tailnet.py list` só lê. `check` recebe `--root`, `--state <estado-da-ENV>` e
`--environment`. Nenhum comando altera a porta 443 nem o `/` principal;
release usa somente `--https=P off` quando o alvo é exatamente
`http://127.0.0.1:P` e o registro pertence ao ambiente. Alvo diferente, handler
adicional, Funnel ou host divergente bloqueiam sem alterar o vínculo.
Nunca edite `tailscale serve` à mão; não use reset ou set-config global.
`ENV_DRY_RUN=1` gera artefatos e reservas, consultando o Tailscale quando há
opt-in, mas não publica Serve nem inicia containers.

Use `${env:public.url.self}` e `${env:public.url.api}` em APP_URL, frontend,
origens CORS e callbacks. Eles escolhem a URL Tailnet do serviço exposto, ou a
URL .local nos demais quando o acesso local está habilitado. Em
`access: tailnet`, referenciar `public.url.*` de serviço não exposto gera erro
claro antes de escrever o `.env`; exponha o serviço ou corrija o template. `${env:public.host.self}` devolve somente o hostname;
`${env:tailnet.host}`, `${env:tailnet.url.self}` e `${env:tailnet.url.<pasta>}`
são os valores Tailnet (vazios quando desativados). Os placeholders `url.*`
legados continuam .local. Os templates novos usam `public.url.self`,
`public.url.backend` (primeiro PHP) e `public.host.self`. Em modo só-tailnet, exponha todos os serviços chamados
pelo navegador. Portas distintas são origens diferentes: configure CORS com a URL
completa, cookies Secure/SameSite e proxy confiável no projeto. Não publique
segredos no frontend nem nas propostas.

`.env` existente é preservado. Para regenerar, faça uma cópia privada dele,
revise `.envstack/<pasta>.env.example`, remova **somente o .env daquele serviço**
e rode update no ambiente autorizado; confira/restaure os valores privados da
cópia sem versioná-la. O status/check avisa nomes de variáveis URL/ORIGIN/CORS/
CALLBACK e hosts públicos (APP_HOST, PUBLIC_HOST e equivalentes). Conexões
internas DB/DATABASE/REDIS/CACHE/MAIL/SMTP/MEMCACHED não geram esses avisos, mesmo
com localhost; isso não atesta sua conectividade. Os avisos identificam localhost, 127.0.0.1 ou .local sem exibir valores.

`status --json` acrescenta `tailnet: {host, services: [{folder,url,port,serve_ok,
http_code,checks}], warnings}` e `iphone_url`. Readiness exige também Serve e HTTP
dos serviços expostos necessários; falha não vira zero nem sucesso. `check`
consulta página `/`, caminhos estáticos, redirects (Location sem seguir origens
externas), API/health, login e upgrade WebSocket (101 com Upgrade). Varre respostas
por dependências locais e examina domínio/Secure de cookies. Declare os caminhos
reais em `services[].tailnet.checks` como no exemplo (string ou lista).
Casos não declarados aparecem como `not_configured`, nunca como testados.
Check sai 5 com falhas/avisos e 1 com erro de coleta. Não segue scripts ou executa
JavaScript; não prova login autenticado, atributos completos de cookies, CORS no
browser, navegação ou WebSocket da aplicação. Relate essas lacunas e peça ao
Rafael testar o link exato no Safari com Tailscale, inclusive 4G/5G.

### Previews persistentes

Resolva `BEZALEL_ROOT` como a raiz da distribuição carregada (`../..` desta skill):

```sh
python3 "$BEZALEL_ROOT/scripts/preview.py" publish --project . --issue 21 .bezalel/reviews/database-21-v1.html
python3 "$BEZALEL_ROOT/scripts/preview_launchagent.py" plan
```

Publish copia atomicamente para `${BEZALEL_PREVIEWS_DIR:-$HOME/previews}/<projeto>/issue-21/`
e devolve `https://<host>/<projeto>/issue-21/<arquivo>`. Mesmo nome/mesmos bytes
é idempotente; conteúdo diferente exige nome v2. Originais são preservados.
Após decisão de banco, exclua/verifique somente os originais temporários em
`.bezalel/reviews/`; as cópias publicadas ficam guardadas. Nenhum script configura
o Serve principal: ele deve já apontar para o servidor de previews.

O comando `preview_launchagent.py install` instala explicitamente um LaunchAgent
macOS para Python http.server em **127.0.0.1:8000** servindo a pasta de previews.
É idempotente, recusa plist divergente ou porta ocupada e nunca encerra processos.
Apenas `plan` é leitura. A instalação é uma operação separada autorizada; não
execute para validar o pacote nem substitua o servidor já em execução. Este
recurso foi preparado/testado com mocks; não foi instalado nesta implementação.

### Recuperação de reservas e readiness

Uma falha de new/update aciona rollback somente das reservas criadas na tentativa;
as reservas preexistentes, arquivos, worktree e containers são preservados. Não
é limpeza de containers parcialmente iniciados. O recibo privado
`tailnet-attempt.*` é mantido se a liberação falhar, com comando de recuperação
em stderr. Repita `tailnet.py rollback --state <estado-ENV> --attempt <recibo>`
após diagnosticar o Serve. Uma tentativa concluída retira as marcas transitórias
do registro para impedir que um recibo antigo libere reservas já adotadas.
Após falha com Tailnet, `start/ensure` exigem `env update` para reconciliar o
Compose salvo; `new` também reconcilia, em vez de retomar silenciosamente.

Para órfãos removidos fora do destroy, o comando é delimitado e idempotente:

```sh
python3 "$SKILL_DIR/scripts/tailnet.py" prune --root <raiz-proprietaria> --project <projeto> --environment <nome>
```

Ele mantém o lock e só libera uma entrada com proveniência registrada cuja raiz
continua acessível, diretório de estado e worktree não existem nem são links e
Docker confirma zero containers daquele projeto Compose no contexto registrado.
Estado legado sem proveniência, worktree preservada, container parado, falha de
consulta, diretório inacessível ou mapeamento Serve alheio preservam a reserva.
A saída distingue `released` de `preserved`; zero itens removidos não comprova
que todos eram órfãos. Não usa contexto ativo, prefixos, força, 443 ou reset.
Quando o destroy preserva a worktree, use a liberação explícita por serviço;
prune continua conservador. Esta regra também vale na revisão de limpar-orbstack.

Cada serviço pode declarar `tailnet.probe_path` (padrão `/`) e
`tailnet.probe_statuses` (lista de códigos HTTP 200–499; padrão 200–399).
Os valores são persistidos em tailnet.json e usados pelo status/ready e check.
Por exemplo, API com `/health` retornando 401 pode declarar `[200,401,403]`;
404 somente é aceito se explicitamente configurado. 5xx, erro de transporte e
avisos de origem/cookie continuam falhas. Uma falha de transporte da página tem
uma repetição curta (timeout de 2 segundos por tentativa); HTTP ruim não recebe
retry. Chamadas Tailscale têm prazo de 10 segundos cada. O lock permanece durante
as consultas/mutações para impedir troca de alvo entre conferência e release.
A varredura local usa padrões sem repetição aninhada e tem teste adversário de
1 MiB; hosts internos não mascaram a sinalização das URLs públicas.

Publish de previews exige HTML/HTM regular dentro do projeto/worktree explicitado
em `--project`, permitindo `.bezalel/reviews` e recusando dotfiles, nomes de
segredos, origem externa e links abaixo dessa raiz. A raiz de previews configurada
é resolvida antes da checagem (aceita ancestrais vinculados como /tmp e /var no
macOS), mas links nos componentes projeto/issue abaixo dela são recusados.
