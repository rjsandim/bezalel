# Acompanhar a sessão por issue

Pré-requisitos: tmux instalado pelo operador, Codex e Claude Code logados pelas
contas (`codex login`, `claude auth login`), nunca API key. O script não instala,
não lê arquivos de credenciais e não modifica configuração persistente.

```sh
bash /caminho/bezalel/scripts/issue_session.sh create --project-name rcastello --issue 122 --cwd /caminho/projeto/.worktrees/issue-122
bash /caminho/bezalel/scripts/issue_session.sh hint --session rcastello-122
tmux attach -t rcastello-122
```

`Ctrl+b` depois `n` troca codex/claude; `Ctrl+b` depois `d` sai sem encerrar.
Você pode digitar diretamente para intervir. Nome humano: `RCastello - #122`.
A pasta precisa ser a raiz registrada da worktree com a branch da issue; outra
branch requer `--branch` explícita. issue_bot.py session-up prepara essa worktree.
Sessões alheias não são adotadas; idempotência preserva CLIs/logs quando o vínculo
é o mesmo. CLI morto ou sessão alterada exige diagnóstico, não texto enviado ao shell.

```sh
bash /caminho/bezalel/scripts/issue_session.sh send --session rcastello-122 --window codex --text-file /caminho/projeto/prompt.md
bash /caminho/bezalel/scripts/issue_session.sh capture --session rcastello-122 --window claude
bash /caminho/bezalel/scripts/issue_session.sh status --session rcastello-122
bash /caminho/bezalel/scripts/issue_session.sh logs --session rcastello-122 --window codex
bash /caminho/bezalel/scripts/issue_session.sh destroy --session rcastello-122
```

Send usa buffer tmux como texto, sem interpolar shell; capture usa capture-pane
-p -J. Logs usam pipe-pane -o com append (só quando não há pipe ativo, sem alternar o
pipe existente), em `.bezalel/logs/` do checkout principal,
fora da worktree efêmera. `--log-dir` alternativo deve ficar nesse projeto, sem
symlink e fora de `.worktrees/`. Arquivos são privados e gitignorados; a captura
contém a conversa real e não oferece anonimização automática. Nunca imprima
segredos/dados privados nas sessões. Destroy encerra a sessão, preserva logs e ENV.
Status JSON informa janelas, processos e caminhos. Saídas: 0 ok, 1 erro.

## Flags e limites verificados

Em 13/11/2026, ajuda local: Codex CLI 0.163.0 e Claude Code 2.1.316. Nenhuma sessão real de Codex/Claude foi iniciada como teste. A fumaça tmux
usou cat em socket temporário isolado, sem contas e sem infraestrutura. A cada create o script confirma flags/login, sem
imprimir dados da conta. Codex login status deve indicar ChatGPT; Claude auth
status --json precisa ter loggedIn=true e authMethod=claude.ai. Sinal diferente
falha fechado e pede login/verificação da versão, sem fallback para chave.
Variáveis de chave/provedor conhecidas na invocação são recusadas; as mesmas são
removidas do ambiente herdado do servidor tmux. Não são exportadas pelo script.

Codex interativo usa `--sandbox workspace-write --ask-for-approval never --cd`
e `--no-alt-screen --no-daemon`, forced_login_method=chatgpt e model_provider=openai.
Limpa writable_roots herdados e habilita rede para gh na invocação, sem alterar
configuração persistente. Não usa exec, full-auto nem bypass de sandbox. A pasta
de handoffs do projeto é
um `--add-dir` explícito; não há acesso de escrita amplo ao checkout principal.
O sandbox pode bloquear operações Git/rede/configurações e falhas ficam visíveis;
não usar bypass como correção. Consulte a
[documentação oficial OpenAI](https://learn.chatgpt.com/docs/agent-approvals-security).

Claude interativo usa `--dangerously-skip-permissions` junto de sandbox enabled,
failIfUnavailable=true, allowUnsandboxedCommands=false e excludedCommands vazio,
passados por --settings. Sem execução fora do sandbox para contornar falhas.
Só a ferramenta Bash é exposta, com hooks desabilitados, fontes de settings locais
não carregadas e MCP estrito vazio; instruções e skills de auditoria são lidas
pelos arquivos do pacote. A pasta de handoffs é permitida explicitamente.
Segundo a [documentação Claude](https://code.claude.com/docs/en/sandboxing), o
sandbox restringe shell, não hooks/MCP/ferramentas de arquivo; por isso estes não
são disponibilizados nesta sessão. A configuração não é uma política administrada
imutável nem garante confinamento de leituras: os sandboxes mantêm leituras de
sistema necessárias. cwd sozinho não é isolamento. Configuração gerenciada da
organização pode impedir execução; o operador deve conferir o sandbox no piloto
real, sem alterar credenciais, CA, DNS ou permissões para passar o teste.
