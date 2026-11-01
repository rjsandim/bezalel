<a id="process-package"></a>

# Preparar o aceite humano

**Referência:** `package`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Pacote único de evidências e roteiro manual para o candidato validado. Nos cenários 2/3, roteiro Excel .xlsx real e acessível; no bug, roteiro proporcional.

1. **Conferir evidências do conjunto.** Conferir escopo, integração, AppSec, QA e decisões da mesma versão. Reutilizar provas válidas; lacuna ou mudança material retorna ao responsável via coordenação.

2. **Preparar roteiro e acesso.** Aplicar development-test-workbook para produzir e conferir o .xlsx real/acessível dos cenários 2/3; no bug, usar quando o roteiro proporcional for Excel. Sem Excel, manter versão, ambiente, pré-condições/dados, critérios, passos, esperado e observado/status, executor/data e evidências. Casos humanos permanecem não executados, sem herdar QA. Preparar acesso autorizado sem segredos.

3. **Apresentar o pacote.** Apresentar pacote, links, instruções, limites e decisões pendentes; humanizer pode revisar apenas a apresentação. Encaminhar a abertura da PR com roteiro pronto para o humano executar e avaliar. Falha de acesso/apresentação mantém pendência.

**Pronto:** QA integral válido e pacote realmente acessível, com casos humanos ainda não executados.

| Saída | Tipo | Destino |
|---|---|---|
| Roteiro e candidato preparados: PR | Conclusão da atividade | Abrir PRs e entregar próximos passos |
| Versão, prova ou acesso insuficiente: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Versão, prova ou acesso insuficiente: TL**: Há alteração material, evidência obrigatória ausente ou resultado invalidado.
- Etapa 2 → **Versão, prova ou acesso insuficiente: TL**: Roteiro/acesso/ambiente obrigatório não pôde ser preparado ou verificado.

**Diferenças por cenário:**

- **Cenário 1:** Roteiro manual proporcional ao bug, com reprodução, resultado esperado e regressões relevantes.
- **Cenário 2:** Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.
- **Cenário 3:** Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.
