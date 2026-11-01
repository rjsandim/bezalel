<a id="process-plan"></a>

# Coordenar a entrega

**Referência:** `plan`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Planejamento, atribuição e retomada do cenário ativo.

1. **Confirmar contexto e o que falta.** Ler requisitos, decisões e provas da mesma issue. Delimitar investigação/ambiente, selecionar os especialistas necessários e um dev pela integração inteira. Após investigar, confirmar menor correção segura (bug), impacto limitado (melhoria) ou plano e dependências do conjunto (feature). Investigação pertence aos devs; TL coordena e confere, sem executar testes.

2. **Definir o próximo resultado e suas condições.** Para a atividade pendente, registrar fase, dono, entrada, evidência e dependências. Aplicar verification-planning quando não trivial; clean-architecture apenas para fronteiras/dependências afetadas. Classificar estrutura, migrations e complexidade de relações; seguir R6 e justificar dispensa de banco. Dados simples exigem plano autorizado/versionado de seleção, filtros/volume, validação, repetição e recuperação. Resolver dúvida técnica com prova do dono; dúvida material persistente ou de regra/escopo/autorização vai a PM/humano. Trabalho independente de banco pendente exige justificativa, tarefas/donos e retomada verificáveis; dúvida bloqueia dependentes.

3. **Encaminhar ou retomar pela condição comprovada.** Encaminhar somente a atividade necessária, respeitando R6–R8 e a ordem integração completa → revisão → AppSec → QA → pacote → PR → aceite → conferência de merge → encerramento. Retomar o ponto pendente com provas ainda válidas; complemento não conclui atividade nem libera gate. Mudança de código/composição exige os controles afetados. Residual de segurança segue AppSec/tratamento; residual de produto fica vinculado sem ampliar escopo. Pendência mantém dono/retomada, sem ciclo automático.

**Pronto:** próximo resultado, responsável, versão e pré-condições identificados; todas as condições do destino satisfeitas. Conclusão de tarefa não aprova a entrega inteira.

| Saída | Tipo | Destino |
|---|---|---|
| Ambiente: preparar ou recuperar | Encaminhamento | Preparar, recuperar ou encerrar o ambiente |
| Tarefa ao dev fullstack | Encaminhamento | Executar contribuição fullstack |
| Tarefa ao dev backend | Encaminhamento | Executar contribuição backend |
| Tarefa ao dev web | Encaminhamento | Executar contribuição web |
| Tarefa ao dev mobile | Encaminhamento | Executar contribuição mobile |
| Mock completo: revisar UI/UX | Encaminhamento | Revisar interface e contrato |
| Banco: preparar ou revisar proposta | Encaminhamento | Preparar a proposta de banco |
| Contexto ou decisão: PM | Encaminhamento | PM do cenário ativo |
| Conjunto integrado: revisão de código | Conclusão da atividade | Revisar a entrega integrada |
| Consulta ou revalidação AppSec | Encaminhamento | Analisar ou revalidar segurança |
| QA: retomar ou completar prova | Encaminhamento | Validar critérios e jornadas |
| QA válido: preparar aceite | Encaminhamento | Preparar o aceite humano |
| Pacote válido: abrir ou retomar PR | Encaminhamento | Abrir PRs e entregar próximos passos |
| Pendência atribuída; aguardar | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Contexto ou decisão: PM**: Falta decisão de produto/autorização, houve mudança de escopo ou decisão humana integral de adiar/descartar.
- Etapa 2 → **Contexto ou decisão: PM**: Dúvida material persiste após prova técnica ou depende de regra/escopo/autorização; apresentar pergunta concreta ao PM/humano.
- Etapa 3 → **Pendência atribuída; aguardar**: A pendência está atribuída e não existe novo encaminhamento a fazer; registrar dono e condição de retomada.

**Diferenças por cenário:**

- **Cenário 1:** Consolidar diagnóstico já realizado; delimitar menor correção segura. Separar residual sem dispensar segurança.
- **Cenário 2:** Confirmar escopo pequeno após investigação. Se necessário, propor transferência humana à feature.
- **Cenário 3:** Exigir recebimento da vN aprovada; planejar todas as histórias/dependências e um integrador do conjunto.
