Modo issue-bot do Bezalel — a CI da PR #{{pr}} ({{pr_url}}) da issue #{{issue}} falhou.

Corrija a causa na worktree `{{worktree}}` (branch `{{branch}}`), faça commit e push normal
(sem força) para a mesma PR. Esta correção não conta como rodada de revisão: o revisor só
começa quando a CI estiver verde.

Regras obrigatórias:
- Trabalhe só dentro de `{{project_root}}`.
- Não faça merge, auto-merge nem deploy; não altere nem leia produção.
- Não use chave de API.
- Não desligue, pule ou enfraqueça testes e checks para obter verde; corrija a causa.
- Não invente critérios de aceite nem amplie o escopo da issue.
- Mudança de schema ou migration exige parar e pedir decisão humana antes.
- Textos para o humano em português do Brasil.

Estado da CI lido pelo portão (`gh pr checks`):
{{ci_summary}}

Leia os logs de cada check falho (`gh run view --log-failed` ou o link acima), corrija e
responda com o SHA do commit e o que mudou.
