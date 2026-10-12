# APROVADOR HUMANO

Ator externo humano, **não agente**. Examina propostas concretas e registra suas
decisões reais; nenhum agente pode assumir sua identidade ou inferir aprovação.

- Banco: decide sobre a proposta estrutural exata antes da implementação. Mudança
  da proposta exige nova decisão; silêncio, JSON, hash e CI verde não aprovam.
- Publicação/operação: delimita as ações autorizadas e seus alvos. Aprovar banco,
  push ou PR não autoriza automaticamente merge, deploy ou limpeza.
- Produto: continua cabendo ao usuário decidir alterações de visão/requisito.
  Product Manager e Tech Lead apresentam alternativas e impactos.

Os gates do [fluxo](../workflow.md) e do [registro](../record-contract.md) continuam
válidos. A presença deste ator no catálogo é documental; não autentica decisões.
