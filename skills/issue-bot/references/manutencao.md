# Manutenção do modo issue-bot

Na raiz da distribuição fonte:

```sh
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s skills/env/tests -v
bash -n scripts/issue_session.sh
git diff --check
```

Fumaça opcional, somente com tmux já instalado:

```sh
BEZALEL_TMUX_SMOKE=1 python3 -B -m unittest discover -s tests -p test_issue_session.py -v
```

Usa socket temporário, configuração tmux vazia, cat e um binário nativo com
nome de versão. Compilador ausente pula essa fumaça; não instala ferramentas. Não inicia
CLIs de conta, não usa rede nem infraestrutura real e não toca sessões do operador.
O teste padrão pula essa fumaça; os demais casos usam dublês. Um piloto real com
Codex/Claude, autenticação e sandbox efetivos é uma verificação própria, assim como
ENV/restore no consumidor. Não instalar pré-requisitos para contornar ausência.

Em 13/11/2026, o checker da master beb16b8 foi executado contra a árvore
corrigida e aceitou o modelo legado. A fumaça tmux opt-in cobriu executável
nativo chamado 2.1.316, send/capture e criação idempotente. O piloto separado
com Codex CLI 0.163.0 autenticado criou commit e push em remoto bare local com
`--approve-for-me`; o sandbox bloqueou add/commit e o revisor automático os
aprovou individualmente. Não foi piloto nos sete projetos nem validação de
restore real, de Claude autenticado ou do fluxo interativo completo.
