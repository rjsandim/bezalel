---
name: issue-bot
description: Conduz uma issue do GitHub no modo issue-bot do Bezalel — sessão tmux com Codex (implementa) e Claude (revisa) interativos, portão de CI verde, no máximo duas rodadas de revisão com handoff JSON, ambiente local pela skill env e merge somente por ordem humana. Use quando o pedido for "toca a issue 122 no modo issue-bot", "abre o bot da issue #122 do rcastello", "revisa a PR da issue com o Claude depois da CI", "responde o handoff da rodada 1" ou "sobe o ambiente da issue para eu testar". Não use para o fluxo clássico de nove papéis da DreamTeam (agents/dream-team.md), para merge/deploy (sempre manuais), para revisão avulsa sem issue (pr-audit) nem para criar ambiente fora de uma issue (env).
---

# Modo issue-bot

## Objetivo e escopo

Levar **uma issue por vez** da implementação ao teste humano com dois executores e um
aprovador: Codex implementa na janela `codex`, Claude revisa na janela `claude` só com
CI verde, e o humano decide banco, iteração após o limite, usabilidade e merge.
É um caminho adicional à DreamTeam clássica, com o rito enxuto descrito na fonte
canônica `agents/issue-bot.md` da base do Bezalel (`contracts/issue-bot.md` no plugin
nativo). A instalação da skill não inicia nada: cada etapa é um comando explícito
para uma issue concreta.

## Entradas e pré-requisitos

- `$SKILL_DIR`: pasta desta skill na instalação carregada; os scripts partem dela.
- Projeto Git com `.bezalel/project.json` no schema 3 (`data` define snapshot, base
  vazia ou pergunta), `.bezalel/.gitignore` com `/handoff/` e `/logs/`, e
  `.envstack/stack.yaml` quando houver ambiente local.
- Issue com critérios de aceite e fora de escopo; sem critérios, o fluxo pede ao humano.
- `gh`, `tmux`, `codex` e `claude` instalados e logados pela conta (ChatGPT e claude.ai).
  Chave de API nunca autentica os CLIs. Python 3.9+ e Bash.
- Flags, teclas e limitações dos CLIs: [sessão tmux](references/sessao-tmux.md).

## Procedimento

Todos os comandos: `python3 "$SKILL_DIR/scripts/issue_bot.py" <comando> --project <raiz> --issue <n>`.

1. **Sessão.** `session-up` cria ou reutiliza `<projeto>-<issue>` (ex.: `rcastello-122`)
   com logs em `.bezalel/logs/` e imprime `tmux attach -t <sessão>` para o humano.
2. **Implementar.** `implement` envia ao Codex o prompt com issue, critérios, branch e
   worktree `.worktrees/issue-<n>`. Ele abre a PR vinculada, sem draft. Mudança de
   schema, migration ou relações complexas para antes, com proposta HTML e decisão humana.
3. **CI.** `ci-gate` espera os checks obrigatórios (ou todos, se o GitHub não distinguir).
   Vermelho (código 2) volta ao Codex; `--send-fix` envia o prompt de correção.
   Correção de CI não conta rodada.
4. **Revisar.** `review` só segue com CI verde, envia o prompt ao Claude (`pr-audit`,
   `security-audit` e, quando couber, `clean-code`/`clean-architecture`) e valida
   `.bezalel/handoff/<issue>-r<n>-claude.json`. Código 0: `pode_mergear`; 2: `ajustes`.
5. **Responder.** `respond` envia o handoff ao Codex e valida `<issue>-r<n>-codex.json`.
   Volte ao passo 3. Com duas rodadas esgotadas, os comandos saem 4: registre a decisão
   humana `iterar` ou `finalizar` em `<issue>-decisao.json`
   ([exemplo](references/decisao.example.json)).
6. **Ambiente.** `env-up` exige `pode_mergear` ou `finalizar`; sobe `issue-<n>` pela
   skill env na branch da PR (`--branch`), com `--allow-shared-infra` somente quando o
   humano autorizar a infra compartilhada nesta execução, e aplica `data` do
   `project.json` commitado (`ask` sai 5; alteração não commitada é recusada).
   `snapshot` mostra o comando exato e seu hash (código 5); depois da aprovação humana,
   repita com `--restore-digest <hash>`. O restore roda uma vez por ambiente.
7. **Teste humano.** Ajustes de usabilidade voltam ao passo 2 e abrem novo ciclo de
   revisão (`review --cycle <n+1>`, arquivos `<issue>-c<ciclo>-r<n>-…`). Merge só com
   ordem explícita do humano, fora deste CLI.

`status` resume issue, PR, CI, rodada, veredito, sessão e ambiente em JSON.
`prepare-prompt <tipo>` e `--dry-run` geram o texto sem enviar teclas ao tmux.

| Código | Significado |
|---|---|
| 0 | Etapa concluída (CI verde, `pode_mergear`, ambiente pronto, sessão ok) |
| 1 | Uso, contrato ou handoff inválido, ferramenta ausente, CLI sem login de conta |
| 2 | CI vermelha ou veredito `ajustes` |
| 3 | CI pendente ou handoff ainda não gravado no prazo |
| 4 | Limite de rodadas sem decisão humana |
| 5 | Infra compartilhada, dados (`ask`) ou ambiente aguardam decisão |

## Saídas

- PR da issue (do Codex), handoffs JSON por rodada e decisão humana em
  `.bezalel/handoff/` (fora do Git), conforme o [schema](references/handoff.schema.json)
  e os exemplos do [Claude](references/handoff-claude.example.json) e do
  [Codex](references/handoff-codex.example.json).
- Logs das janelas em `.bezalel/logs/<sessão>-<janela>.log`, preservados no `session-down`.
- JSON de status, do portão de CI e do ambiente (URLs, portas, banco), sem segredos.

## Validação

- `scripts/check_handoff.py --project <raiz> --issue <n>` imprime o resumo da rodada
  (`veredito`, `bloqueantes_abertos`, `pronto_para_humano`) e sai 0 só com contrato válido.
- `scripts/ci_gate.py --project <raiz> --pr <n> --dry-run` mostra o estado lido da CI.
- `status --project <raiz> --issue <n>` confere sessão viva, rodada e ambiente pronto;
  as URLs do `env-up` respondem antes de pedir o teste humano.
- Testes de manutenção: [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. Nenhum comando faz merge, auto-merge,
aprovação de PR ou deploy, e `pode_mergear` não os autoriza. Os CLIs usam só a conta
logada; as variáveis de chave de API são removidas das janelas. A sessão trabalha na
raiz do projeto ou na worktree da issue. `ENV_ALLOW_SHARED_INFRA=1` vale só para a
execução autorizada, sem exportar no shell; `env destroy` continua exigindo
`--confirm`. O restore roda o comando declarado pelo projeto, que deve recusar
produção; o Bezalel não baixa nem lê dados de produção. Segredos não entram em
handoff, log ou relatório.
