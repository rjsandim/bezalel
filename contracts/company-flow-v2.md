# Company Flow v2 para bug melhoria e feature

Fonte canônica dos três cenários vigentes. São 20 processos reutilizáveis e 60
etapas, com 18 processos em cada cenário; os quatro devs são opções de especialidade.
Os contratos em [agents](README.md) distribuem os processos por responsabilidade,
sem criar um agente por etapa. O aprovador humano é externo.

## Regras comuns

No Company Flow, estas regras ficam uma única vez na descrição de **Coordenar a entrega · v2**, reutilizada pelos três cenários. Cada atividade usa as pré-condições do destino, inclusive nas retomadas. Condições locais complementam, sem substituir, o procedimento e estas regras.

### R1 Registro e autorização

Usar a mesma issue como registro da intenção, escopo, decisões e evidências; anexos ficam vinculados. Registrar o mínimo antes de qualquer destino. Efeitos externos dependem da autorização concreta da tarefa, aproveitando a já concedida. Ausência de acesso/autorização mantém pendência e rascunho verificável. O mapa documenta responsabilidades; não executa ferramentas, autentica pessoas ou concede permissão.

### R2 Responsabilidade e evidência

TL planeja, coordena e revisa código/evidências; nunca implementa, compõe branches de implementação ou executa testes. Escolhe somente os especialistas necessários e um dev responsável pela integração inteira. Devs executam investigação, preparação, implementação e testes próprios; DevOps cuida do isolamento; QA e AppSec verificam independentemente dos autores. Evidência identifica escopo e candidato: repositórios, base/head, componentes/builds, contratos, dados/schema, dependências e configuração pertinentes.

### R3 Passagem entre atividades

Cada tarefa informa objetivo/fase, responsável, entrada/versão, entrega esperada e condição de conclusão. Fases dos devs: investigar, preparar interface/mock ou implementar/corrigir. Concluir uma tarefa ou complementar prova não aprova a entrega inteira. Selecionar somente os destinos necessários; saídas não disparam todos os participantes. Provas válidas são reutilizadas; só mudança com impacto exige refazer a cobertura afetada.

### R4 Interrupção e retomada

Interromper a parte afetada assim que faltar condição ou surgir reprovação/decisão necessária, antes de efeitos dependentes. Registrar na issue motivo, prova/lacuna, versão, dono e ponto/condição de retomada; falha de gravação preserva rascunho e erro. Problema novo vai ao TL; pendência já atribuída permanece no processo atual. Correção ordinária dentro da tarefa autorizada fica com o executor. Espera não é conclusão; silêncio não decide. Condições locais destacam desvios relevantes, sem copiar esta regra em toda etapa.

### R5 Investigação e preparação

Investigação dos devs é obrigatória antes de implementar, proporcional ao impacto; diagnóstico válido do bug já a satisfaz. Experimentos não entram automaticamente na entrega. Antes da investigação executável, DevOps comprova isolamento de arquivos, banco, filas, portas e storage; não aplicável exige motivo concreto. Reutilizar ambiente válido sem recriá-lo. Produção não é ambiente de teste. Ferramenta ou recurso obrigatório indisponível é bloqueio, não dispensa.

### R6 Interface e banco

Com interface afetada: telas/contrato → mock exercitável → QA de UI/UX, antes da API definitiva afetada. Sem interface, justificar. TL escolhe banco antecipado quando campos/relações estão estáveis, ou interface primeiro; aprovação antecipada retorna à interface pendente. Após UI/UX, reconferir banco. Estrutura, qualquer migration e transformação complexa de relações por dados exigem proposta e decisão humana exata anteriores à implementação correspondente. Trabalho independente pode avançar com condições próprias e independência demonstrada pelo TL; pendência bloqueia as partes dependentes e a conclusão do conjunto.

### R7 Revisões proporcionais

Entrega implementada exige integração completa, revisão TL, AppSec, QA independente e aceite humano, na mesma versão. TL define verificações por impacto; devs executam as próprias e QA confronta/amplia a cobertura. Técnica não pertinente aceita justificativa; teste obrigatório falho/não executado bloqueia. QA da feature cobre histórias e jornadas globais no mesmo processo. Nenhuma contribuição parcial libera a revisão final do conjunto.

### R8 Segurança

AppSec distingue hipótese, confirmação, severidade, confiança e cobertura. Valida hipóteses dentro do isolamento e autorização disponíveis antes de devolver; dependência externa/decisão pode interromper antes. Crítico/alto confirmado ou lacuna material bloqueia. Médio/baixo confirmado exige correção ou adiamento humano explícito com motivo, dono e prazo/condição. Falso positivo exige prova. Nova questão de segurança vai ao AppSec via TL; issue residual não dispensa tratamento. Evidências são sanitizadas; segredos/dados privados não entram em issue ou PR.

### R9 Decisões e destinos

Decisão humana registra interação real, identidade, fonte, data/fuso e conteúdo/versão. Reaproveitar decisão que já cubra o objeto; ambiguidade exige esclarecimento. Rejeitar solução não cancela a intenção. PM trata revisão parcial, adiamento integral, descarte, reabertura e transferência na entrada do cenário: adiar mantém issue aberta com dono/retomada; descartar fecha e verifica somente itens abrangidos/exclusivos; reabrir requer orientação humana. Transferência exige destino iniciado/verificado na mesma issue antes de encerrar origem; v2 usa v2 do destino. Estados sem implementação dispensam PR/scan fictícios.

### R10 Entrega e validade final

Aceite refere-se ao candidato e roteiro realmente executados pelo humano. Antes da PR e até entregar as orientações, TL compara candidato e evidências: sem mudança material, reutiliza os pareceres; diferença material retorna à atividade responsável, inclusive AppSec quando houver impacto ou dúvida de segurança. Abrir/verificar todas as PRs para a branch de produção indicada pelo projeto e entregar links/validações/pendências/próximos passos. Checks prévios obrigatórios passam antes da abertura. CI acionado somente pela abertura é informado no estado observado, inclusive pendente/falho; sem espera/correção automática posterior. Rafael conduz manualmente merge, deploy e ações de produção.

## Seleção de skills nas etapas

As etapas indicam objetivo, responsável, condição e entrega; o método fica na skill indicada, em skills/<nome>/SKILL.md do Bezalel, com suas referências. Aplicar somente o modo/fase pertinente. Uma aplicação pode atender várias etapas do mesmo trabalho: não reiniciar auditoria, plano ou redação a cada passagem; reutilizar artefatos/provas ainda válidos. Apoios condicionais só entram quando úteis. Skill não cria agente, gate, autorização ou transferência de responsabilidade. Se indisponível, registrar o limite e usar procedimento equivalente disponível; prova/ferramenta obrigatória ausente segue R4.
iss-audit: qualificação PM ou investigação dev, conforme fase. pr-audit: revisão TL sem editar/testar. clean-code inclui simplificação; clean-architecture aplica-se a fronteiras afetadas. implementar-snapshots só para construir/corrigir a funcionalidade. verification-planning orienta provas proporcionais; TL planeja/confere e executores produzem evidência. Pesquisa dependente de @librarian indisponível fica registrada, sem inventar agente ou conclusão; infraestrutura de verificação depende da autorização própria.
agent-browser exige CLI/guia da versão e alvo isolado autorizado; não instalar por inferência. MCP continua preferido para operações do serviço. Browser apoia a prova da interface, sem substituir regressão automatizada, acessibilidade completa, serviços/persistência ou mobile nativo. humanizer é opcional na redação antes da submissão/publicação; não muda fatos, critérios, respostas, resultados ou decisões versionadas.
security-audit fica em auditoria/validação: correção de produto volta a TL/dev; não ampliar credenciais, remover GITHUB_TOKEN, alterar/encerrar alertas ou cancelar CI por esta indicação. Cópias originais permanecem intactas; pr-audit e iss-audit usam variantes autorizadas. Skills reservadas ao uso manual e candidatas pendentes no inventário ficam fora das etapas; nenhuma é disparada ao concluir PR/auditoria.

