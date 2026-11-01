<a id="process-qa"></a>

# Validar critérios e jornadas

**Referência:** `qa`. **Responsável:** Engenheiro de QA.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

QA independente da entrega completa. Bug, melhoria e feature usam o mesmo procedimento; as notas do cenário definem a cobertura específica.

1. **Conferir versão e cobertura necessária.** Definir os dados de teste necessários e pedi-los ao DevOps pelo TL quando faltarem. Receber candidato integrado com revisão TL e AppSec válidos; conferir independência e ambiente. Aplicar verification-planning aos critérios/riscos, confrontando e ampliando a cobertura do dev sem copiar apenas sua suíte. Reutilizar plano pertinente, com dados/pré-condições e cobertura específica do cenário.

2. **Executar critérios e jornadas.** Na classe pequena, executar a reprodução, o teste de regressão e 2 a 3 casos vizinhos; ampliar se encontrar falha. Executar comportamento, integração real, regressões e E2E críticos do plano; agent-browser apoia jornadas web quando disponível. Feature exige cada história e depois jornadas/dependências globais no mesmo candidato. Dados exigem seleção, resultado, integridade, repetição e recuperação pertinentes; mobile exige plataformas/dispositivos identificados. Falha ou teste obrigatório ausente bloqueia; suspeita de segurança segue TL/AppSec.

3. **Consolidar o resultado independente.** Consolidar casos, resultados, evidências e limites da versão. Correção material exige reintegração e revisões TL/AppSec afetadas antes do reteste. Complemento de prova válida volta ao TL; QA integral aprovado segue ao pacote de aceite.

**Pronto:** critérios e integração pertinentes verificados independentemente, com evidência por versão. Feature exige cobertura individual e global.

| Saída | Tipo | Destino |
|---|---|---|
| QA completo aprovado: preparar aceite | Conclusão da atividade | Preparar o aceite humano |
| Complemento de prova concluído: TL | Encaminhamento | Coordenar a entrega |
| Falha ou cobertura obrigatória ausente: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Falha ou cobertura obrigatória ausente: TL**: Candidato, review, AppSec, ambiente ou independência obrigatórios não estão válidos.
- Etapa 2 → **Falha ou cobertura obrigatória ausente: TL**: Falha funcional/integrada, teste obrigatório não executado ou suspeita de segurança necessita tratamento.
- Etapa 3 → **Complemento de prova concluído: TL**: Solicitação era apenas complementar prova existente, verificável e válida, sem nova falha; não declarar QA inteiro concluído.

**Diferenças por cenário:**

- **Cenário 1:** Validar reprodução original, correção, regressões e integração da versão; considerar acesso/dados de outros usuários. Relato não reproduzido não significa ausência de defeito.
- **Cenário 2:** Validar benefício/critério esperado, limites acordados e regressões do comportamento existente na integração real.
- **Cenário 3:** No mesmo candidato completo, validar critérios de cada história e depois jornadas globais, dependências e integração entre serviços. Uma história isolada aprovada não conclui a feature.
