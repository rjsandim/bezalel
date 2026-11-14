---
name: issue-bot
description: Conduz uma issue concreta no modo issue-bot com Codex implementador, CI verde, Claude revisor, handoff JSON e ambiente local para aceite humano; merge e deploy continuam manuais.
---

# Modo issue-bot

## Objetivo e escopo

Use quando solicitado conduzir uma issue pelo caminho issue-bot. É adicional à
DreamTeam clássica, sem exigir nove agentes ou Excel. A instalação não o inicia.
A fonte canônica fica em `agents/issue-bot.md` na integração direta e
`contracts/issue-bot.md` no pacote nativo, relativos à raiz deste pacote.

## Entradas e pré-requisitos

Issue com critérios objetivos e fora de escopo; projeto Git, configuração schema 3,
GitHub CLI autenticado e CLIs de conta ChatGPT/Claude. Nunca chave de API.
Python 3.9+, tmux, Codex com `--approve-for-me` e dependências próprias da ENV. Confirme isolamento e escopo.

## Procedimento

1. Resolva `SKILL_DIR` como a pasta desta skill carregada e `BEZALEL_ROOT` como
   seu diretório `../..`. Leia a fonte canônica correspondente à distribuição.
2. Use `python3 "$BEZALEL_ROOT/scripts/issue_bot.py" --help`. Chame session-up,
   implement, ci-gate, review, respond e env-up conforme resultados da mesma issue.
   Todos recebem `--project` e `--issue`. Os [prompts](prompts/implementar.md) são
   materializados pelo CLI; não fingir execução ou conclusão de outro papel.
3. Só Claude com CI verde, sem executar o candidato, aplicando pr-audit e
   security-audit. Use [schema de handoff](references/handoff.md), duas rodadas,
   depois decisão humana real (iterar/finalizar). Correção de CI não conta rodada.
4. Schema de banco, migration ou relações complexas exigem HTML e decisão humana
   antes da implementação; preserve R6. Sem impacto, registre não aplicável.
5. Suba ENV com branch/SHA da PR e dados declarados; aguarde teste de usabilidade
   do humano. Snapshot é único por geração do ambiente; repetição exige aprovação
   humana do comando exato. `--allow-shared-infra` se limita ao ensure. Problemas posteriores abrem novo ciclo sem sobrescrever arquivos.
   Entregue `iphone_url` e `tailnet` do status, os checks executados e as lacunas
   de Safari/iPhone; previews publicados são cópias persistentes. Nunca edite Serve
   manualmente nem use Funnel.
   Merge e deploy só com ordem humana explícita, fora deste CLI.

## Saídas

PR vinculada pronta para revisão; JSONs locais de handoff e status da ENV; sessão
tmux acompanhável e logs privados. Consulte o [guia tmux](references/sessao-tmux.md).
0 sucesso, 1 erro, 2 ajustes/CI falha, 3 pendente, 4 limite humano, 5 decisão de dados
ou infraestrutura. Nenhum código autoriza merge.

## Validação

`python3 "$BEZALEL_ROOT/scripts/check_handoff.py" --project . --issue N` confere
contratos sem rede. CI é conferida por ci_gate.py; ENV usa status --json. Testes
sintéticos do pacote não comprovam um piloto com CLIs ou infraestrutura reais.
Testes da própria skill ficam em [manutenção](references/manutencao.md).

## Limites operacionais

Não instale ferramentas, não use produção e não altere consumidores por inferência.
Não remova sandbox para contornar falha, não fabrique decisão e não faça merge ou
deploy. ENV e infraestrutura compartilhada mantêm autorização e limites próprios.
Não grave credenciais/dumps em log, handoff ou Git. Skills manuais permanecem manuais.