O [inventário completo](company-flow-skills-inventario.md) registra origem, cópias e adaptações pendentes. A [relação por processo e etapa](company-flow-v2-skills.md) facilita consultar a seleção. As adaptações autorizadas de pr-audit e iss-audit estão identificadas; as demais cópias preservam o conteúdo original. Os agentes referenciam essas skills sem duplicar seus procedimentos.

## Percursos dos cenários

### 1 Bug v2 investigar e entregar a correção

**Entrada:** Relato de possível defeito ou retomada humana, com esperado/observado/evidências a esclarecer.

Foco: separar hipótese, comportamento esperado e defeito; investigar antes de definir a menor correção segura. Diagnóstico suficiente é a investigação obrigatória. Residual de produto fica vinculado; suspeita/achado de segurança precisa de tratamento. Humano decide regra, comportamento esperado e reclassificação. Transferências permitidas: 2 v2 ou 3 v2, iniciadas/verificadas pelo PM na mesma issue.

**Percurso:** PM qualifica a intenção e resolve decisões de produto necessárias → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → humano executa/aceita → TL confere, abre/verifica PRs e entrega próximos passos.

**QA específico:** Validar reprodução original, correção, regressões e integração da versão; considerar acesso/dados de outros usuários. Relato não reproduzido não significa ausência de defeito.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão validada e aceita, com orientação manual entregue a Rafael. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

### 2 Melhoria v2 delimitar e validar a mudança

**Entrada:** Melhoria de comportamento existente ou transferência humana do bug; benefício e limite a confirmar.

Foco: resultado observável e escopo pequeno, confirmado pelo TL após investigação de comportamento, contratos e dependências. Mudança de regra/escopo precisa de decisão humana; aproveitar o pedido já claro. Se a investigação revelar trabalho de feature, humano decide transferência a 3 v2 e PM inicia/verifica o destino na mesma issue. Roteiro de aceite em Excel .xlsx real.

**Percurso:** PM qualifica a intenção e resolve decisões de produto necessárias → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → humano executa/aceita → TL confere, abre/verifica PRs e entrega próximos passos.

**QA específico:** Validar benefício/critério esperado, limites acordados e regressões do comportamento existente na integração real.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão validada e aceita, com orientação manual entregue a Rafael. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

### 3 Feature v2 aprovar e entregar o conjunto

**Entrada:** Capacidade nova ou mudança grande, inclusive transferência humana de bug/melhoria; exige visão, histórias e critérios globais.

Foco: principal e histórias curtas vinculadas, critérios individuais/globais, dependências e um dev integrador. Humano aprova o escopo vN; PM confere e entrega a mesma versão ao TL antes da investigação/planejamento técnico. Investigar viabilidade obrigatoriamente e confirmar plano do conjunto. Uma única atividade de QA verifica histórias e depois jornadas globais na feature completa. Roteiro de aceite em Excel .xlsx real.

**Percurso:** PM registra principal/histórias → humano decide vN → PM entrega ao TL → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → humano executa/aceita → TL confere, abre/verifica PRs e entrega próximos passos.

**QA específico:** No mesmo candidato completo, validar critérios de cada história e depois jornadas globais, dependências e integração entre serviços. Uma história isolada aprovada não conclui a feature.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão validada e aceita, com orientação manual entregue a Rafael. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

## Procedimentos dos responsáveis

Os identificadores curtos abaixo organizam a correspondência documental; não são um runtime. As entradas de retorno recebem contexto, fase/objeto, versão e origem. Cada processo tem uma entrada de retorno; os três processos PM também têm entrada inicial. As saídas abaixo são exclusivas/selecionadas conforme a condição, exceto tarefas independentes explicitamente atribuídas a mais de um dev.

<a id="process-bug"></a>

### Qualificar e conduzir o bug

**Referência:** `bug`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 1 v2: relato, decisões de produto e destinos sem correção. Referência: regras comuns no processo Coordenar a entrega · v2.

1. **Garantir a issue mínima.** Localizar/criar e verificar a mesma issue, com relato e fonte. Decisão integral de adiamento/descarte segue diretamente ao destino; retomada reabre/verifica o objeto autorizado.

2. **Definir a necessidade.** Aplicar iss-audit no modo PM para qualificar necessidade, esperado/observado, impacto, perfis/dados, hipóteses e critérios. Não exigir causa comprovada para investigar. Dúvida de regra, esperado ou reclassificação exige decisão humana. Usar humanizer somente se a redação precisar de revisão.

3. **Entregar contexto ou registrar destino.** Aplicar R9 na mesma issue. Revisão parcial preserva a intenção restante e confere a decisão sobre o conteúdo atualizado; decisão integral não exige detalhamento/investigação. Descarte/adiamento/reabertura têm estados reais verificados; falha permanece no PM. Transferência humana a 2 v2 ou 3 v2 exige destino iniciado/verificado, mesmo se adiado. Encerrar como comportamento esperado só com confirmação humana, justificativa e fechamento verificado, registrando ausência de correção. Caso qualificado segue ao TL.

**Pronto:** issue real e contexto suficiente para investigação; ou destino próprio decidido e verificado. Não exige comprovar a causa para iniciar.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo · v2 |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Transferência verificada para 2 v2 ou 3 v2 | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Falha de registro/reabertura/verificação: preservar rascunho e atribuir retomada ao PM.
- Etapa 2 → **Decisão de produto necessária**: Regra, escopo, comportamento esperado ou reclassificação precisam de decisão humana.
- Etapa 3 → **Intenção adiada e registrada**: Decisão integral de adiar registrada; issue aberta verificada, dono e retomada definidos.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte ou comportamento esperado possuem decisão humana e fechamento verificado.
- Etapa 3 → **Transferência verificada para 2 v2 ou 3 v2**: Destino 2 v2 ou 3 v2 iniciado e verificado com a mesma issue.

<a id="process-improvement"></a>

### Qualificar e conduzir a melhoria

**Referência:** `improvement`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 2 v2: melhoria do comportamento existente com benefício e limite claros.

1. **Garantir a issue mínima.** Localizar/criar e verificar a mesma issue, inclusive em transferência; registrar intenção, fonte e decisão existente. Retomada, adiamento e descarte seguem R9.

2. **Definir resultado e limites.** Aplicar iss-audit no modo PM para definir benefício, comportamento atual/desejado, critérios, exclusões e dependências, usuários/perfis, dados e integrações pertinentes. Encaminhar dúvidas de segurança. TL confirma o impacto limitado após investigar; mudança de regra/escopo exige humano, aproveitando pedido já inequívoco. humanizer é opcional para revisar a redação.

