---
name: env
description: Cria e opera ambientes locais isolados por Git worktree e Docker (serviços PHP/Node, MySQL/PostgreSQL e Redis atrás de Traefik com HTTPS) a partir do manifesto .envstack/stack.yaml do projeto. Use quando o pedido for "sobe um ambiente para essa branch", "cria um ambiente isolado para corrigir-login", "env new/start/stop/status/update/destroy <nome>", "liga o serviço api do ambiente" ou "configura o env neste projeto". Não use para deploy ou servidor remoto (vps-deploy), limpeza em lote de ambientes concluídos (limpar-orbstack), stacks fora de PHP/Node ou máquinas fora do macOS sem adaptação. Os comandos new, start, ensure e update podem instalar dnsmasq e mkcert via Homebrew, usar sudo em /etc/resolver e alterar Traefik e DNS compartilhados, por isso exigem ENV_ALLOW_SHARED_INFRA=1 na execução autorizada; destroy apaga volumes do ambiente e exige --confirm <projeto>/<nome>.
---

# ENV

## Objetivo e escopo

Gerenciar ambientes isolados por projeto, com serviços PHP/Node, bancos locais,
proxy HTTPS e worktrees. A implementação usa Bash, templates e auxiliares Python.
É ferramenta de desenvolvimento local, não de deploy nem de limpeza global de Docker.

MySQL/PostgreSQL podem usar instância compartilhada com database e usuário
próprios por ambiente e serviço; Redis 7 pode compartilhar o servidor com
usuário, prefixo e bancos lógicos por serviço. Para configurar ou migrar, leia
[bancos compartilhados](references/bancos-compartilhados.md).

## Entradas e pré-requisitos

- Repositório alvo com pelo menos um commit; rode os comandos a partir dele ou
  de uma de suas worktrees.
- Nome do ambiente: descrição curta em minúsculas, sem acentos, com hífens, como
  `corrigir-login` (números só quando significativos, como `migrar-php-84`), sem
  prefixos de agente ou tipo nem sufixos aleatórios. Branch, `.worktrees/<nome>`
  e ambiente usam o mesmo nome; ambientes existentes mantêm o nome registrado.
- `$SKILL_DIR`: pasta desta skill na instalação efetivamente carregada.
- `.envstack/stack.yaml` com serviços, banco, `base_ref`, `engine` e
  `docker_context`. `database_mode: shared` usa um pool configurado; sem ele, o
  modo é exclusivo. Converter um ambiente existente exige migrar seus dados.
- Bash, Python 3.9+, Git com `--path-format`/`--end-of-options`, `yq` (Mike Farah
  v4), `jq`, `envsubst`, Docker/Compose com `--wait --wait-timeout`. Operação
  completa testada em macOS com Homebrew, mkcert, dnsmasq e Traefik.

## Procedimento

1. **Confirme projeto, comando e recursos afetados** pela tabela abaixo e leia o
   [guia de operação](references/operacao.md) do comando.
2. **Configure uma vez por projeto.** `detect` gera o manifesto (sem sobrescrever
   um existente); revise-o com o usuário. `init` materializa Dockerfiles, boot e
   `.env.example` em `.envstack/`. Peça ao usuário que versione `.envstack/`
   exceto os `*.env.example`.
3. **Confira base e contexto.** A branch nova parte de `base_ref`, depois de
   `origin/HEAD` já conhecido, depois da única entre `main` e `master`; falta ou
   ambiguidade interrompe (sem fetch automático). O contexto Docker é explícito:
   `auto` exige `docker_context`, e divergência com o estado salvo bloqueia.
4. **Para gerar só arquivos**, use `ENV_DRY_RUN=1 bash "$SKILL_DIR/scripts/new.sh" <nome>`:
   cria worktree, Compose e `.env` sem tocar em infraestrutura.
5. **Para new, start, ensure e update**, informe o impacto na infraestrutura
   compartilhada e rode com `ENV_ALLOW_SHARED_INFRA=1` somente nessa execução
   autorizada, sem exportar a variável no shell.
6. **Antes de testes ou capturas**, rode `ensure <nome> <serviço...>` (ou
   `--all`) e espere os serviços ficarem prontos.
7. **Para destroy**, preserve dados e confirme o alvo com
   `--confirm <projeto>/<nome>`; use `--keep-worktree` quando arquivos ou commits
   precisarem ficar. A flag registra a autorização do usuário, não a substitui.

