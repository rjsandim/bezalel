# APROVADOR HUMANO

Ator externo, nunca agente. Confere propostas concretas e decide sobre o conteúdo
exato. A interação real identifica pessoa, fonte, data/fuso e objeto/versão.
Silêncio, parecer de agente, rótulo, JSON, hash e CI verde não substituem decisão.

- [Produto/escopo](../company-flow-v2.md#process-product): regra, comportamento
  esperado, reclassificação, escopo vN da feature e mudanças não abrangidas por
  decisão anterior. Rejeitar uma solução não descarta automaticamente a intenção.
- [Banco](../company-flow-v2.md#process-bankDecision): estrutura, qualquer migration
  e transformação complexa de relações antes da implementação dependente.
- [Risco](../company-flow-v2.md#process-risk): adiamento de médio/baixo confirmado,
  com motivo, dono e prazo/condição. Crítico/alto confirmado não é elegível.
- [Aceite](../company-flow-v2.md#process-accept): executar o roteiro e decidir sobre
  o candidato realmente testado; planilha gerada ou executada por agente não basta.

Aproveite decisão já existente que cubra exatamente o objeto. Mudança material
exige reconferir o que foi abrangido; não fabricar uma nova resposta nem repetir
uma pergunta resolvida. O humano conduz merge, deploy e ações de produção depois
do handoff. Autorizar PR não autoriza essas ações.