3. **Entregar contexto ou registrar destino.** Aplicar R9 na mesma issue. Revisão parcial preserva a intenção restante e confere a decisão sobre o conteúdo atualizado; decisão integral dispensa detalhamento/investigação. Verificar estados reais de descarte/adiamento/reabertura; falha permanece no PM. Transferência humana a 3 v2 exige destino iniciado/verificado, mesmo se adiado. Entregar ao TL a versão correspondente dos requisitos e decisões.

**Pronto:** benefício e critérios suficientes para investigar, com escopo autorizado; ou destino próprio verificado.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo · v2 |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Transferência verificada para 3 v2 | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Registro, retomada ou verificação da issue falhou; pendência atribuída ao PM.
- Etapa 2 → **Decisão de produto necessária**: Falta decisão de regra/escopo ou o reenquadramento para feature requer decisão humana.
- Etapa 3 → **Intenção adiada e registrada**: Adiamento integral registrado, com issue aberta e retomada.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte integral decidido e fechamento dos itens abrangidos verificado.
- Etapa 3 → **Transferência verificada para 3 v2**: Cenário 3 v2 iniciado e verificado com a mesma issue.

<a id="process-feature"></a>

### Definir e conduzir o escopo da feature

**Referência:** `feature`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 3 v2: visão e histórias aprovadas como conjunto, com um responsável pela integração.

1. **Registrar visão e histórias.** Garantir issue principal mínima. Aplicar iss-audit no modo PM para qualificar visão, necessidades, limites, perfis/dados/integrações e questões de segurança. Vincular histórias curtas com critérios individuais, dependências e exclusões; a principal reúne critérios globais. humanizer pode revisar a redação antes de submeter a versão.

2. **Submeter ou conferir a versão do escopo.** Registrar visão/limites/prioridades e histórias em comentários vN na principal e em cada história, preservando o conteúdo submetido. Obter decisão humana sobre esse conjunto antes do planejamento técnico. Mudança material cria vN+1 e confere decisão correspondente; aproveitar resposta já explícita que cubra a mudança/resultante.

3. **Entregar a mesma versão ou registrar destino.** Aplicar R9 na mesma issue: revisão parcial preserva a intenção restante e confere a decisão atual; destino integral dispensa detalhamento/investigação. Descarte abrange somente itens exclusivos autorizados; reabertura inclui somente histórias descartadas retomadas pelo humano. Verificar estados reais e manter falha pendente no PM. TL confirma recebimento da vN aprovada; divergência volta ao PM, e falta de acesso não é revisão fictícia de escopo.

**Pronto:** principal e histórias vinculadas, escopo vN com decisão correspondente e entrega ao TL; ou destino próprio verificado.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo · v2 |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Não foi possível registrar ou verificar a principal/histórias necessárias; preservar pendência PM.
- Etapa 2 → **Decisão de produto necessária**: Escopo vN ainda não possui decisão humana que cubra seu conteúdo exato.
- Etapa 3 → **Intenção adiada e registrada**: Adiamento integral registrado e estados abertos/retomada verificados.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte decidido; principal e histórias exclusivas abrangidas fechadas/verificadas.

<a id="process-product"></a>

### Decidir regra ou escopo

**Referência:** `product`. **Responsável:** APROVADOR HUMANO.

Decisão externa de produto: regra, escopo da feature, alteração, reenquadramento ou destino. PM apresenta a pergunta e alternativas.

1. **Conferir o objeto.** Ler a issue, versão, evidências e alternativas; verificar o que precisa de decisão. Na feature, considerar principal e histórias do conjunto.

2. **Decidir sobre o conteúdo identificado.** Aprovar, revisar/rejeitar a solução, esclarecer regra, reclassificar ou decidir adiamento/descarte parcial/integral. Resposta existente inequívoca é aproveitada. Ausência/ambiguidade permanece pendente; não inferir aprovação.

3. **Devolver a decisão ao PM.** Registrar a interação real e objeto conforme R9. PM atualiza a mesma issue, confere o resultado/versão e dá o destino pertinente.

**Pronto:** decisão humana verificável e de alcance definido. Não aprova banco, risco de segurança ou aceite funcional por consequência.

| Saída | Tipo | Destino |
|---|---|---|
| Decisão registrada: PM | Conclusão da atividade | PM do cenário ativo |
| Aguardando decisão ou esclarecimento | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 2 → **Aguardando decisão ou esclarecimento**: Não há resposta inequívoca que cubra o objeto apresentado.

<a id="process-plan"></a>

### Coordenar a entrega

**Referência:** `plan`. **Responsável:** Tech Lead.

Planejamento, atribuição e retomada do cenário ativo. Regras transversais na seção Regras comuns.

1. **Confirmar contexto e o que falta.** Ler requisitos, decisões e provas da mesma issue. Delimitar investigação/ambiente, selecionar os especialistas necessários e um dev pela integração inteira. Após investigar, confirmar menor correção segura (bug), impacto limitado (melhoria) ou plano e dependências do conjunto (feature). Investigação pertence aos devs; TL coordena e confere, sem executar testes.

2. **Definir o próximo resultado e suas condições.** Para a atividade pendente, registrar fase, dono, entrada, evidência e dependências. Aplicar verification-planning quando não trivial; clean-architecture apenas para fronteiras/dependências afetadas. Classificar estrutura, migrations e complexidade de relações; seguir R6 e justificar dispensa de banco. Dados simples exigem plano autorizado/versionado de seleção, filtros/volume, validação, repetição e recuperação. Resolver dúvida técnica com prova do dono; dúvida material persistente ou de regra/escopo/autorização vai a PM/humano. Trabalho independente de banco pendente exige justificativa, tarefas/donos e retomada verificáveis; dúvida bloqueia dependentes.

3. **Encaminhar ou retomar pela condição comprovada.** Encaminhar somente a atividade necessária, respeitando R6–R8 e a ordem integração completa → revisão → AppSec → QA → pacote → aceite → PR. Retomar o ponto pendente com provas ainda válidas; complemento não conclui atividade nem libera gate. Mudança de código/composição exige os controles afetados. Residual de segurança segue AppSec/tratamento; residual de produto fica vinculado sem ampliar escopo. Pendência mantém dono/retomada, sem ciclo automático.

**Pronto:** próximo resultado, responsável, versão e pré-condições identificados; todas as condições do destino satisfeitas. Conclusão de tarefa não aprova a entrega inteira. Aplicam-se as regras comuns R1–R10 da descrição.

