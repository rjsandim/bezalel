<a id="process-ui"></a>

# Revisar interface e contrato

**Referência:** `ui`. **Responsável:** Engenheiro de QA.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Revisão independente de UI/UX sobre telas e mock, antes da API definitiva afetada. É distinta do QA funcional sobre a integração real.

1. **Conferir a demonstração.** Receber telas/estados, contrato e mock de todas as interfaces selecionadas, com investigação válida. Conferir ambiente, objetivo e executor distinto dos autores; definir jornadas e observáveis aproveitando o plano de evidências pertinente.

2. **Exercitar as jornadas previstas.** Exercitar jornadas com agent-browser quando web e disponível, complementando os testes próprios de acessibilidade/plataforma. Conferir usabilidade, estados vazios/erro, autorização, dados e chamadas; exigir respostas coesas por tela e justificar separações por paginação, tamanho, cache, autorização, atualização ou falhas parciais, sem endpoint universal. Mock não comprova persistência, desempenho ou integração real.

3. **Devolver parecer e impacto.** Entregar parecer versionado e impacto em campos/relações/contratos. TL reconfere banco antes da API definitiva, inclusive após aprovação antecipada. Ajustes voltam aos autores via TL; reteste cobre correção e impactos.

**Pronto:** cobertura pertinente de todas as interfaces selecionadas, com evidência independente; não libera integração final.

| Saída | Tipo | Destino |
|---|---|---|
| Parecer UI/UX registrado: TL | Conclusão da atividade | Coordenar a entrega |
| Pré-condição ausente ou UI/UX reprovada: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Pré-condição ausente ou UI/UX reprovada: TL**: Mock/contribuição obrigatória está ausente ou falta independência/condição de execução.
- Etapa 2 → **Pré-condição ausente ou UI/UX reprovada: TL**: Problema de UI/UX/contrato exige ajuste ou decisão antes da API definitiva.
