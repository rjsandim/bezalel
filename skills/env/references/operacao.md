# Skill `env` — ambientes isolados genericos

Dois momentos distintos:

1. **`init`** (uma vez por projeto, resultado **versionado**): detecta as pastas, tipos e versoes e gera a config em `.envstack/`. Voce revisa e **commita**.
2. **`new`/`update`/`destroy`** (por feature, **efemero**): usam a config commitada para criar/derrubar ambientes. Nao detectam nada.

`<projeto>` = nome da pasta raiz do repo git (ou `.project` do manifesto). Nada de hardcode.

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