| Saída | Tipo | Destino |
|---|---|---|
| Ambiente: preparar ou recuperar | Encaminhamento | Preparar ou recuperar o ambiente · v2 |
| Tarefa ao dev fullstack | Encaminhamento | Executar contribuição fullstack · v2 |
| Tarefa ao dev backend | Encaminhamento | Executar contribuição backend · v2 |
| Tarefa ao dev web | Encaminhamento | Executar contribuição web · v2 |
| Tarefa ao dev mobile | Encaminhamento | Executar contribuição mobile · v2 |
| Mock completo: revisar UI/UX | Encaminhamento | Revisar interface e contrato · v2 |
| Banco: preparar ou revisar proposta | Encaminhamento | Preparar a proposta de banco · v2 |
| Contexto ou decisão: PM | Encaminhamento | PM do cenário ativo |
| Conjunto integrado: revisão de código | Conclusão da atividade | Revisar a entrega integrada · v2 |
| Consulta ou revalidação AppSec | Encaminhamento | Analisar ou revalidar segurança · v2 |
| QA: retomar ou completar prova | Encaminhamento | Validar critérios e jornadas · v2 |
| QA válido: preparar aceite | Encaminhamento | Preparar o aceite humano · v2 |
| Aceite válido: retomar entrega da PR | Encaminhamento | Abrir PRs e entregar próximos passos · v2 |
| Pendência atribuída; aguardar | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Contexto ou decisão: PM**: Falta decisão de produto/autorização, houve mudança de escopo ou decisão humana integral de adiar/descartar.
- Etapa 2 → **Contexto ou decisão: PM**: Dúvida material persiste após prova técnica ou depende de regra/escopo/autorização; apresentar pergunta concreta ao PM/humano.
- Etapa 3 → **Pendência atribuída; aguardar**: A pendência está atribuída e não existe novo encaminhamento a fazer; registrar dono e condição de retomada.

<a id="process-env"></a>

### Preparar ou recuperar o ambiente

**Referência:** `env`. **Responsável:** Engenheiro DevOps.

Avaliação, preparação e prova de isolamento no mesmo procedimento. Usar a skill ENV carregada e seu contrato de bancos compartilhados; detalhes operacionais pertencem à skill.

1. **Conferir alvos e autorização.** Usar env para conferir projeto, manifesto/base/contexto, recursos e ação solicitada pelo TL: preparar, reutilizar ou recuperar. Delimitar autorização e pré-requisitos; impedimento segue R4.

2. **Preparar e comprovar isolamento.** Aplicar o procedimento de env e, quando houver pools, sua referência de bancos compartilhados. Entregar prova de isolamento de arquivos, banco, filas, portas e storage conforme R5; arquivos sempre comprovados, demais dimensões não aplicáveis somente com motivo. Em pools, comprovar recursos/credenciais próprios, configuração dos consumidores e recusa de acesso cruzado. Preservar dados/configurações; não usar produção nem limpeza como teste.

3. **Entregar provas e ponto de retomada.** Entregar ao TL identificação do ambiente, versões, provas e limitações, sem credenciais. Na recuperação, indicar mudanças e evidências invalidadas; não reiniciar investigação automaticamente.

**Pronto:** isolamento comprovado e finalidade identificada; avaliação documental ou container existente não bastam.

| Saída | Tipo | Destino |
|---|---|---|
| Ambiente/prova entregue: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Impedimento ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Impedimento ou decisão necessária: TL**: Alvo, necessidade ou autorização está indefinido, ou exige decisão/ação externa.
- Etapa 2 → **Impedimento ou decisão necessária: TL**: Preparação ou prova de isolamento falhou ou divergiu; interromper a parte afetada.

<a id="process-fullstack"></a>

### Executar contribuição fullstack

**Referência:** `fullstack`. **Responsável:** Desenvolvedor fullstack.

Abrange as camadas selecionadas. Preparar telas/contrato e próprio mock quando pertinente; integrar front, negócio/persistência e serviços sem presumir que dispensa outro especialista. Um procedimento por especialidade; cada entrada executa somente a fase designada.

1. **Receber a tarefa e conferir pré-condições.** Conferir fase, pergunta/escopo, versão, dependências e entrega esperada. Aplicar R5–R6: investigação com isolamento; interface/mock após investigação; implementação após investigação, UI/UX e aprovações aplicáveis. Falta material ou dúvida de dependência volta ao TL.

2. **Executar a fase atribuída.** Investigar com iss-audit no modo dev: entregar diagnóstico/viabilidade e alternativas, mantendo experimento separado. Preparar interface/mock: entregar estados, contrato e demonstração sintética, sem antecipar banco/migration/API definitiva pendentes. Implementar/corrigir conforme plano e .bezalel/project.json, usando clean-code no código alterado e clean-architecture somente quando afetar responsabilidades, fronteiras ou dependências; executar testes próprios por risco e integrar consumidores reais. Toda operação somente de dados entrega artefato versionado com seleção, validação, repetição e recuperação. Corrigir falha ordinária autorizada; decisão de escopo/contrato/banco ou dependência externa volta ao TL. Preservar view → entrada HTTP/action fina → negócio específico → fachadas de persistência → banco; negócio fora de HTTP/Filament, sem Request/Response/forms. Domain-kernel somente quando definido pelo projeto; sem fachada universal, interface por classe ou refatoração geral. Aplicar implementar-snapshots somente se construir/corrigir essa funcionalidade for a tarefa. agent-browser pode apoiar reprodução e jornadas web, nas condições comuns.

3. **Entregar a contribuição identificada.** Entregar fase, versão, provas e limites ao TL. Na implementação, o dev integrador reúne contribuições/histórias, confere contratos/mock/API real e entrega candidato completo com base/head e testes. Contribuição parcial ou complemento de prova não libera o conjunto nem substitui revisão independente.

**Pronto:** entrega da fase verificável e limites explícitos. Conclusão de investigação/mock não autoriza implementação; TL confirma o próximo passo.

| Saída | Tipo | Destino |
|---|---|---|
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.

<a id="process-backend"></a>

### Executar contribuição backend

**Referência:** `backend`. **Responsável:** Desenvolvedor backend.

Investigar e implementar negócio, contratos, persistência e serviços selecionados. Na preparação, fornecer mock exercitável a web/mobile com contratos e estados combinados; não antecipar API definitiva afetada. Um procedimento por especialidade; cada entrada executa somente a fase designada.

1. **Receber a tarefa e conferir pré-condições.** Conferir fase, pergunta/escopo, versão, dependências e entrega esperada. Aplicar R5–R6: investigação com isolamento; interface/mock após investigação; implementação após investigação, UI/UX e aprovações aplicáveis. Falta material ou dúvida de dependência volta ao TL.

2. **Executar a fase atribuída.** Investigar com iss-audit no modo dev: entregar diagnóstico/viabilidade e alternativas, mantendo experimento separado. Preparar interface/mock: entregar estados, contrato e demonstração sintética, sem antecipar banco/migration/API definitiva pendentes. Implementar/corrigir conforme plano e .bezalel/project.json, usando clean-code no código alterado e clean-architecture somente quando afetar responsabilidades, fronteiras ou dependências; executar testes próprios por risco e integrar consumidores reais. Toda operação somente de dados entrega artefato versionado com seleção, validação, repetição e recuperação. Corrigir falha ordinária autorizada; decisão de escopo/contrato/banco ou dependência externa volta ao TL. Preservar view → entrada HTTP/action fina → negócio específico → fachadas de persistência → banco; negócio fora de HTTP/Filament, sem Request/Response/forms. Domain-kernel somente quando definido pelo projeto; sem fachada universal, interface por classe ou refatoração geral. Aplicar implementar-snapshots somente se construir/corrigir essa funcionalidade for a tarefa.

3. **Entregar a contribuição identificada.** Entregar fase, versão, provas e limites ao TL. Na implementação, o dev integrador reúne contribuições/histórias, confere contratos/mock/API real e entrega candidato completo com base/head e testes. Contribuição parcial ou complemento de prova não libera o conjunto nem substitui revisão independente.

