<a id="process-bank"></a>

# Preparar a proposta de banco

**Referência:** `bank`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Proposta HTML temporária quando há estrutura, qualquer migration ou transformação complexa de relações. A fonte é o código/schema/migrations da base real identificada no projeto; não consultar produção para produzir a proposta.

1. **Conferir impacto e base.** Identificar repositório, commit/base, estrutura, dados, relações, consumidores e escopo. Toda migration, inclusive de dados, exige decisão anterior à implementação dependente. Relações complexas exigem parecer técnico identificado do TL ou revisor competente disponível, sem ferramenta específica obrigatória. Falta de fonte/evidência material bloqueia; não inventar estado atual.

2. **Preparar o HTML revisável.** Partir do [template HTML](../templates/database-review.html) e salvar somente a cópia da tarefa em `.bezalel/reviews/database-<tarefa>-<versao>.html`. Antes de gerar, conferir/adicionar `/reviews/` ao `.bezalel/.gitignore` preservando regras existentes; a cópia não entra em Git. Mostrar estrutura atual e proposta lado a lado: tabelas, colunas/tipos/nulabilidade/defaults, chaves, índices, restrições e relações/cardinalidades; identificar adições, alterações, remoções e o que permanece. Usar tabelas legíveis por entidade, com uma linha por coluna e campos explícitos para nome, tipo completo, relação (destino e cardinalidade), finalidade de uso na funcionalidade/negócio e regras. Destacar visualmente nomes, tipos e relações; marcar adições em verde, alterações em amarelo, remoções em vermelho e itens mantidos em cinza, sempre com rótulos textuais e legenda, contraste legível e sem depender somente da cor. Não apresentar a estrutura apenas em blocos de texto/SQL monocromáticos; SQL complementar deve ter destaque de sintaxe. Em mudança só de dados, mostrar seleção e transformação antes/depois, sem inventar mudança estrutural. Explicar necessidade, alternativas, consumidores, compatibilidade, migração/backfill, locks/volume, validação e recuperação. proposta-banco reúne o procedimento de montagem, apresentação e fechamento; clean-architecture apoia fronteiras; verification-planning apoia provas. HTML autocontido, UTF-8, sem scripts remotos, credenciais ou dados pessoais; inspecionar a renderização antes de apresentar. Não implementar a migration para ilustrar a proposta.

3. **Submeter e preservar a decisão.** Apresentar o HTML acessível, base/escopo e versão exatos ao humano. Registrar referência, resumo suficiente da estrutura/diferenças, hash dos bytes e eventual parecer na issue ou conversa; hash não é aprovação. Ajuste solicitado mantém a proposta pendente: atualizar o HTML, identificar nova versão e reapresentar. Após aprovação ou rejeição final, registrar a interação real e o conteúdo decidido fora do HTML, excluir somente as cópias temporárias dessa proposta e verificar a ausência. Falha de registro ou exclusão mantém pendência; não remover o template do pacote. Nova mudança material exige novo HTML e decisão.

**Pronto:** HTML apresentado com base e conteúdo verificáveis; após decisão final, registro preservado e cópias temporárias excluídas. Aprovação não é inferida da exclusão.

| Saída | Tipo | Destino |
|---|---|---|
| Proposta identificada: decisão humana | Conclusão da atividade | Decidir a proposta de banco |
| Ajuste solicitado | Encaminhamento | Preparar a proposta de banco |
| Fonte, registro ou exclusão pendente | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Fonte, registro ou exclusão pendente**: Base/estrutura real ou análise necessária indisponível.
- Etapa 3 → **Ajuste solicitado**: Humano pede reformulação; não interpretar como aprovação ou rejeição final.
- Etapa 3 → **Fonte, registro ou exclusão pendente**: Não foi possível preservar a decisão ou excluir o HTML após a decisão final.
