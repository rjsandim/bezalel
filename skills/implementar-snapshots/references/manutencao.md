# Manutenção da skill

Leia somente ao alterar esta skill. Implementar snapshots em um projeto não
exige estes passos.

A skill é documental e não tem suíte própria: a fixture
[tiny-relations.json](../templates/tiny-relations.json) define resultados
esperados para os testes do projeto consumidor, não um motor de snapshots.
No repositório do Bezalel, rode o checker (`python3 -B scripts/check_repository.py`)
e `git diff --check`, confira links e metadados e revise se os cenários de
[testes](testes.md) continuam coerentes com [segurança](seguranca.md). Comandos
destrutivos de projetos ficam fora dessa verificação.