**Pronto:** entrega da fase verificável e limites explícitos. Conclusão de investigação/mock não autoriza implementação; TL confirma o próximo passo.

| Saída | Tipo | Destino |
|---|---|---|
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.

<a id="process-web"></a>

### Executar contribuição web

**Referência:** `web`. **Responsável:** Desenvolvedor frontend web.

Preparar telas/estados/contratos web e exercitá-los com mock fornecido pelo backend, ou mock próprio explicitamente atribuído pelo TL. Implementar/validar a integração web na fase autorizada. Um procedimento por especialidade; cada entrada executa somente a fase designada.

1. **Receber a tarefa e conferir pré-condições.** Conferir fase, pergunta/escopo, versão, dependências e entrega esperada. Aplicar R5–R6: investigação com isolamento; interface/mock após investigação; implementação após investigação, UI/UX e aprovações aplicáveis. Falta material ou dúvida de dependência volta ao TL.

2. **Executar a fase atribuída.** Investigar com iss-audit no modo dev: entregar diagnóstico/viabilidade e alternativas, mantendo experimento separado. Preparar interface/mock: entregar estados, contrato e demonstração sintética, sem antecipar banco/migration/API definitiva pendentes. Implementar/corrigir conforme plano e .bezalel/project.json, usando clean-code no código alterado e clean-architecture somente quando afetar responsabilidades, fronteiras ou dependências; executar testes próprios por risco e integrar consumidores reais. Toda operação somente de dados entrega artefato versionado com seleção, validação, repetição e recuperação. Corrigir falha ordinária autorizada; decisão de escopo/contrato/banco ou dependência externa volta ao TL. agent-browser pode apoiar reprodução e jornadas web, nas condições comuns.

3. **Entregar a contribuição identificada.** Entregar fase, versão, provas e limites ao TL. Na implementação, o dev integrador reúne contribuições/histórias, confere contratos/mock/API real e entrega candidato completo com base/head e testes. Contribuição parcial ou complemento de prova não libera o conjunto nem substitui revisão independente.

**Pronto:** entrega da fase verificável e limites explícitos. Conclusão de investigação/mock não autoriza implementação; TL confirma o próximo passo.

| Saída | Tipo | Destino |
|---|---|---|
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.

<a id="process-mobile"></a>

### Executar contribuição mobile

**Referência:** `mobile`. **Responsável:** Desenvolvedor mobile.

Preparar telas/estados/contratos mobile e exercitá-los com mock combinado com backend. Implementar/validar a integração na fase autorizada, identificando plataformas/dispositivos cobertos e limites nativos. Web não comprova recursos nativos. Um procedimento por especialidade; cada entrada executa somente a fase designada.

1. **Receber a tarefa e conferir pré-condições.** Conferir fase, pergunta/escopo, versão, dependências e entrega esperada. Aplicar R5–R6: investigação com isolamento; interface/mock após investigação; implementação após investigação, UI/UX e aprovações aplicáveis. Falta material ou dúvida de dependência volta ao TL.

2. **Executar a fase atribuída.** Investigar com iss-audit no modo dev: entregar diagnóstico/viabilidade e alternativas, mantendo experimento separado. Preparar interface/mock: entregar estados, contrato e demonstração sintética, sem antecipar banco/migration/API definitiva pendentes. Implementar/corrigir conforme plano e .bezalel/project.json, usando clean-code no código alterado e clean-architecture somente quando afetar responsabilidades, fronteiras ou dependências; executar testes próprios por risco e integrar consumidores reais. Toda operação somente de dados entrega artefato versionado com seleção, validação, repetição e recuperação. Corrigir falha ordinária autorizada; decisão de escopo/contrato/banco ou dependência externa volta ao TL.

3. **Entregar a contribuição identificada.** Entregar fase, versão, provas e limites ao TL. Na implementação, o dev integrador reúne contribuições/histórias, confere contratos/mock/API real e entrega candidato completo com base/head e testes. Contribuição parcial ou complemento de prova não libera o conjunto nem substitui revisão independente.

**Pronto:** entrega da fase verificável e limites explícitos. Conclusão de investigação/mock não autoriza implementação; TL confirma o próximo passo.

| Saída | Tipo | Destino |
|---|---|---|
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.

<a id="process-bank"></a>

### Preparar a proposta de banco

**Referência:** `bank`. **Responsável:** Tech Lead.

Proposta revisável somente quando estrutura, migration ou transformação complexa de relações exige decisão. Classificação técnica e plano simples de dados ficam na coordenação; não criar uma proposta vazia.

1. **Conferir impacto e classificação.** Identificar estrutura, operações de dados, artefatos/migrations, relações e consumidores. Qualquer mudança estrutural ou migration, inclusive de dados, exige aprovação prévia. Transformação complexa de relações por dados também exige proposta, DB Reviewer e decisão prévia, mesmo por script/comando. Complexidade considera integridade, cardinalidade, acoplamento e consumidores do conjunto; quantidade de tabelas/registros não decide sozinha. Dúvida técnica volta ao TL com pergunta/prova; persistindo materialmente ou envolvendo regra/autorização, TL apresenta ao humano.

2. **Preparar a alternativa revisável.** DB Reviewer é obrigatório para relações complexas; nos demais casos, usar proporcionalmente ao risco ou propor na issue. Com estrutura, comparar com a master identificada da ferramenta, sem alterá-la; sem estrutura, analisar modelo e vínculos/seleção antes/depois, sem inventar schema. Entregar alternativas, consumidores, compatibilidade, locks/volumes, ordem, validação e recuperação. clean-architecture apoia contratos/fronteiras; verification-planning apoia o plano de provas, sem substituir DB Reviewer. Ferramenta/base obrigatória ausente ou incapaz bloqueia; não implementar para demonstrar a proposta.

3. **Submeter a versão exata.** Publicar vN e conteúdo/referências recuperáveis na issue; exportar representação/comparação se necessário. Preservar texto UTF-8 e anexos; registrar SHA-256 em comentário separado para identificar o conteúdo, sem tratá-lo como aprovação. Encaminhar ao humano. Alteração material de conteúdo/base exige nova decisão; decisão anterior exata válida pode ser reaproveitada após conferência.

**Pronto:** proposta exata revisável com análise adequada; nenhuma implementação dependente iniciada.

| Saída | Tipo | Destino |
|---|---|---|
| Proposta identificada: decisão humana | Conclusão da atividade | Decidir a proposta de banco · v2 |
| Prova, classificação ou ferramenta insuficiente: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Prova, classificação ou ferramenta insuficiente: TL**: Classificação não está sustentada ou falta decisão de regra/escopo/autorização.
- Etapa 2 → **Prova, classificação ou ferramenta insuficiente: TL**: Modelo/base, ferramenta obrigatória ou evidência necessária está indisponível/incapaz.

<a id="process-bankDecision"></a>

### Decidir a proposta de banco

**Referência:** `bankDecision`. **Responsável:** APROVADOR HUMANO.

Decisão humana anterior à criação de migrations, implementação estrutural ou transformação complexa de relações por dados.

1. **Ler o conteúdo submetido.** Conferir vN, conteúdo identificado, comparação/modelo, efeitos sobre dados/consumidores, alternativas e recuperação. Esclarecer lacunas antes de decidir.

