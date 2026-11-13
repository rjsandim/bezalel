Modo issue-bot do Bezalel — resposta à revisão da PR #{{pr}} (issue #{{issue}}).
Ciclo {{cycle}}, rodada {{round}} de no máximo {{max_rounds}}.

O revisor gravou `{{claude_handoff_path}}`. Leia-o inteiro e responda item a item.

Regras obrigatórias:
- Trabalhe só dentro de `{{project_root}}`, na worktree `{{worktree}}` (branch `{{branch}}`).
- Não faça merge, auto-merge nem deploy; não altere nem leia produção.
- Não use chave de API.
- Não invente critérios de aceite nem amplie o escopo além dos ajustes pedidos.
- Mudança de schema ou migration exige parar e pedir decisão humana antes.
- Grave a resposta exatamente em `{{handoff_path}}`, no schema `{{schema_path}}`
  (exemplo: `{{codex_example_path}}`).
- Textos para o humano em português do Brasil. Sem segredos no handoff.

Procedimento:
1. Corrija todos os ajustes `bloqueante`; para cada um, faça commit e registre
   `status: corrigido`, `como` e o SHA em `commit`.
2. Se discordar de um bloqueante, registre `nao_corrigido` com o motivo técnico em `como`;
   o revisor decide na próxima rodada.
3. Ajustes `sugestao` podem ficar `nao_corrigido`, explicando em `como` por que ficaram fora.
4. Publique os commits na mesma PR (push normal). A CI volta a ser conferida antes da
   próxima revisão; correções de CI não contam rodada.
5. Confira o arquivo com `{{check_command}} --role par` e corrija até passar.

Campos: schema_version 1, papel "codex", issue {{issue}}, pr {{pr}}, rodada {{round}},
ciclo {{cycle}} (omita quando 1), candidato (base, head, sha do HEAD após as correções),
ajustes (id, status, como, commit) e gerado_em com fuso.
