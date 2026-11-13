Modo issue-bot do Bezalel — ambiente local para o teste humano da issue #{{issue}} (PR {{pr}}).

Suba o ambiente `{{environment}}` (worktree `{{worktree}}`, branch `{{branch}}`) com o
orquestrador, que usa a skill `env` e o campo `data` de `.bezalel/project.json`:

    {{env_up_command}}

Regras obrigatórias:
- Trabalhe só dentro de `{{project_root}}`.
- Não faça merge, auto-merge nem deploy; não leia nem restaure dados de produção.
- Não use chave de API.
- Não invente critérios de aceite; o teste de usabilidade é do humano.
- Infra compartilhada (proxy, DNS, certificados): só com autorização humana nesta
  execução, via `--allow-shared-infra`. Nunca exporte ENV_ALLOW_SHARED_INFRA no shell.
- `data.mode ask` (código 5): pergunte ao humano; `--data-mode empty` só se ele pedir.
- Não crie máquina OrbStack por issue; não use `env destroy` sem pedido explícito.
- Textos para o humano em português do Brasil.

Ao terminar, informe as URLs e a porta do banco do JSON de saída. Problemas de usabilidade
apontados pelo humano voltam ao implementador e abrem um novo ciclo de revisão.
