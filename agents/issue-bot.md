# Modo issue-bot

Fonte canônica do caminho adicional ao [fluxo clássico da DreamTeam](dream-team.md).
A [skill issue-bot](../skills/issue-bot/SKILL.md) chama etapas explícitas do
[orquestrador](../scripts/issue_bot.py). Instalar/distribuir arquivos não inicia
sessões, não concede confiança a hooks, nem executa o fluxo. Não é serviço de
observação de produção, daemon ou runtime dos nove contratos clássicos.

## Responsabilidades e rito obrigatório

- Uma issue real contém necessidade, critérios objetivos com IDs e fora de escopo.
  O implementador confirma isso antes de editar; o script preserva o texto integral
  e não tenta inferir requisitos a partir de títulos ou checkboxes.
- Codex implementa na worktree da issue, comprova isolamento de arquivos, banco,
  filas, portas e storage e abre/atualiza PR vinculada, pronta, sem draft e sem
  auto-merge. Claude revisa independentemente; não implementa nem executa código,
  scripts, builds ou testes do candidato. Não se personifica TL nem nove papéis.
- CI verde é obrigatória antes de enviar revisão ao Claude (`review-ready`).
  [ci_gate.py](../scripts/ci_gate.py) consulta checks required; se nenhum é
  declarado, exige todos. Falha de acesso não vira fallback. Ausência de checks,
  skipped/neutral ou resultado desconhecido é pending, nunca verde. O SHA é
  reconferido após a leitura; mudança invalida o resultado. Cada nova versão
  precisa passar novamente. Correção de CI volta ao Codex e não conta rodada.
- Claude lê `gh issue view`, `gh pr view` e `gh pr diff`; aplica
  [pr-audit](../skills/pr-audit/SKILL.md) e
  [security-audit](../skills/security-audit/SKILL.md), com clean-code e
  clean-architecture quando pertinente. As auditorias continuam sem execução do
  candidato; o parecer em prosa é auxiliar ao JSON obrigatório deste modo.
- Proposta HTML e decisão humana exata **antes** de implementar schema de banco,
  qualquer migration ou relações complexas (R6) continuam obrigatórias. Usar base
  real, antes/depois, tabela por entidade com coluna/tipo/relação/finalidade,
  destaques e legenda textual. Ajuste exige reapresentação; após decisão, preservar
  resumo/base/versão/decisão na issue/conversa e excluir/verificar o HTML temporário.
- Duas rodadas por ciclo; depois o humano decide iterar ou finalizar. `pode_mergear`
  significa apenas ausência de impedimento na revisão desse candidato. Sugestões
  podem permanecer; critérios pendentes ou bloqueantes impedem esse veredito.
- Ambiente local via ENV, worktree e Docker, com `data` declarado; nunca criar uma
  máquina OrbStack por issue. O humano testa usabilidade e funcionamento.
- Merge e deploy são manuais, somente por ordem explícita. Nenhum código de saída,
  parecer, JSON ou teste autoriza merge. Este CLI não oferece comando de merge.

## O que não é exigido neste modo

A seleção formal dos nove papéis, QA/AppSec como agentes adicionais, revisão
completa pré-PR e Excel de aceite não são gates do issue-bot. Excel só se o humano
pedir. Etapas `accept`/`accepted` de
[check_delivery.py](../scripts/check_delivery.py) não são pré-requisitos de
`env-up`. O registro clássico é opcional e seus requisitos não foram relaxados.
A DreamTeam clássica conserva nove papéis, revisões pré-PR e Excel em melhoria e
feature e os donos de correção de CI definidos em R2. Seu handoff pode informar CI pending/failed; a etapa adicional
`review-ready` exige CI passed com evidência em todas as PRs do registro.

## Etapas executáveis

Python 3.9+, Git, `gh`, tmux e CLIs autenticados por conta são pré-requisitos;
ENV tem suas próprias dependências. Não instalar ferramentas automaticamente.
Execute a partir da pasta do projeto, usando o caminho real do pacote carregado:

```sh
python3 /caminho/bezalel/scripts/issue_bot.py session-up --project . --issue 122
python3 /caminho/bezalel/scripts/issue_bot.py implement --project . --issue 122
python3 /caminho/bezalel/scripts/issue_bot.py ci-gate --project . --issue 122 --pr 130
python3 /caminho/bezalel/scripts/issue_bot.py review --project . --issue 122 --pr 130
python3 /caminho/bezalel/scripts/issue_bot.py respond --project . --issue 122 --pr 130
python3 /caminho/bezalel/scripts/issue_bot.py env-up --project . --issue 122 --pr 130
python3 /caminho/bezalel/scripts/issue_bot.py status --project . --issue 122
python3 /caminho/bezalel/scripts/issue_bot.py session-down --project . --issue 122
```

Esses são comandos separados: o operador/orquestrador externo acompanha resultados
antes de chamar o próximo. `implement` envia e retorna; `review`/`respond` enviam
e aguardam o handoff por até `--timeout-seconds` (1800 por padrão), sondando a cada
`--poll-seconds`. Timeout não cancela o CLI. Repita com `--round N` para validar a
mesma revisão já concluída, sem reenviar. Arquivo inválido ou candidato alterado
interrompe com 1; o produtor usa rename atômico e o operador corrige o diagnóstico,
sem apagar provas de outra rodada. `ci-gate` com falha envia o prompt de correção
ao Codex; não conta rodada. `status` é leitura instantânea, inclusive sem PR.
`prepare-prompt implement|review|respond|corrigir-ci|subir-ambiente` gera texto sem
enviar, opcionalmente em `--output` novo e interno. `--dry-run` não cria sessão,
worktree, lock, prompt ou ambiente; pode consultar GitHub, mas não envia teclas.

