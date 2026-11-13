# Sessão tmux do modo issue-bot

Uma sessão por issue, chamada `<projeto>-<issue>` em minúsculas (ex.: `rcastello-122`),
com duas janelas nesta ordem: `codex` e `claude`. O script
[`issue_session.sh`](../scripts/issue_session.sh) cria a sessão, liga o log, envia texto
e lê o painel; ele não implementa nem revisa.

## Para quem acompanha

```sh
tmux attach -t rcastello-122
```

- `Ctrl+b` e depois `n`: troca de janela (codex ↔ claude).
- `Ctrl+b` e depois `d`: sai sem encerrar a sessão.
- Pode digitar diretamente na janela para intervir; o orquestrador lê o mesmo painel.
- No primeiro uso de uma pasta, o Codex pode pedir confiança na pasta
  ("Trust this folder?"); responda você mesmo, anexado à sessão.

## Para o orquestrador

```sh
bash "$SKILL_DIR/scripts/issue_session.sh" create  --project-name rcastello --issue 122 --cwd <raiz-ou-worktree> [--log-dir <pasta>]
bash "$SKILL_DIR/scripts/issue_session.sh" send    --session rcastello-122 --window codex --text-file prompt.md
bash "$SKILL_DIR/scripts/issue_session.sh" capture --session rcastello-122 --window claude [--lines 200]
bash "$SKILL_DIR/scripts/issue_session.sh" hint    --session rcastello-122
bash "$SKILL_DIR/scripts/issue_session.sh" logs    --session rcastello-122 --window codex [--log-dir <pasta>]
bash "$SKILL_DIR/scripts/issue_session.sh" status  --session rcastello-122
bash "$SKILL_DIR/scripts/issue_session.sh" destroy --session rcastello-122
```

- `create` é idempotente: reaproveita janelas vivas, não trunca logs e só inicia o CLI
  quando o processo em primeiro plano ainda é um shell. Recusa `--cwd` que não seja a
  raiz do projeto ou de uma worktree registrada, e sessão existente com outra pasta.
- Logs: `tmux pipe-pane -o` para `<log-dir>/<sessão>-codex.log` e `-claude.log`. O
  padrão é `.bezalel/logs/` do checkout principal (ignorado no Git), fora da worktree
  efêmera, para sobreviver ao `env destroy`.
- `send` cola o arquivo com colagem delimitada (`paste-buffer -p`) e envia Enter;
  recusa janela sem CLI ativo ou arquivo que não seja texto.
- `destroy` encerra só a sessão; logs e ambiente `env` ficam intactos.
- Códigos: 0 ok; 1 erro (tmux ausente, nome inválido, CLI sem login de conta, janela morta).

## Flags efetivas e autenticação

Conferidas em codex-cli 0.163 e Claude Code 2.1.316 (13/11/2026); confira `codex --help`
e `claude --help` ao atualizar os CLIs e ajuste `CODEX_FLAGS`/`CLAUDE_FLAGS` no script.

| Janela | Comando iniciado | Efeito |
|---|---|---|
| `codex` | `codex -C <cwd> -s workspace-write -a never -c sandbox_workspace_write.network_access=true` | Interativo, sem prompts de aprovação; escrita restrita à pasta pelo sandbox do Codex; rede liberada para `gh`/`git push`. |
| `claude` | `claude --dangerously-skip-permissions` | Interativo, sem prompts de permissão. |

- O binário iniciado é o mesmo, por caminho absoluto, que passou na checagem de login;
  o shell da janela não troca o executável ao reordenar o `PATH`.
- `OPENAI_API_KEY`, `CODEX_API_KEY`, `ANTHROPIC_API_KEY` e `ANTHROPIC_AUTH_TOKEN` são
  removidas do ambiente de cada CLI. Antes de iniciar, o script exige
  `codex login status` com "ChatGPT" e `claude auth status --json` com
  `loggedIn: true` e `authMethod: "claude.ai"`; outra forma de login sai 1 sem expor
  a saída.
- **Limitação do Claude.** `--dangerously-skip-permissions` não tem sandbox de pasta
  equivalente ao do Codex: a restrição ao projeto vem do `cwd` da janela, do papel
  somente de revisão no prompt e do log persistente da sessão. Prefira rodar em máquina
  do operador, sem credenciais de produção carregadas no shell.
- Sem `--full-auto` nem `--dangerously-bypass-approvals-and-sandbox` no Codex: o modo
  escolhido mantém o sandbox de escrita ligado.
- O `cwd` do Codex é a raiz do projeto: a worktree `.worktrees/issue-<n>` fica dentro
  dela e os metadados Git das worktrees também.
