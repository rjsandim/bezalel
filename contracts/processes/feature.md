<a id="process-feature"></a>

# Definir e conduzir o escopo da feature

**Referência:** `feature`. **Responsável:** Product Manager.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Entrada e manutenção do cenário 3: visão e histórias aprovadas como conjunto, com um responsável pela integração.

1. **Registrar visão e histórias.** Identificar a demanda principal na issue existente ou conversa. Aplicar iss-audit no modo PM para qualificar visão, necessidades, limites, perfis/dados/integrações e questões de segurança. Vincular histórias curtas com referências distintas, critérios individuais, dependências e exclusões; a principal reúne critérios globais. Não inventar URLs ou criar issues só para satisfazer o contrato. humanizer pode revisar a redação antes de submeter a versão.

2. **Submeter ou conferir a versão do escopo.** Registrar visão/limites/prioridades e histórias em comentários vN na principal e em cada história, preservando o conteúdo submetido. Obter decisão humana sobre esse conjunto antes do planejamento técnico. Mudança material cria vN+1 e confere decisão correspondente; aproveitar resposta já explícita que cubra a mudança/resultante.

3. **Entregar a mesma versão ou registrar destino.** Aplicar R9 na mesma issue: revisão parcial preserva a intenção restante e confere a decisão atual; destino integral dispensa detalhamento/investigação. Descarte abrange somente itens exclusivos autorizados; reabertura inclui somente histórias descartadas retomadas pelo humano. Verificar estados reais e manter falha pendente no PM. TL confirma recebimento da vN aprovada; divergência volta ao PM, e falta de acesso não é revisão fictícia de escopo.

**Pronto:** principal e histórias vinculadas, escopo vN com decisão correspondente e entrega ao TL; ou destino próprio verificado.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Não foi possível registrar ou verificar a principal/histórias necessárias; preservar pendência PM.
- Etapa 2 → **Decisão de produto necessária**: Escopo vN ainda não possui decisão humana que cubra seu conteúdo exato.
- Etapa 3 → **Intenção adiada e registrada**: Adiamento integral registrado e estados abertos/retomada verificados.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte decidido; principal e histórias exclusivas abrangidas fechadas/verificadas.

**Diferenças por cenário:**

- **Cenário 3:** Feature: principal e histórias, comentários de submissão vN, decisão humana correspondente e handoff da mesma versão ao TL.
