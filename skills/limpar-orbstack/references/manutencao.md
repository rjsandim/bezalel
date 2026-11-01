# Manutenção da skill

Leia somente ao alterar esta skill. Ela é documental: no repositório do Bezalel,
a manutenção consiste no checker (`python3 -B scripts/check_repository.py`), em
`git diff --check` e na revisão dos cenários abaixo contra o contrato atual de
`destroy` da skill env. Ao alterá-la, Docker mutável, limpeza e integração real
ficam fora dos testes.

## Cenários de revisão sem executar limpeza

| Situação | Resultado exigido |
|---|---|
| Pedido sem projeto/ambiente ou critério delimitado | Pedir o alvo; nenhuma remoção |
| Contexto OrbStack ausente ou manifesto aponta a outro destino | Interromper, sem fallback |
| HEAD integrado, mas há arquivos locais ou dados necessários | Preservar/validar recuperação antes de considerar remoção |
| Volume ou imagem usados por container de outro projeto, mesmo parado | Preservar recurso e não parar o outro container |
| Imagem sem tag e sem prova de origem | Preservar; ausência de tag não comprova elegibilidade |
| Compose/estado sem vínculo inequívoco ao projeto | Preservar, sem busca destrutiva por prefixo |
| Docker/Git recusam operação | Registrar estado parcial; não aumentar força |
| Autorização é apenas copiar ou editar a skill | Somente checks documentais e mocks; nenhum acesso mutável |

Os testes de segurança da ENV simulam contexto incorreto, falha no destroy,
volume compartilhado e preservação de worktree. Não substituem auditoria de um
ambiente real nem constituem execução da limpeza desta skill.
