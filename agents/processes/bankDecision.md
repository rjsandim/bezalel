<a id="process-bankDecision"></a>

# Decidir a proposta de banco

**Referência:** `bankDecision`. **Responsável:** APROVADOR HUMANO.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Decisão sobre o HTML apresentado antes da implementação dependente, incluindo estrutura e diferença entre estado atual e proposta.

1. **Conferir conteúdo e alcance.** Examinar HTML, base/versão, estrutura, impactos, alternativas e limites. Esclarecer lacunas antes de decidir; não requer envio a outra ferramenta.

2. **Decidir a versão exata.** Aprovar, pedir ajuste ou rejeitar a proposta final em interação real. Pedido de ajuste volta ao TL para novo HTML e nova avaliação; não é autorização para implementar. Aprovação anterior só vale para o conteúdo/base/escopo que efetivamente cobre.

3. **Devolver ao TL.** TL preserva decisão e resumo, exclui/verifica o HTML temporário após decisão final e só então retoma interface ou implementação dependente com demais condições satisfeitas. Rejeição não cancela a intenção automaticamente; TL/PM tratam o próximo passo. Se o humano voltar a mudar a proposta, reapresentar uma nova versão.

**Pronto:** decisão final identificada ou ajuste claramente solicitado; nenhum agente decide pelo humano.

| Saída | Tipo | Destino |
|---|---|---|
| Aprovação final registrada | Encaminhamento | Coordenar a entrega, após excluir o HTML |
| Ajuste solicitado | Encaminhamento | Preparar a proposta de banco |
| Rejeição final | Encaminhamento | Coordenar a entrega, após registrar e excluir o HTML |
| Aguardando decisão ou esclarecimento | Estado próprio | Permanecer nesta atividade |

**Condições locais das etapas:**

- Etapa 2 → **Aguardando decisão ou esclarecimento**: Resposta ausente, ambígua ou de outra versão.
- Etapa 2 → **Ajuste solicitado**: Alteração solicitada sem aprovação do conteúdo novo.
