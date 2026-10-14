---
name: env
description: Cria e gerencia ambientes locais com Git worktree e Docker, usando manifesto por projeto, base configurada/detectada e contexto Docker validado. Use para init, new, update, start, ensure, stop, restart, status, config, xdebug e destroy. Operações compartilhadas e destrutivas exigem escopo explícito.
---

# ENV

## Objetivo e escopo

Gerencie ambientes isolados por projeto, com serviços PHP/Node, bancos locais,
proxy e worktrees. A implementação usa Bash, templates e auxiliares Python.
Não é uma ferramenta de deploy ou limpeza global de Docker.

MySQL/PostgreSQL podem usar instância compartilhada com database e usuário próprios
por ambiente/serviço. Redis 7 pode compartilhar o servidor com usuário, prefixo e
dois bancos lógicos por serviço. Para configurar ou migrar, leia
[bancos compartilhados](references/bancos-compartilhados.md).

## Entradas e pré-requisitos

- Diretório do repositório alvo, com pelo menos um commit; execute os comandos
  a partir dele. Os helpers também reconhecem worktrees desse repositório.
- Pasta desta skill (`SKILL_DIR`) resolvida a partir da instalação efetivamente
  carregada. Não use caminhos fixos de outro agente ou instalação antiga.
- `.envstack/stack.yaml`: serviços, banco, `base_ref`, `engine` e `docker_context`.
  `database_mode: shared` habilita um pool explicitamente configurado; a ausência
  mantém o modo exclusivo. Não converta ambientes existentes sem migrar seus dados.
- Bash; Python 3.9+; Git com `--path-format`/`--end-of-options`; `yq` de Mike Farah
  v4, `jq`, `envsubst`; Docker/Compose com `--wait --wait-timeout`.
- Operação completa é orientada a macOS/Homebrew, mkcert, dnsmasq e Traefik.
  Outros sistemas não foram certificados. Testes locais usam processos simulados.

## Procedimento

1. Confirme o projeto, a ação e os recursos afetados. Leia o
   [guia de operação](references/operacao.md) para os detalhes de cada comando.
2. Use `bash "$SKILL_DIR/scripts/detect.sh"` para um manifesto novo e revise-o.
   Detect não sobrescreve manifesto existente. `init.sh` materializa somente
   arquivos locais, sem instalar DNS, certificados ou iniciar containers.
3. A base de nova branch vem de `base_ref`, depois `origin/HEAD` já conhecido
   localmente, depois a única branch existente entre `main` e `master`. Falta,
   ambiguidade ou referência inválida interrompem a criação; não há fetch.
4. O contexto precisa existir e ser explícito. `auto` requer `docker_context`;
   não significa usar o contexto ativo. Cada estado registra raiz do projeto e
   contexto; divergências bloqueiam operação sobre o ambiente salvo.
5. `ENV_DRY_RUN=1 bash "$SKILL_DIR/scripts/new.sh" <nome>` gera worktree,
   Compose e arquivos locais. Não é somente leitura, mas não altera infraestrutura.
6. Para new/update/start/ensure com possível ação sobre o proxy compartilhado,
   informe o impacto e use `ENV_ALLOW_SHARED_INFRA=1` somente na execução já
   autorizada. Não exporte essa autorização permanentemente no shell.
7. Para destroy, preserve dados e confirme o alvo com
   `--confirm <projeto>/<ambiente>`. Use `--keep-worktree` quando arquivos ou
   commits precisarem ser mantidos. A presença da flag não substitui a autorização
   do usuário. Propriedade de volumes e uso por outros containers são conferidos.

## Saídas

- `.envstack/`: manifesto/Dockerfiles/boot versionáveis e templates de ambiente
  locais ignorados, que podem conter valores privados do projeto.
- `.worktrees/<nome>/`: código e configurações locais do ambiente.
- `state/<projeto>/<ambiente>/` dentro da skill: Compose, seleção de serviços,
  identidade do repositório e contexto Docker. É estado local ignorado pelo Git.
- Status, URLs e códigos de saída; falha não é anunciada como sucesso.
- Pools em `state/_databases/`, separados do ciclo de vida das features. Estado e
  credenciais são privados; preserve-os junto dos backups dos bancos.
- Pools Redis em `state/_redis/`, com alocações persistentes de bancos lógicos,
  ACLs e dados. O banco zero é reservado; esse modo atende desenvolvimento local
  confiável, não separação entre clientes hostis nem Redis Cluster.

## Validação

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Os testes criam repositórios descartáveis e simulam Docker e comandos de sistema;
somente a validação estática de Compose usa o CLI real, sem daemon. O roteiro
`tests/integration_lifecycle.py` usa containers reais e exige autorização e
ambiente descartável específicos; não faz parte da validação segura padrão.

## Limites operacionais

DNS, CA de certificados, Traefik, rede proxy e portas 80/443 são compartilhados.
New/update podem afetá-los somente com autorização explícita. A limpeza de um
ambiente não remove essa infraestrutura nem imagens compartilhadas.

Destroy também preserva databases, bancos lógicos, usuários e alocações dos pools. Não
anuncie exclusão SQL nem economia de memória medida sem evidência correspondente.

Destroy recusa estado desconhecido, contexto divergente, volumes de outro
projeto ou usados por outros containers. Sem `--keep-worktree`, também recusa
arquivos locais e commits não integrados. Não força remoção nem tenta adivinhar
recursos por prefixos. Uma falha pode deixar remoção parcial; preserve o estado,
registre o ocorrido e investigue antes de repetir. Não há transação entre Git e
Docker nem proteção contra todas as mudanças concorrentes.

Estados antigos sem `project-root`/`docker-context` exigem auditoria manual de
origem e associação antes de registrar esses campos. Não migre ou adote um estado
apenas por semelhança de nomes. A cópia da skill não migra o estado da instalação
antiga. Segredos e arquivos locais nunca entram no Git ou nos relatórios.
