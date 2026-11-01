<a id="process-bug"></a>

# Qualificar e conduzir o bug

**Referência:** `bug`. **Responsável:** Product Manager.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Entrada e manutenção do cenário 1: relato, decisões de produto e destinos sem correção.

1. **Garantir o registro mínimo.** Localizar/verificar a issue existente, ou registrar relato e fonte na conversa da tarefa quando não houver issue. Criar issue somente se fizer parte do pedido. Decisão integral de adiamento/descarte segue ao destino; retomada reabre/verifica o objeto existente autorizado.

2. **Definir a necessidade.** Aplicar iss-audit no modo PM para qualificar necessidade, esperado/observado, impacto, perfis/dados, hipóteses e critérios. Não exigir causa comprovada para investigar. Dúvida de regra, esperado ou reclassificação exige decisão humana. Usar humanizer somente se a redação precisar de revisão.

3. **Entregar contexto ou registrar destino.** Aplicar R9 na mesma issue. Revisão parcial preserva a intenção restante e confere a decisão sobre o conteúdo atualizado; decisão integral não exige detalhamento/investigação. Descarte/adiamento/reabertura têm estados reais verificados; falha permanece no PM. Transferência humana a 2 ou 3 exige destino iniciado/verificado, mesmo se adiado. Encerrar como comportamento esperado só com confirmação humana, justificativa e fechamento verificado, registrando ausência de correção. Caso qualificado segue ao TL.

**Pronto:** issue real e contexto suficiente para investigação; ou destino próprio decidido e verificado. Não exige comprovar a causa para iniciar.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Transferência verificada para 2 ou 3 | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Falha de registro/reabertura/verificação: preservar rascunho e atribuir retomada ao PM.
- Etapa 2 → **Decisão de produto necessária**: Regra, escopo, comportamento esperado ou reclassificação precisam de decisão humana.
- Etapa 3 → **Intenção adiada e registrada**: Decisão integral de adiar registrada; issue aberta verificada, dono e retomada definidos.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte ou comportamento esperado possuem decisão humana e fechamento verificado.
- Etapa 3 → **Transferência verificada para 2 ou 3**: Destino 2 ou 3 iniciado e verificado com a mesma issue.

**Diferenças por cenário:**

- **Cenário 1:** Bug: fonte, observado/esperado, reprodução, impacto e critério de correção. Comportamento esperado exige decisão humana e fechamento verificado.
