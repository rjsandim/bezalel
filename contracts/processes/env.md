<a id="process-env"></a>

# Preparar, recuperar ou encerrar o ambiente

**Referência:** `env`. **Responsável:** Engenheiro DevOps.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Preparação/recuperação durante o trabalho e encerramento somente após a conferência pós-merge. Usar a skill env carregada e seu contrato de bancos compartilhados; não implementar outro destruidor de ambientes.

1. **Conferir alvos e autorização.** Usar env para conferir projeto, manifesto/base/contexto, recursos e ação: preparar, reutilizar, recuperar ou encerrar. Registrar durante a tarefa repositório, branch da worktree, caminho, ambiente associado e contexto Docker. Na limpeza, receber prova de merge e tratamento das issues; resolver `{{current-worktree-branch}}` pela branch da tarefa registrada, não pela branch do terminal após trocar de diretório. Na criação, escolher a descrição curta de R5 e passar esse nome à ENV, que cria a branch e `.worktrees/<nome>`; não criar outra worktree com nome ou prefixo imposto pelo aplicativo. Conferir colisões antes de criar; quando precisar distinguir tarefas, acrescentar uma palavra ou número significativo, sem reutilizar ambiente alheio. Em ambientes preexistentes, conferir a associação exata no estado da skill: nomes podem diferir e devem ser preservados, sem renomear branch, pasta, dados ou estado automaticamente. Ausência/ambiguidade mantém pendência, sem adivinhar nomes ou criar ambiente para destruí-lo.

2. **Executar a operação pertinente.** Aplicar o procedimento de env e, quando houver pools, sua referência de bancos compartilhados. Na classe pequena sem serviços, a prova é a worktree própria, com as demais dimensões não aplicáveis e o motivo em uma linha. Entregar prova de isolamento de arquivos, banco, filas, portas e storage conforme R5; arquivos sempre comprovados, demais dimensões não aplicáveis somente com motivo. Em pools, comprovar recursos/credenciais próprios, configuração dos consumidores e recusa de acesso cruzado. Preservar dados/configurações; não usar produção nem limpeza como teste. Para encerrar, preservar arquivos rastreados/não rastreados/ignorados, commits, dados e backups necessários fora da worktree; verificar a preservação. Executar o destroy da skill no projeto correto com o nome de ambiente associado e confirmação exata `projeto/ambiente`, a partir de um diretório que não será removido. Não usar força, excluir por prefixo ou remover pools/imagens/infraestrutura compartilhada. Squash/rebase pode impedir a prova de ancestralidade: não contornar a proteção; conservar worktree/branch e reportar o que ficou pendente. `--keep-worktree` permite apenas o encerramento parcial autorizado do ambiente após preservar dados, nunca declarar remoção completa da worktree.

3. **Entregar provas e ponto de retomada.** Entregar ao TL identificação, versões, provas e limitações. Na preparação/recuperação, comprovar isolamento e indicar provas invalidadas. No encerramento, verificar recursos removidos e preservados, worktree/branch e resultado da skill; falha ou remoção parcial mantém pendência. Se já destruído, conferir o registro e a ausência dos alvos, sem repetir por nome aproximado. Sem ambiente gerenciado, registrar não aplicável com evidência; não usar limpeza genérica como substituta.

**Pronto:** preparação/recuperação com isolamento comprovado; ou encerramento do alvo exato confirmado, com preservação e resultado documentados. Remoção parcial não é conclusão completa.

| Saída | Tipo | Destino |
|---|---|---|
| Ambiente/prova entregue: TL | Conclusão da atividade | Coordenar a entrega |
| Encerramento conferido: TL | Conclusão da atividade | Conferir merge e encerrar a tarefa |
| Impedimento ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Impedimento ou decisão necessária: TL**: Alvo, necessidade ou autorização está indefinido, ou exige decisão/ação externa.
- Etapa 2 → **Impedimento ou decisão necessária: TL**: Preparação ou prova de isolamento falhou ou divergiu; interromper a parte afetada.