2. **Decidir a versão exata.** Aprovar ou solicitar reformulação/rejeitar solução, com interação real identificada. Aprovação anterior permanece utilizável somente se conteúdo/base/escopo pertinentes continuam cobertos. Não confundir recusa técnica com descarte da intenção.

3. **Devolver ao TL.** Registrar decisão e referências. Aprovação libera somente a mudança aprovada e dependentes com demais condições satisfeitas; TL retoma interface pendente ou implementação conforme o plano. Mudança de conteúdo exige reavaliar a aprovação.

**Pronto:** decisão real vinculada ao conteúdo exato; silêncio não autoriza. Trabalho independente segue R6, sem antecipar a parte pendente.

| Saída | Tipo | Destino |
|---|---|---|
| Decisão registrada: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Aguardando decisão ou esclarecimento | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 2 → **Aguardando decisão ou esclarecimento**: Decisão ausente, ambígua ou sem vínculo verificável com a proposta.

<a id="process-ui"></a>

### Revisar interface e contrato

**Referência:** `ui`. **Responsável:** Engenheiro de QA.

Revisão independente de UI/UX sobre telas e mock, antes da API definitiva afetada. É distinta do QA funcional sobre a integração real.

1. **Conferir a demonstração.** Receber telas/estados, contrato e mock de todas as interfaces selecionadas, com investigação válida. Conferir ambiente, objetivo e executor distinto dos autores; definir jornadas e observáveis aproveitando o plano de evidências pertinente.

2. **Exercitar as jornadas previstas.** Exercitar jornadas com agent-browser quando web e disponível, complementando os testes próprios de acessibilidade/plataforma. Conferir usabilidade, estados vazios/erro, autorização, dados e chamadas; exigir respostas coesas por tela e justificar separações por paginação, tamanho, cache, autorização, atualização ou falhas parciais, sem endpoint universal. Mock não comprova persistência, desempenho ou integração real.

3. **Devolver parecer e impacto.** Entregar parecer versionado e impacto em campos/relações/contratos. TL reconfere banco antes da API definitiva, inclusive após aprovação antecipada. Ajustes voltam aos autores via TL; reteste cobre correção e impactos.

**Pronto:** cobertura pertinente de todas as interfaces selecionadas, com evidência independente; não libera integração final.

| Saída | Tipo | Destino |
|---|---|---|
| Parecer UI/UX registrado: TL | Conclusão da atividade | Coordenar a entrega · v2 |
| Pré-condição ausente ou UI/UX reprovada: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Pré-condição ausente ou UI/UX reprovada: TL**: Mock/contribuição obrigatória está ausente ou falta independência/condição de execução.
- Etapa 2 → **Pré-condição ausente ou UI/UX reprovada: TL**: Problema de UI/UX/contrato exige ajuste ou decisão antes da API definitiva.

<a id="process-review"></a>

### Revisar a entrega integrada

**Referência:** `review`. **Responsável:** Tech Lead.

Uma revisão reúne completude da integração, versão e código. Elimina conferências separadas que inspecionavam o mesmo candidato.

1. **Conferir o candidato completo.** Iniciar um único pr-audit sobre o candidato completo do dev integrador, mesmo antes de existir PR. Conferir contribuições/histórias e decisões de investigação, UI/UX e banco. Parte pendente impede revisão final; TL não integra branches nem executa testes.

2. **Revisar código e contratos.** Aplicar pr-audit à conferência de alegações, diff, contratos, integração e provas. Usar clean-code e, havendo impacto arquitetural, clean-architecture, em modo sem edição, somente para aprofundar o mesmo parecer. Reutilizar provas válidas; solicitar testes/correções aos executores.

3. **Entregar conclusão identificada.** Concluir o mesmo pr-audit com versão, cobertura, achados e restrições. Candidato completo sem impedimento na revisão segue ao AppSec; correção ou prova faltante volta à coordenação com dono e retomada. Parecer técnico não é aceite humano nem autorização de merge.

**Pronto:** conjunto completo identificado e revisão aprovada; testes próprios não substituem QA independente.

| Saída | Tipo | Destino |
|---|---|---|
| Candidato revisado: AppSec | Conclusão da atividade | Analisar ou revalidar segurança · v2 |
| Entrega incompleta ou revisão reprovada: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Entrega incompleta ou revisão reprovada: TL**: Falta contribuição, pré-condição ou prova obrigatória, ou composição/base divergem.
- Etapa 2 → **Entrega incompleta ou revisão reprovada: TL**: Revisão encontrou defeito, incompatibilidade ou cobertura obrigatória insuficiente.

<a id="process-security"></a>

### Analisar ou revalidar segurança

**Referência:** `security`. **Responsável:** Especialista em Segurança de Aplicações (AppSec).

Um procedimento para consulta antecipada, análise da entrega e revalidação afetada. O tipo de entrada define o alcance; consulta não aprova a entrega.

1. **Definir objeto e cobertura.** Iniciar security-audit no alcance atribuído: consulta, análise da entrega ou revalidação. Fixar escopo/versão, independência e modelo de ameaças; análise da entrega requer integração e revisão TL. Aplicar checklist e referências pertinentes, distinguindo cobertura, não aplicável justificado e não verificado.

2. **Examinar e validar hipóteses.** Aplicar security-audit à inspeção e validação adversarial das hipóteses dentro do isolamento/autorização. Não devolver suspeita que o próprio AppSec ainda pode verificar. Recurso/decisão externa, crítico/alto confirmado ou lacuna material interrompem a parte afetada. Registrar prova sanitizada, confiança e severidade apenas do confirmado, conforme R8.

3. **Concluir parecer ou tratamento.** Concluir o parecer de security-audit, com provas de falsos positivos e limites. Escolher um destino: crítico/alto, lacuna material ou impedimento → TL; médio/baixo confirmado, cobertura suficiente e proposta completa/elegível de adiamento → humano, mantendo QA bloqueado. Sem proposta pendente, ou se recusada/inválida, correção → TL. Decisão válida cobre somente risco/versão/condições identificados. Entrega segue a QA só com cobertura/tratamento resolvidos; consulta/complemento retorna ao TL. Revalidar apenas impacto, reutilizando provas válidas.

**Pronto:** parecer versionado com cobertura suficiente e tratamento de todos os achados. Mesmo candidato sem mudança material reutiliza parecer; mudança relevante ou dúvida exige AppSec.

| Saída | Tipo | Destino |
|---|---|---|
| Parecer da entrega válido: QA | Conclusão da atividade | Validar critérios e jornadas · v2 |
| Consulta ou complemento concluído: TL | Encaminhamento | Coordenar a entrega · v2 |
| Proposta de adiar risco médio/baixo: humano | Encaminhamento | Decidir adiamento de risco · v2 |
| Achado bloqueante ou dependência externa: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Achado bloqueante ou dependência externa: TL**: Pré-condição material da análise está ausente ou falta independência/condição de execução.
- Etapa 2 → **Achado bloqueante ou dependência externa: TL**: Prova requer recurso/decisão externa, há crítico/alto confirmado ou lacuna material; suspeita investigável internamente permanece com AppSec.
- Etapa 3 → **Proposta de adiar risco médio/baixo: humano**: A única pendência é decisão humana sobre proposta completa e elegível de adiar achado médio/baixo confirmado, com cobertura suficiente e sem outro impedimento bloqueante. Usar somente esta rota, mantendo QA bloqueado enquanto a decisão estiver pendente.
- Etapa 3 → **Consulta ou complemento concluído: TL**: Entrada é consulta/complemento e a pergunta foi respondida sem novo impedimento; a resposta não substitui o parecer completo.
- Etapa 3 → **Achado bloqueante ou dependência externa: TL**: Achado confirmado exige correção e não há proposta completa e elegível de adiamento aguardando decisão humana; inclui proposta recusada ou decisão inválida. Crítico/alto confirmado, lacuna material ou outro impedimento bloqueante seguem ao TL e não usam a rota de adiamento.

