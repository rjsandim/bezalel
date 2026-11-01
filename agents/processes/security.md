<a id="process-security"></a>

# Analisar ou revalidar segurança

**Referência:** `security`. **Responsável:** Especialista em Segurança de Aplicações (AppSec).

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Um procedimento para consulta antecipada, análise da entrega e revalidação afetada. O tipo de entrada define o alcance; consulta não aprova a entrega.

1. **Definir objeto e cobertura.** Iniciar security-audit no alcance atribuído: consulta, análise da entrega ou revalidação. Fixar escopo/versão, independência e modelo de ameaças; análise da entrega requer integração e revisão TL. Aplicar checklist e referências pertinentes, distinguindo cobertura, não aplicável justificado e não verificado.

2. **Examinar e validar hipóteses.** Aplicar security-audit à inspeção e validação adversarial das hipóteses dentro do isolamento/autorização. Não devolver suspeita que o próprio AppSec ainda pode verificar. Recurso/decisão externa, crítico/alto confirmado ou lacuna material interrompem a parte afetada. Registrar prova sanitizada, confiança e severidade apenas do confirmado, conforme R8.

3. **Concluir parecer ou tratamento.** Concluir o parecer de security-audit, com provas de falsos positivos e limites. Escolher um destino: crítico/alto, lacuna material ou impedimento → TL; médio/baixo confirmado, cobertura suficiente e proposta completa/elegível de adiamento → humano, mantendo QA bloqueado. Sem proposta pendente, ou se recusada/inválida, correção → TL. Decisão válida cobre somente risco/versão/condições identificados. Entrega segue a QA só com cobertura/tratamento resolvidos; consulta/complemento retorna ao TL. Revalidar apenas impacto, reutilizando provas válidas.

**Pronto:** parecer versionado com cobertura suficiente e tratamento de todos os achados. Mesmo candidato sem mudança material reutiliza parecer; mudança relevante ou dúvida exige AppSec.

| Saída | Tipo | Destino |
|---|---|---|
| Parecer da entrega válido: QA | Conclusão da atividade | Validar critérios e jornadas |
| Consulta ou complemento concluído: TL | Encaminhamento | Coordenar a entrega |
| Proposta de adiar risco médio/baixo: humano | Encaminhamento | Decidir adiamento de risco |
| Achado bloqueante ou dependência externa: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Achado bloqueante ou dependência externa: TL**: Pré-condição material da análise está ausente ou falta independência/condição de execução.
- Etapa 2 → **Achado bloqueante ou dependência externa: TL**: Prova requer recurso/decisão externa, há crítico/alto confirmado ou lacuna material; suspeita investigável internamente permanece com AppSec.
- Etapa 3 → **Proposta de adiar risco médio/baixo: humano**: A única pendência é decisão humana sobre proposta completa e elegível de adiar achado médio/baixo confirmado, com cobertura suficiente e sem outro impedimento bloqueante. Usar somente esta rota, mantendo QA bloqueado enquanto a decisão estiver pendente.
- Etapa 3 → **Consulta ou complemento concluído: TL**: Entrada é consulta/complemento e a pergunta foi respondida sem novo impedimento; a resposta não substitui o parecer completo.
- Etapa 3 → **Achado bloqueante ou dependência externa: TL**: Achado confirmado exige correção e não há proposta completa e elegível de adiamento aguardando decisão humana; inclui proposta recusada ou decisão inválida. Crítico/alto confirmado, lacuna material ou outro impedimento bloqueante seguem ao TL e não usam a rota de adiamento.

**Diferenças por cenário:**

- **Cenário 1:** Examinar causa, correção e regressões de segurança no fluxo atingido.
- **Cenário 2:** Examinar entradas/API, permissões, dados e dependências alteradas; tamanho não define risco.
- **Cenário 3:** Analisar histórias/jornadas integradas, ativos, perfis e fronteiras de confiança; parecer de parte isolada não aprova o conjunto.