| Comando | Efeito | Autorização |
|---|---|---|
| `scripts/detect.sh` | Gera `.envstack/stack.yaml` se ausente | Pedido do usuário (arquivo local) |
| `scripts/init.sh` | Gera Dockerfiles, `boot.sh`, `.env.example` e `.gitignore` em `.envstack/` | Pedido do usuário (arquivos locais) |
| `scripts/new.sh <nome> [serviço...\|--all]` | Cria branch, worktree e Compose; sobe serviços; pode instalar dnsmasq/mkcert, usar sudo e reiniciar Traefik | `ENV_ALLOW_SHARED_INFRA=1`; `ENV_DRY_RUN=1` só gera arquivos |
| `scripts/ctl.sh start\|ensure <nome> [serviço...\|--all]` | Liga serviços e dependências e o Traefik global | `ENV_ALLOW_SHARED_INFRA=1` |
| `scripts/ctl.sh stop <nome>` | Para o ambiente; preserva containers, volumes e arquivos | Pedido do usuário |
| `scripts/ctl.sh restart <nome>` | Reinicia só os serviços já ativos | Pedido do usuário |
| `scripts/ctl.sh status <nome>` | Lista containers, inclusive parados | Leitura |
| `scripts/update.sh <nome> [serviço...\|--all]` | Regenera Compose e reconstrói; preserva `.env`, worktree e volumes | `ENV_ALLOW_SHARED_INFRA=1` |
| `scripts/destroy.sh <nome> --confirm <projeto>/<nome> [--keep-worktree]` | Remove containers, volumes exclusivos e estado; sem `--keep-worktree`, também worktree e branch | Pedido explícito do usuário com projeto e ambiente |

`destroy` encerra **um** ambiente identificado. Auditoria e limpeza de vários
ambientes concluídos, com backup e remoção de imagens, ficam com limpar-orbstack.

## Saídas

- `.envstack/`: manifesto, Dockerfiles e `boot.sh` versionáveis; `*.env.example`
  ignorados, pois podem conter valores privados do app.
- `.worktrees/<nome>/`: código e configurações locais do ambiente.
- `state/<projeto>/<nome>/` dentro da skill: Compose, seleção de serviços,
  identidade do repositório e contexto Docker (local, fora do Git).
- Pools em `state/_databases/` e `state/_redis/`, separados do ciclo de vida das
  features; estado e credenciais privados, preservados junto dos backups.
- Status, URLs e códigos de saída; falha é reportada como falha.

## Validação

Confira o resultado de cada comando antes de relatá-lo:

- **detect/init:** os arquivos gerados existem e o usuário revisou pastas,
  tipos, versões e portas do manifesto.
- **new/start/ensure/update:** `bash "$SKILL_DIR/scripts/ctl.sh" status <nome>`
  mostra os serviços pedidos em execução e saudáveis, e cada URL anunciada
  responde por HTTPS (por exemplo, `curl -sk -o /dev/null -w '%{http_code}' <url>`).
  Relate apenas os serviços realmente prontos; prontidão HTTP não substitui os
  testes funcionais da tarefa.
- **Dry-run:** o Compose e os `.env` foram gerados no estado e na worktree.
- **stop/restart:** `status` mostra o estado esperado e os volumes continuam presentes.
- **destroy:** `status` deixa de encontrar o ambiente, os volumes exclusivos
  sumiram e worktree/branch existem ou não conforme `--keep-worktree`; pools e
  infraestrutura compartilhada continuam de pé.

Comandos de teste da própria skill ficam em [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. DNS, CA, Traefik, rede proxy e
portas 80/443 são compartilhados entre projetos; alterá-los exige a autorização
do passo 5. Destroy preserva infraestrutura, imagens, databases, bancos lógicos,
usuários e alocações dos pools; economia de memória ou exclusão SQL só é
anunciada com evidência.

Destroy recusa estado desconhecido, contexto divergente, volumes de outro projeto
ou em uso por outros containers e, sem `--keep-worktree`, arquivos locais e
commits não integrados. Ele não usa força nem remove por prefixo. Falha pode
deixar remoção parcial: preserve o estado, registre e investigue antes de repetir.

Estado antigo sem `project-root`/`docker-context` exige auditoria manual antes
de ser adotado; semelhança de nomes não basta. Segredos e arquivos locais ficam
fora do Git e dos relatórios.
