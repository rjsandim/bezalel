<a id="process-review"></a>

# Revisar a entrega integrada

**Referência:** `review`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Uma revisão reúne completude da integração, versão e código. Elimina conferências separadas que inspecionavam o mesmo candidato.

1. **Conferir o candidato completo.** Iniciar um único pr-audit sobre o candidato completo do dev integrador, mesmo antes de existir PR. Conferir contribuições/histórias e decisões de investigação, UI/UX e banco. Parte pendente impede revisão final; TL não integra branches nem executa testes.

2. **Revisar código e contratos.** Aplicar pr-audit à conferência de alegações, diff, contratos, integração e provas. Usar clean-code e, havendo impacto arquitetural, clean-architecture, em modo sem edição, somente para aprofundar o mesmo parecer. Reutilizar provas válidas; solicitar testes/correções aos executores.

3. **Entregar conclusão identificada.** Concluir o mesmo pr-audit com versão, cobertura, achados e restrições. Candidato completo sem impedimento na revisão segue ao AppSec; correção ou prova faltante volta à coordenação com dono e retomada. Parecer técnico não é aceite humano nem autorização de merge.

**Pronto:** conjunto completo identificado e revisão aprovada; testes próprios não substituem QA independente.

| Saída | Tipo | Destino |
|---|---|---|
| Candidato revisado: AppSec | Conclusão da atividade | Analisar ou revalidar segurança |
| Entrega incompleta ou revisão reprovada: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Entrega incompleta ou revisão reprovada: TL**: Falta contribuição, pré-condição ou prova obrigatória, ou composição/base divergem.
- Etapa 2 → **Entrega incompleta ou revisão reprovada: TL**: Revisão encontrou defeito, incompatibilidade ou cobertura obrigatória insuficiente.