<a id="process-risk"></a>

### Decidir adiamento de risco

**Referência:** `risk`. **Responsável:** APROVADOR HUMANO.

Decisão restrita a achados de segurança confirmados médios/baixos. Não equivale a adiar a intenção inteira ou aceitar o funcionamento.

1. **Ler a proposta de AppSec.** Conferir evidência, severidade, impacto, versão, alternativas, responsável e prazo/condição de tratamento. Crítico/alto ou cobertura material ausente exigem bloqueio/correção, não este adiamento.

2. **Decidir o tratamento.** Aceitar o adiamento delimitado ou solicitar correção/esclarecimento. Registrar interação real e objeto. Decisão ausente mantém pendência.

3. **Devolver o resultado pertinente.** Adiamento válido retorna ao AppSec para consolidar parecer; recusa ou proposta inelegível retorna ao TL para correção/replanejamento. Não tratar adiamento de risco como cancelamento integral. Preservar o tipo de entrada original do AppSec: consulta antecipada retorna ao TL e não libera QA; análise da entrega só libera após todas as condições.

**Pronto:** decisão verificável e delimitada sobre risco elegível.

| Saída | Tipo | Destino |
|---|---|---|
| Adiamento registrado: consolidar parecer | Conclusão da atividade | Analisar ou revalidar segurança · v2 |
| Corrigir ou rever tratamento: TL | Encaminhamento | Coordenar a entrega · v2 |
| Aguardando decisão ou esclarecimento | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Corrigir ou rever tratamento: TL**: Proposta inclui crítico/alto, lacuna material ou outro risco inelegível para adiamento.
- Etapa 2 → **Aguardando decisão ou esclarecimento**: Resposta ausente ou ambígua.
- Etapa 3 → **Corrigir ou rever tratamento: TL**: Humano não aceita o adiamento e solicita correção/revisão.

<a id="process-qa"></a>

### Validar critérios e jornadas

**Referência:** `qa`. **Responsável:** Engenheiro de QA.

QA independente da entrega completa. Bug, melhoria e feature usam o mesmo procedimento; as notas do cenário definem a cobertura específica.

1. **Conferir versão e cobertura necessária.** Receber candidato integrado com revisão TL e AppSec válidos; conferir independência e ambiente. Aplicar verification-planning aos critérios/riscos, confrontando e ampliando a cobertura do dev sem copiar apenas sua suíte. Reutilizar plano pertinente, com dados/pré-condições e cobertura específica do cenário.

2. **Executar critérios e jornadas.** Executar comportamento, integração real, regressões e E2E críticos do plano; agent-browser apoia jornadas web quando disponível. Feature exige cada história e depois jornadas/dependências globais no mesmo candidato. Dados exigem seleção, resultado, integridade, repetição e recuperação pertinentes; mobile exige plataformas/dispositivos identificados. Falha ou teste obrigatório ausente bloqueia; suspeita de segurança segue TL/AppSec.

3. **Consolidar o resultado independente.** Consolidar casos, resultados, evidências e limites da versão. Correção material exige reintegração e revisões TL/AppSec afetadas antes do reteste. Complemento de prova válida volta ao TL; QA integral aprovado segue ao pacote de aceite.

**Pronto:** critérios e integração pertinentes verificados independentemente, com evidência por versão. Feature exige cobertura individual e global.

| Saída | Tipo | Destino |
|---|---|---|
| QA completo aprovado: preparar aceite | Conclusão da atividade | Preparar o aceite humano · v2 |
| Complemento de prova concluído: TL | Encaminhamento | Coordenar a entrega · v2 |
| Falha ou cobertura obrigatória ausente: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Falha ou cobertura obrigatória ausente: TL**: Candidato, review, AppSec, ambiente ou independência obrigatórios não estão válidos.
- Etapa 2 → **Falha ou cobertura obrigatória ausente: TL**: Falha funcional/integrada, teste obrigatório não executado ou suspeita de segurança necessita tratamento.
- Etapa 3 → **Complemento de prova concluído: TL**: Solicitação era apenas complementar prova existente, verificável e válida, sem nova falha; não declarar QA inteiro concluído.

<a id="process-package"></a>

### Preparar o aceite humano

**Referência:** `package`. **Responsável:** Tech Lead.

Pacote único de evidências e roteiro manual para o candidato validado. Nos cenários 2/3, roteiro Excel .xlsx real e acessível; no bug, roteiro proporcional.

1. **Conferir evidências do conjunto.** Conferir escopo, integração, AppSec, QA e decisões da mesma versão. Reutilizar provas válidas; lacuna ou mudança material retorna ao responsável via coordenação.

2. **Preparar roteiro e acesso.** Aplicar development-test-workbook para produzir e conferir o .xlsx real/acessível dos cenários 2/3; no bug, usar quando o roteiro proporcional for Excel. Sem Excel, manter versão, ambiente, pré-condições/dados, critérios, passos, esperado e observado/status, executor/data e evidências. Casos humanos permanecem não executados, sem herdar QA. Preparar acesso autorizado sem segredos.

3. **Apresentar o pacote.** Apresentar pacote, links, instruções, limites e decisões pendentes; humanizer pode revisar apenas a apresentação. Solicitar execução e aceite do conjunto identificado. Falha de acesso/apresentação mantém pendência.

**Pronto:** QA integral válido e pacote realmente acessível, com casos humanos ainda não executados.

| Saída | Tipo | Destino |
|---|---|---|
| Roteiro e candidato apresentados: humano | Conclusão da atividade | Executar roteiro e decidir aceite · v2 |
| Versão, prova ou acesso insuficiente: TL | Impedimento/reprovação | Coordenar a entrega · v2 |

**Condições locais das etapas:**

- Etapa 1 → **Versão, prova ou acesso insuficiente: TL**: Há alteração material, evidência obrigatória ausente ou resultado invalidado.
- Etapa 2 → **Versão, prova ou acesso insuficiente: TL**: Roteiro/acesso/ambiente obrigatório não pôde ser preparado ou verificado.

<a id="process-accept"></a>

### Executar roteiro e decidir aceite

**Referência:** `accept`. **Responsável:** APROVADOR HUMANO.

Aceite funcional externo sobre a versão apresentada. A execução do humano permanece distinta do QA.

1. **Conferir candidato e roteiro.** Abrir pacote/ambiente identificados; esclarecer impedimentos de acesso, dados ou versão antes de executar.

2. **Executar e registrar o observado.** Executar os casos humanos aplicáveis e registrar observado, resultado, data/executor e evidência. Casos não executados permanecem assim; não herdar resultado do QA.

3. **Decidir o aceite do conjunto.** Aceitar a versão validada ou descrever falhas/ajustes. Mudança de necessidade vai a PM/TL; defeito segue correção e revisões afetadas. Registrar decisão real; aceite não autoriza merge/deploy nem cobre versão alterada por inferência.

