<a id="process-risk"></a>

# Decidir adiamento de risco

**Referência:** `risk`. **Responsável:** APROVADOR HUMANO.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Decisão restrita a achados de segurança confirmados médios/baixos. Não equivale a adiar a intenção inteira ou aceitar o funcionamento.

1. **Ler a proposta de AppSec.** Conferir evidência, severidade, impacto, versão, alternativas, responsável e prazo/condição de tratamento. Crítico/alto ou cobertura material ausente exigem bloqueio/correção, não este adiamento.

2. **Decidir o tratamento.** Aceitar o adiamento delimitado ou solicitar correção/esclarecimento. Registrar interação real e objeto. Decisão ausente mantém pendência.

3. **Devolver o resultado pertinente.** Adiamento válido retorna ao AppSec para consolidar parecer; recusa ou proposta inelegível retorna ao TL para correção/replanejamento. Não tratar adiamento de risco como cancelamento integral. Preservar o tipo de entrada original do AppSec: consulta antecipada retorna ao TL e não libera QA; análise da entrega só libera após todas as condições.

**Pronto:** decisão verificável e delimitada sobre risco elegível.

| Saída | Tipo | Destino |
|---|---|---|
| Adiamento registrado: consolidar parecer | Conclusão da atividade | Analisar ou revalidar segurança |
| Corrigir ou rever tratamento: TL | Encaminhamento | Coordenar a entrega |
| Aguardando decisão ou esclarecimento | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Corrigir ou rever tratamento: TL**: Proposta inclui crítico/alto, lacuna material ou outro risco inelegível para adiamento.
- Etapa 2 → **Aguardando decisão ou esclarecimento**: Resposta ausente ou ambígua.
- Etapa 3 → **Corrigir ou rever tratamento: TL**: Humano não aceita o adiamento e solicita correção/revisão.
