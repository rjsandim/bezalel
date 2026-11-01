<a id="process-pr"></a>

# Abrir PRs e entregar próximos passos

**Referência:** `pr`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Entrega técnica com todas as PRs necessárias abertas/verificadas assim que desenvolvimento e validações terminarem. O aceite humano e a conferência de merge vêm depois, na PR; manter o ambiente para essa avaliação.

1. **Conferir autorização, candidato e evidências.** Identificar repositórios e branch de produção nas instruções do projeto, sem presumir nome. A adoção deste fluxo com o pedido de desenvolvimento inclui publicar a branch da tarefa e abrir a PR após as validações, salvo restrição expressa do usuário/projeto. Conferir candidato completo, banco/UI/UX, review, AppSec, QA e roteiro; todos na versão correspondente. Aceite funcional posterior não bloqueia a abertura. Comparar composição, base/head/diff, contratos, schema/dados, dependências/configuração. Sem mudança material, reutilizar pareceres válidos; diferença material ou dúvida de impacto exige revalidação afetada. Checks obrigatórios disponíveis antes da abertura precisam passar.

2. **Abrir e verificar as PRs reais.** Publicar somente branches autorizadas e abrir/verificar todas as PRs necessárias com base/head, issues e evidências corretos, usando o [template de PR](../templates/pull-request.md), abertas e prontas para revisão (`draft: false` no serviço); humanizer pode revisar a descrição antes da publicação. Preservar PRs já abertas e retomar somente o faltante após falha, sem duplicar. Se uma PR anterior estiver em draft, marcá-la como pronta para revisão após as validações e conferir o estado; não entregá-la como draft. Sem verificação, manter pendência; divergência confirmada volta ao TL/revalidação. Não habilitar auto-merge.

3. **Conferir até o handoff e orientar o solicitante.** Reler estado/base/head das PRs e candidato até o handoff: divergência confirmada, inclusive pós-abertura, retorna à coordenação. Informar CI disparado apenas pela PR no estado observado, inclusive pendente/falho e distinguindo checks prévios; falha observada volta ao dev integrador na mesma branch, sem acompanhamento contínuo. Publicar na PR o plano de reversão e a instrução de retomada pós-merge: avisar o merge na conversa ou na issue para fechar issues e encerrar o ambiente. Entregar links, ordem de integração/liberação, validações, riscos/pendências e passos manuais de merge/deploy/dados/recuperação; humanizer pode revisar a orientação. Concluir a entrega técnica com todas as PRs verificadas e roteiro apresentado. Rejeição ou ajuste humano posterior retoma correção e validações afetadas na mesma PR; aprovação ou aviso de merge retoma a conferência pós-merge.

**Pronto:** todas as PRs abertas, prontas para revisão e sem draft, com próximo passo manual entregue para a versão validada. PR aberta não prova merge, deploy ou publicação em produção.

| Saída | Tipo | Destino |
|---|---|---|
| PRs verificadas e roteiro entregue | Encaminhamento | Executar roteiro e decidir aceite |
| Aprovação ou aviso de merge recebido | Encaminhamento | Conferir merge e encerrar a tarefa |
| Versão divergente ou revalidação necessária: TL | Impedimento/reprovação | Coordenar a entrega |
| Abertura, verificação ou orientação pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Versão divergente ou revalidação necessária: TL**: Versão/condição mudou materialmente ou falta evidência obrigatória que exige ação de outro responsável.
- Etapa 1 → **Abertura, verificação ou orientação pendente**: Falta autorização/acesso já encaminhado; manter rascunho e condição de retomada.
- Etapa 2 → **Versão divergente ou revalidação necessária: TL**: A leitura comprova base/head/composição divergente do candidato validado.
- Etapa 2 → **Abertura, verificação ou orientação pendente**: Não foi possível abrir ou verificar alguma PR; preservar as existentes e retomar o faltante.
- Etapa 3 → **Versão divergente ou revalidação necessária: TL**: Antes do handoff, foi confirmada divergência material ou nova questão de segurança, mesmo com PR já aberta.
- Etapa 3 → **Abertura, verificação ou orientação pendente**: Orientação não entregue ou estado das PRs não verificável, sem divergência confirmada.
- Etapa 3 → **PRs verificadas e orientação entregue**: Todas as PRs necessárias foram abertas/verificadas no candidato válido e a orientação foi apresentada a Rafael.