**Pronto:** execução humana suficiente e aceite explícito vinculado à versão.

| Saída | Tipo | Destino |
|---|---|---|
| Aceite registrado: entregar PR | Conclusão da atividade | Abrir PRs e entregar próximos passos · v2 |
| Falha, impedimento ou ajuste: TL | Encaminhamento | Coordenar a entrega · v2 |
| Roteiro ou decisão pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Falha, impedimento ou ajuste: TL**: Acesso, dados ou candidato impedem a execução e precisam de ação/decisão.
- Etapa 2 → **Roteiro ou decisão pendente**: Execução humana permanece pendente, com condição e responsável identificados.
- Etapa 3 → **Falha, impedimento ou ajuste: TL**: Humano rejeita ou solicita alteração/esclarecimento; não concluir a entrega.
- Etapa 3 → **Roteiro ou decisão pendente**: Aceite ausente ou ambíguo.

<a id="process-pr"></a>

### Abrir PRs e entregar próximos passos

**Referência:** `pr`. **Responsável:** Tech Lead.

Conclusão com todas as PRs necessárias abertas/verificadas para as bases de produção reais e orientação manual entregue. Junta conferência final de versões/checks e abertura.

1. **Conferir autorização, candidato e evidências.** Identificar repositórios e branch de produção nas instruções do projeto, sem presumir nome. Conferir autorização concreta para publicar branch/abrir PR, candidato completo, banco/UI/UX, review, AppSec, QA e aceite; todos na versão correspondente. Comparar composição, base/head/diff, contratos, schema/dados, dependências/configuração. Sem mudança material, reutilizar pareceres e aceite; diferença material ou dúvida de impacto exige revalidação afetada. Checks obrigatórios disponíveis antes da abertura precisam passar.

2. **Abrir e verificar as PRs reais.** Publicar somente branches autorizadas e abrir/verificar todas as PRs necessárias com base/head, issues e evidências corretos; humanizer pode revisar a descrição antes da publicação. Preservar PRs já abertas e retomar somente o faltante após falha, sem duplicar. Sem verificação, manter pendência; divergência confirmada volta ao TL/revalidação. Não habilitar auto-merge.

3. **Conferir até o handoff e orientar Rafael.** Reler estado/base/head das PRs e candidato até o handoff: divergência confirmada, inclusive pós-abertura, retorna à coordenação. Informar CI disparado apenas pela PR no estado observado, inclusive pendente/falho e distinguindo checks prévios, sem espera/correção automática posterior. Entregar links, ordem de integração/liberação, validações, riscos/pendências e passos manuais de merge/deploy/dados/recuperação; humanizer pode revisar a orientação. Concluir com todas as PRs verificadas e orientação apresentada.

**Pronto:** todas as PRs e próximo passo manual entregues para a versão validada. PR aberta não prova merge, deploy ou publicação em produção.

| Saída | Tipo | Destino |
|---|---|---|
| PRs verificadas e orientação entregue | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Versão divergente ou revalidação necessária: TL | Impedimento/reprovação | Coordenar a entrega · v2 |
| Abertura, verificação ou orientação pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Versão divergente ou revalidação necessária: TL**: Versão/condição mudou materialmente ou falta evidência obrigatória que exige ação de outro responsável.
- Etapa 1 → **Abertura, verificação ou orientação pendente**: Falta autorização/acesso já encaminhado; manter rascunho e condição de retomada.
- Etapa 2 → **Versão divergente ou revalidação necessária: TL**: A leitura comprova base/head/composição divergente do candidato validado.
- Etapa 2 → **Abertura, verificação ou orientação pendente**: Não foi possível abrir ou verificar alguma PR; preservar as existentes e retomar o faltante.
- Etapa 3 → **Versão divergente ou revalidação necessária: TL**: Antes do handoff, foi confirmada divergência material ou nova questão de segurança, mesmo com PR já aberta.
- Etapa 3 → **Abertura, verificação ou orientação pendente**: Orientação não entregue ou estado das PRs não verificável, sem divergência confirmada.
- Etapa 3 → **PRs verificadas e orientação entregue**: Todas as PRs necessárias foram abertas/verificadas no candidato válido e a orientação foi apresentada a Rafael.

## Diferenças aplicadas nas participações

### Cenário 1

- **Qualificar e conduzir o bug · v2**: Bug: fonte, observado/esperado, reprodução, impacto e critério de correção. Comportamento esperado exige decisão humana e fechamento verificado.
- **Coordenar a entrega · v2**: Consolidar diagnóstico já realizado; delimitar menor correção segura. Separar residual sem dispensar segurança.
- **Analisar ou revalidar segurança · v2**: Examinar causa, correção e regressões de segurança no fluxo atingido.
- **Validar critérios e jornadas · v2**: Validar reprodução original, correção, regressões e integração da versão; considerar acesso/dados de outros usuários. Relato não reproduzido não significa ausência de defeito.
- **Preparar o aceite humano · v2**: Roteiro manual proporcional ao bug, com reprodução, resultado esperado e regressões relevantes.

### Cenário 2

- **Qualificar e conduzir a melhoria · v2**: Melhoria: necessidade, benefício, limites e critérios observáveis; escopo pequeno é confirmado tecnicamente após investigação.
- **Coordenar a entrega · v2**: Confirmar escopo pequeno após investigação. Se necessário, propor transferência humana à feature.
- **Analisar ou revalidar segurança · v2**: Examinar entradas/API, permissões, dados e dependências alteradas; tamanho não define risco.
- **Validar critérios e jornadas · v2**: Validar benefício/critério esperado, limites acordados e regressões do comportamento existente na integração real.
- **Preparar o aceite humano · v2**: Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.

### Cenário 3

- **Definir e conduzir o escopo da feature · v2**: Feature: principal e histórias, comentários de submissão vN, decisão humana correspondente e handoff da mesma versão ao TL.
- **Coordenar a entrega · v2**: Exigir recebimento da vN aprovada; planejar todas as histórias/dependências e um integrador do conjunto.
- **Analisar ou revalidar segurança · v2**: Analisar histórias/jornadas integradas, ativos, perfis e fronteiras de confiança; parecer de parte isolada não aprova o conjunto.
- **Validar critérios e jornadas · v2**: No mesmo candidato completo, validar critérios de cada história e depois jornadas globais, dependências e integração entre serviços. Uma história isolada aprovada não conclui a feature.
- **Preparar o aceite humano · v2**: Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.

## Correspondência com o MCP

Empresa **Fluxo de IA**, `534d1f66-90a5-462d-bf78-29c6ccf9ef94`.
A revisão **1179** é a referência de conversão. O [catálogo](catalog.json) associa
os IDs estáveis de cargos, cenários e processos aos contratos e às skills.
Os três cenários são 1 — Bug v2, 2 — Melhoria v2 e 3 — Feature v2; os 74 processos
antigos que ainda existem no catálogo visual não integram este pacote de execução.

Em mudanças acordadas do fluxo, releia o MCP, preserve alterações concorrentes e
confira procedimentos, decisões, condições e conexões nos dois sentidos.
Validação estrutural não prova equivalência semântica. Os arquivos são a fonte
canônica; agentes, skills e adaptadores não autenticam decisões nem concedem acesso.