`session-up` prepara `.worktrees/issue-N` com branch padrão `issue-N`; `--branch`
usa outra branch local explícita. Antes da PR, a criação usa `--base-ref` ou a
única base declarada em `production_branches`. Não há fetch silencioso. Com PR,
a branch já deve existir localmente e o HEAD da worktree deve ser o SHA da PR.
A sessão `<projeto>-N` tem janelas `codex` e `claude`; nome humano recomendado:
`<Projeto> - #N`. O [guia tmux](../skills/issue-bot/references/sessao-tmux.md)
explica attach, logs privados, flags, login e limites de isolamento.

## Handoffs, limite e decisões

O [schema 1](contracts/handoff.schema.json), os exemplos
[Claude](templates/handoff-claude.example.json) e
[Codex](templates/handoff-codex.example.json) são o único contrato de veredito e
resposta. São fixtures sintéticas, nunca evidência de trabalho real. Caminhos:
`.bezalel/handoff/N-rR-claude.json` e `N-rR-codex.json`. A rodada só avança após
Claude `ajustes` válido **e** resposta Codex válida. Na rodada seguinte o Claude
confere cada bloqueante anterior; o checker exige o par anterior, mas não
interpreta sua prosa nem comprova cobertura de todos os critérios da issue.

```sh
python3 /caminho/bezalel/scripts/check_handoff.py --project . --issue 122 --role par
```

Sem `--round`, usa a maior rodada do `--cycle` (default 1). O nome coincide com
issue/rodada/papel/ciclo. Ciclo 1 aceita também `N-c1-rR-…`, mas recusa colisão com
o nome simples. Ajuste de usabilidade humano após env-up abre novo ciclo com
`--cycle 2` e `N-c2-r1-…`; não sobrescrever ciclo 1 nem usar ciclo para contornar
limite antes do teste humano. O operador registra a origem desse novo pedido.

Depois de duas revisões com ajustes, `respond`/nova `review` saem 4. O humano
registra `.bezalel/handoff/N-decisao.json` (ciclos seguintes: `N-cC-decisao.json`):

```json
{
  "schema_version": 1, "issue": 122, "pr": 130, "apos_rodada": 2,
  "decisao": "iterar", "autorizado_ate": 4,
  "ator": "identificação da pessoa", "fonte": "referência à interação humana real",
  "registrado_em": "2026-11-13T21:00:00-03:00", "motivo": "decisão real"
}
```

Para usar a decisão, o operador passa `--human-decision-source` com a mesma fonte.
Isso confirma uma declaração explícita do chamador; não autentica a pessoa nem
transforma JSON em prova de autorização. O chamador precisa conferir a interação
humana real. `iterar` libera só até `autorizado_ate`. `finalizar` permite `env-up`
da última versão mesmo com ajustes registrados, sempre com CI verde; nunca merge.
O CLI não fabrica decisões, não oferece autoaprovação e não altera esses arquivos.

## Ambiente e dados

A [ENV](../skills/env/SKILL.md) aceita `--branch` e `--issue` explícitos; o ambiente
`issue-N` pode usar branch diferente. `env-up` confere identidade, branch, SHA e
readiness antes do restore e retorna o JSON público da ENV. Infra compartilhada
exige `ENV_ALLOW_SHARED_INFRA=1` somente na execução previamente autorizada. Sem
ela, sai 5; não deduz autorização de simples arquivos nem altera o perfil do shell.

[project.json](../.bezalel/project.example.json) usa schema 3. Migração explícita:
`python3 /caminho/bezalel/scripts/project.py migrate-config --project .` preserva
campos, acrescenta `data.mode=ask` e é idempotente. Schema 2 é recusado no validador.

- `ask`: código 5 até decidir; `--data-mode empty` vale só para a invocação.
- `empty`: boot/migrations da ENV, sem restore.
- `snapshot`: exige `dataset` tiny/full e `restore` como lista de argumentos;
  `workdir` relativo é opcional (raiz por padrão), `docs` é referência opcional.
  Restore ocorre só depois de ready, no workdir da worktree. Usa exatamente o
  comando declarado, sem shell e sem adivinhar `docker compose exec`. O projeto
  deve validar o destino isolado, suas conexões e recusar produção. Um comando de
  host não recebe automaticamente as variáveis de um container: declare um wrapper
  seguro do próprio projeto quando necessário. Falha não declara sucesso (código 1,
  sem imprimir a saída privada). Nova chamada de env-up executa novo restore:
  confirme que é desejado antes de repetir, pois pode substituir dados de teste.

Instalação e testes do pacote não executam restore, não leem produção nem atualizam
os sete consumidores. A adoção é separada por projeto após publicar/atualizar o
plugin, migrar a configuração e validar o manifesto ENV com o humano.

## Códigos e limites

0: etapa concluída; 1: erro/ferramenta/contrato; 2: CI falha ou ajustes válidos;
3: pendente/timeout; 4: decisão após limite; 5: decisão de dados/infra ou ambiente
não pronto. Em `review`, 0 exige `pode_mergear` válido no candidato atual.
Nenhum código significa autorização de merge. Checks estruturais e testes com
fixtures não certificam o funcionamento real dos agentes, login, isolamento do
aplicativo, Docker, CI remota ou execução de snapshot. Sessão e env têm ciclos de
vida independentes; session-down preserva env/logs. Destroy de ENV continua manual,
com `--confirm projeto/ambiente`, preservação, sem força nem remoção por prefixo.
Skills reservadas à chamada manual continuam fora da automação.
