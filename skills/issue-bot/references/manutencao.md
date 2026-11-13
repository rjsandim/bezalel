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

Usa socket temporário, configuração tmux vazia e cat nas duas janelas. Não inicia
CLIs de conta, não usa rede nem infraestrutura real e não toca sessões do operador.
O teste padrão pula essa fumaça; os demais casos usam dublês. Um piloto real com
Codex/Claude, autenticação e sandbox efetivos é uma verificação própria, assim como
ENV/restore no consumidor. Não instalar pré-requisitos para contornar ausência.
