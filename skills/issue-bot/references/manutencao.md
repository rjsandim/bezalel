# Manutenção da skill

Leia somente ao alterar scripts, prompts ou o contrato desta skill. Usar a skill em um
projeto não exige rodar estes testes.

Na raiz do Bezalel:

```sh
python3 -B -m unittest tests/test_handoff.py tests/test_ci_gate.py tests/test_issue_session.py tests/test_issue_bot.py -v
bash -n skills/issue-bot/scripts/issue_session.sh
```

Os testes simulam `gh`, `tmux`, `codex`, `claude` e a skill env; não acessam rede, não
anexam ao terminal do operador e não fazem merge. O teste de fumaça com tmux real usa
servidor isolado (`TMUX_TMPDIR` temporário) e CLIs simulados; só roda com
`ISSUE_BOT_TMUX_SMOKE=1`.

Ao mudar o schema do handoff, atualize juntos `references/handoff.schema.json`, os
exemplos, `scripts/check_handoff.py`, os prompts e `agents/issue-bot.md`. Ao atualizar
os CLIs, confira as flags registradas em [sessão tmux](sessao-tmux.md).
