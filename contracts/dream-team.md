# DreamTeam — fluxo de desenvolvimento

Fonte canônica do fluxo de desenvolvimento da [DreamTeam](README.md), equipe de
agentes do plugin Bezalel. São três cenários, 21 processos reutilizáveis e 63
etapas, com 19 processos em cada cenário; os quatro devs são opções de especialidade.
Os contratos em [agents](README.md) distribuem os processos por responsabilidade,
sem criar um agente por etapa. O aprovador humano é externo.

## Regras comuns

Estas regras são a fonte local comum aos três cenários. O fluxo é mantido neste repositório e não exige envio, sincronização ou aprovação em serviço de modelagem. Cada atividade usa as pré-condições do destino, inclusive nas retomadas. Condições locais complementam, sem substituir, o procedimento e estas regras.

### R1 Registro e autorização

Usar a mesma issue, quando existir, como registro da intenção, escopo, decisões e evidências; sem issue, usar a conversa da tarefa e depois a PR. Referências à issue nas etapas seguem essa regra; não criar issue fictícia ou obrigatória apenas para encerrar. Anexos ficam vinculados. Registrar o mínimo antes de qualquer destino. Efeitos externos dependem da autorização concreta da tarefa, aproveitando a já concedida. Ausência de acesso/autorização mantém pendência e rascunho verificável. O mapa documenta responsabilidades; não executa ferramentas, autentica pessoas ou concede permissão.

### R2 Responsabilidade e evidência

TL planeja, coordena e revisa código/evidências; nunca implementa, compõe branches de implementação ou executa testes. Escolhe somente os especialistas necessários e um dev responsável pela integração inteira. Devs executam investigação, preparação, implementação e testes próprios; DevOps cuida do isolamento; QA e AppSec verificam independentemente dos autores. Evidência identifica escopo e candidato: repositórios, base/head, componentes/builds, contratos, dados/schema, dependências e configuração pertinentes.

### R3 Passagem entre atividades

Cada tarefa informa objetivo/fase, responsável, entrada/versão, entrega esperada e condição de conclusão. Fases dos devs: investigar, preparar interface/mock ou implementar/corrigir. Concluir uma tarefa ou complementar prova não aprova a entrega inteira. Selecionar somente os destinos necessários; saídas não disparam todos os participantes. Provas válidas são reutilizadas; só mudança com impacto exige refazer a cobertura afetada.

### R4 Interrupção e retomada

Interromper a parte afetada assim que faltar condição ou surgir reprovação/decisão necessária, antes de efeitos dependentes. Registrar na issue motivo, prova/lacuna, versão, dono e ponto/condição de retomada; falha de gravação preserva rascunho e erro. Problema novo vai ao TL; pendência já atribuída permanece no processo atual. Correção ordinária dentro da tarefa autorizada fica com o executor. Espera não é conclusão; silêncio não decide. Condições locais destacam desvios relevantes, sem copiar esta regra em toda etapa.

### R5 Investigação e preparação

Investigação dos devs é obrigatória antes de implementar, proporcional ao impacto; diagnóstico válido do bug já a satisfaz. Experimentos não entram automaticamente na entrega. Antes da investigação executável, DevOps comprova isolamento de arquivos, banco, filas, portas e storage; não aplicável exige motivo concreto. Reutilizar ambiente válido sem recriá-lo. Novas branches/worktrees usam uma descrição curta em minúsculas, sem acentos, separada por hífens (`corrigir-login`); números só quando significativos (`migrar-php-84`). Não acrescentar prefixos de agente/tipo como `codex/` ou `feat/`, nem sufixos aleatórios. Usar exatamente o mesmo nome na branch, na pasta `.worktrees/<nome>` e no ambiente ENV. Produção não é ambiente de teste. Ferramenta ou recurso obrigatório indisponível é bloqueio, não dispensa.

### R6 Interface e banco

Com interface afetada: telas/contrato → mock exercitável → QA de UI/UX, antes da API definitiva afetada. Sem interface, justificar. TL escolhe banco antecipado quando campos/relações estão estáveis, ou interface primeiro; aprovação antecipada retorna à interface pendente. Após UI/UX, reconferir banco. Estrutura, qualquer migration e transformação complexa de relações por dados exigem proposta e decisão humana exata anteriores à implementação correspondente. Trabalho independente pode avançar com condições próprias e independência demonstrada pelo TL; pendência bloqueia as partes dependentes e a conclusão do conjunto.

### R7 Revisões proporcionais

Abrir a PR assim que integração completa, revisão TL, AppSec, QA independente, checks prévios e roteiro estiverem prontos na mesma versão. O aceite funcional humano ocorre na PR aberta; não o exigir para publicar a PR, nem simulá-lo ao abrir ou verificar merge. TL define verificações por impacto; devs executam as próprias e QA confronta/amplia a cobertura. Técnica não pertinente aceita justificativa; teste obrigatório falho/não executado bloqueia. QA da feature cobre histórias e jornadas globais no mesmo processo. Nenhuma contribuição parcial libera a revisão final do conjunto.

### R8 Segurança

AppSec distingue hipótese, confirmação, severidade, confiança e cobertura. Valida hipóteses dentro do isolamento e autorização disponíveis antes de devolver; dependência externa/decisão pode interromper antes. Crítico/alto confirmado ou lacuna material bloqueia. Médio/baixo confirmado exige correção ou adiamento humano explícito com motivo, dono e prazo/condição. Falso positivo exige prova. Nova questão de segurança vai ao AppSec via TL; issue residual não dispensa tratamento. Evidências são sanitizadas; segredos/dados privados não entram em issue ou PR.

### R9 Decisões e destinos

Decisão humana registra interação real, identidade, fonte, data/fuso e conteúdo/versão. Reaproveitar decisão que já cubra o objeto; ambiguidade exige esclarecimento. Rejeitar solução não cancela a intenção. PM trata revisão parcial, adiamento integral, descarte, reabertura e transferência na entrada do cenário: adiar mantém issue aberta com dono/retomada; descartar fecha e verifica somente itens abrangidos/exclusivos; reabrir requer orientação humana. Transferência exige destino iniciado/verificado na mesma issue antes de encerrar origem; use o percurso vigente do destino. Estados sem implementação dispensam PR/scan fictícios.

### R10 PR, aceite e encerramento

Concluídos desenvolvimento e validações técnicas, publicar a branch da tarefa e abrir/verificar todas as PRs prontas para revisão, sem draft, para as bases reais configuradas, sem pedir uma nova autorização apenas para abrir a PR. Restrição expressa do usuário ou do repositório, acesso ausente ou check prévio falho mantém pendência concreta. CI que só inicia pela PR é informado no estado observado. Entregar o roteiro para aceite na PR aberta; aprovação refere-se à versão examinada e não autoriza o agente a fazer merge ou deploy.

Quando o usuário aprovar a entrega ou informar que fez merge, TL consulta o serviço novamente e confirma todas as PRs e respectivos base/head/merge commit. Aprovação, branch removida ou PR fechada não provam merge. Sem merge confirmado, manter issue e ambiente e informar a pendência; não fazer polling ou agendar acompanhamento por inferência. Merge confirmado permite fechar/verificar somente issues do escopo realmente concluído e encaminhar ao DevOps o encerramento do ambiente da branch da tarefa. Limpeza segue o contrato da skill, incluindo preservação, identificação do alvo e bloqueios; parcialidade permanece registrada. Merge e deploy continuam humanos.

## Seleção de skills nas etapas

As etapas indicam objetivo, responsável, condição e entrega; o método fica na skill indicada, em skills/<nome>/SKILL.md do Bezalel, com suas referências. Aplicar somente o modo/fase pertinente. Uma aplicação pode atender várias etapas do mesmo trabalho: não reiniciar auditoria, plano ou redação a cada passagem; reutilizar artefatos/provas ainda válidos. Apoios condicionais só entram quando úteis. Skill não cria agente, gate, autorização ou transferência de responsabilidade. Se indisponível, registrar o limite e usar procedimento equivalente disponível; prova/ferramenta obrigatória ausente segue R4.
iss-audit: qualificação PM ou investigação dev, conforme fase. pr-audit: revisão TL sem editar/testar. clean-code inclui simplificação; clean-architecture aplica-se a fronteiras afetadas. implementar-snapshots só para construir/corrigir a funcionalidade. verification-planning orienta provas proporcionais; TL planeja/confere e executores produzem evidência. Pesquisa dependente de @librarian indisponível fica registrada, sem inventar agente ou conclusão; infraestrutura de verificação depende da autorização própria.
agent-browser exige CLI/guia da versão e alvo isolado autorizado; não instalar por inferência. MCP continua preferido para operações do serviço. Browser apoia a prova da interface, sem substituir regressão automatizada, acessibilidade completa, serviços/persistência ou mobile nativo. humanizer é opcional na redação antes da submissão/publicação; não muda fatos, critérios, respostas, resultados ou decisões versionadas.
security-audit fica em auditoria/validação: correção de produto volta a TL/dev; não ampliar credenciais, remover GITHUB_TOKEN, alterar/encerrar alertas ou cancelar CI por esta indicação. Cópias originais permanecem intactas; pr-audit e iss-audit usam variantes autorizadas. Skills reservadas ao uso manual e candidatas pendentes no inventário ficam fora das etapas; nenhuma é disparada ao concluir PR/auditoria.

O [inventário completo](skills-inventario.md) registra origem, cópias e adaptações pendentes. A [relação por processo e etapa](dream-team-skills.md) facilita consultar a seleção. As adaptações autorizadas de pr-audit e iss-audit estão identificadas; as demais cópias preservam o conteúdo original. Os agentes referenciam essas skills sem duplicar seus procedimentos.

## Percursos dos cenários

### 1 Bug investigar e entregar a correção

**Entrada:** Relato de possível defeito ou retomada humana, com esperado/observado/evidências a esclarecer.

Foco: separar hipótese, comportamento esperado e defeito; investigar antes de definir a menor correção segura. Diagnóstico suficiente é a investigação obrigatória. Residual de produto fica vinculado; suspeita/achado de segurança precisa de tratamento. Humano decide regra, comportamento esperado e reclassificação. Transferências permitidas: 2 ou 3, iniciadas/verificadas pelo PM na mesma issue.

**Percurso:** PM qualifica a intenção e resolve decisões de produto necessárias → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → TL abre/verifica PRs e apresenta roteiro → humano avalia → ao aprovar ou avisar merge, TL confere merge/fecha issues aplicáveis → DevOps encerra o ambiente identificado.

**QA específico:** Validar reprodução original, correção, regressões e integração da versão; considerar acesso/dados de outros usuários. Relato não reproduzido não significa ausência de defeito.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão tecnicamente validada, com roteiro e orientação entregues a Rafael. Encerramento posterior exige merge consultado no serviço, issues aplicáveis verificadas e ambiente tratado conforme o processo pós-merge. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

### 2 Melhoria delimitar e validar a mudança

**Entrada:** Melhoria de comportamento existente ou transferência humana do bug; benefício e limite a confirmar.

Foco: resultado observável e escopo pequeno, confirmado pelo TL após investigação de comportamento, contratos e dependências. Mudança de regra/escopo precisa de decisão humana; aproveitar o pedido já claro. Se a investigação revelar trabalho de feature, humano decide transferência a 3 e PM inicia/verifica o destino na mesma issue. Roteiro de aceite em Excel .xlsx real.

**Percurso:** PM qualifica a intenção e resolve decisões de produto necessárias → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → TL abre/verifica PRs e apresenta roteiro → humano avalia → ao aprovar ou avisar merge, TL confere merge/fecha issues aplicáveis → DevOps encerra o ambiente identificado.

**QA específico:** Validar benefício/critério esperado, limites acordados e regressões do comportamento existente na integração real.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão tecnicamente validada, com roteiro e orientação entregues a Rafael. Encerramento posterior exige merge consultado no serviço, issues aplicáveis verificadas e ambiente tratado conforme o processo pós-merge. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

### 3 Feature aprovar e entregar o conjunto

**Entrada:** Capacidade nova ou mudança grande, inclusive transferência humana de bug/melhoria; exige visão, histórias e critérios globais.

Foco: principal e histórias curtas vinculadas, critérios individuais/globais, dependências e um dev integrador. Humano aprova o escopo vN; PM confere e entrega a mesma versão ao TL antes da investigação/planejamento técnico. Investigar viabilidade obrigatoriamente e confirmar plano do conjunto. Uma única atividade de QA verifica histórias e depois jornadas globais na feature completa. Roteiro de aceite em Excel .xlsx real.

**Percurso:** PM registra principal/histórias → humano decide vN → PM entrega ao TL → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → TL abre/verifica PRs e apresenta roteiro → humano avalia → ao aprovar ou avisar merge, TL confere merge/fecha issues aplicáveis → DevOps encerra o ambiente identificado.

**QA específico:** No mesmo candidato completo, validar critérios de cada história e depois jornadas globais, dependências e integração entre serviços. Uma história isolada aprovada não conclui a feature.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão tecnicamente validada, com roteiro e orientação entregues a Rafael. Encerramento posterior exige merge consultado no serviço, issues aplicáveis verificadas e ambiente tratado conforme o processo pós-merge. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

## Procedimentos dos responsáveis

Os identificadores curtos abaixo organizam a correspondência documental; não são um runtime. As entradas de retorno recebem contexto, fase/objeto, versão e origem. Cada processo tem uma entrada de retorno; os três processos PM também têm entrada inicial. As saídas abaixo são exclusivas/selecionadas conforme a condição, exceto tarefas independentes explicitamente atribuídas a mais de um dev.

<a id="process-bug"></a>

### Qualificar e conduzir o bug

**Referência:** `bug`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 1: relato, decisões de produto e destinos sem correção. Referência: regras comuns no processo Coordenar a entrega.

1. **Garantir o registro mínimo.** Localizar/verificar a issue existente, ou registrar relato e fonte na conversa da tarefa quando não houver issue. Criar issue somente se fizer parte do pedido. Decisão integral de adiamento/descarte segue ao destino; retomada reabre/verifica o objeto existente autorizado.

2. **Definir a necessidade.** Aplicar iss-audit no modo PM para qualificar necessidade, esperado/observado, impacto, perfis/dados, hipóteses e critérios. Não exigir causa comprovada para investigar. Dúvida de regra, esperado ou reclassificação exige decisão humana. Usar humanizer somente se a redação precisar de revisão.

3. **Entregar contexto ou registrar destino.** Aplicar R9 na mesma issue. Revisão parcial preserva a intenção restante e confere a decisão sobre o conteúdo atualizado; decisão integral não exige detalhamento/investigação. Descarte/adiamento/reabertura têm estados reais verificados; falha permanece no PM. Transferência humana a 2 ou 3 exige destino iniciado/verificado, mesmo se adiado. Encerrar como comportamento esperado só com confirmação humana, justificativa e fechamento verificado, registrando ausência de correção. Caso qualificado segue ao TL.

**Pronto:** issue real e contexto suficiente para investigação; ou destino próprio decidido e verificado. Não exige comprovar a causa para iniciar.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Transferência verificada para 2 ou 3 | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Falha de registro/reabertura/verificação: preservar rascunho e atribuir retomada ao PM.
- Etapa 2 → **Decisão de produto necessária**: Regra, escopo, comportamento esperado ou reclassificação precisam de decisão humana.
- Etapa 3 → **Intenção adiada e registrada**: Decisão integral de adiar registrada; issue aberta verificada, dono e retomada definidos.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte ou comportamento esperado possuem decisão humana e fechamento verificado.
- Etapa 3 → **Transferência verificada para 2 ou 3**: Destino 2 ou 3 iniciado e verificado com a mesma issue.

<a id="process-improvement"></a>

### Qualificar e conduzir a melhoria

**Referência:** `improvement`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 2: melhoria do comportamento existente com benefício e limite claros.

1. **Garantir o registro mínimo.** Localizar/verificar a issue existente ou usar a conversa da tarefa, inclusive em transferência; registrar intenção, fonte e decisão. Criar issue somente se fizer parte do pedido. Retomada, adiamento e descarte seguem R9.

2. **Definir resultado e limites.** Aplicar iss-audit no modo PM para definir benefício, comportamento atual/desejado, critérios, exclusões e dependências, usuários/perfis, dados e integrações pertinentes. Encaminhar dúvidas de segurança. TL confirma o impacto limitado após investigar; mudança de regra/escopo exige humano, aproveitando pedido já inequívoco. humanizer é opcional para revisar a redação.

3. **Entregar contexto ou registrar destino.** Aplicar R9 na mesma issue. Revisão parcial preserva a intenção restante e confere a decisão sobre o conteúdo atualizado; decisão integral dispensa detalhamento/investigação. Verificar estados reais de descarte/adiamento/reabertura; falha permanece no PM. Transferência humana a 3 exige destino iniciado/verificado, mesmo se adiado. Entregar ao TL a versão correspondente dos requisitos e decisões.

**Pronto:** benefício e critérios suficientes para investigar, com escopo autorizado; ou destino próprio verificado.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo |
| Pendência de registro ou resposta | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção adiada e registrada | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Intenção encerrada sem implementação | Estado próprio | Estado descrito na saída; não encaminha outro processo |
| Transferência verificada para 3 | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Pendência de registro ou resposta**: Registro, retomada ou verificação da issue falhou; pendência atribuída ao PM.
- Etapa 2 → **Decisão de produto necessária**: Falta decisão de regra/escopo ou o reenquadramento para feature requer decisão humana.
- Etapa 3 → **Intenção adiada e registrada**: Adiamento integral registrado, com issue aberta e retomada.
- Etapa 3 → **Intenção encerrada sem implementação**: Descarte integral decidido e fechamento dos itens abrangidos verificado.
- Etapa 3 → **Transferência verificada para 3**: Cenário 3 iniciado e verificado com a mesma issue.

<a id="process-feature"></a>

### Definir e conduzir o escopo da feature

**Referência:** `feature`. **Responsável:** Product Manager.

Entrada e manutenção do cenário 3: visão e histórias aprovadas como conjunto, com um responsável pela integração.

1. **Registrar visão e histórias.** Identificar a demanda principal na issue existente ou conversa. Aplicar iss-audit no modo PM para qualificar visão, necessidades, limites, perfis/dados/integrações e questões de segurança. Vincular histórias curtas com referências distintas, critérios individuais, dependências e exclusões; a principal reúne critérios globais. Não inventar URLs ou criar issues só para satisfazer o contrato. humanizer pode revisar a redação antes de submeter a versão.

2. **Submeter ou conferir a versão do escopo.** Registrar visão/limites/prioridades e histórias em comentários vN na principal e em cada história, preservando o conteúdo submetido. Obter decisão humana sobre esse conjunto antes do planejamento técnico. Mudança material cria vN+1 e confere decisão correspondente; aproveitar resposta já explícita que cubra a mudança/resultante.

3. **Entregar a mesma versão ou registrar destino.** Aplicar R9 na mesma issue: revisão parcial preserva a intenção restante e confere a decisão atual; destino integral dispensa detalhamento/investigação. Descarte abrange somente itens exclusivos autorizados; reabertura inclui somente histórias descartadas retomadas pelo humano. Verificar estados reais e manter falha pendente no PM. TL confirma recebimento da vN aprovada; divergência volta ao PM, e falta de acesso não é revisão fictícia de escopo.

**Pronto:** principal e histórias vinculadas, escopo vN com decisão correspondente e entrega ao TL; ou destino próprio verificado.

| Saída | Tipo | Destino |
|---|---|---|
| Contexto conferido: TL | Conclusão da atividade | Coordenar a entrega |
| Decisão de produto necessária | Encaminhamento | Decidir regra ou escopo |
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

3. **Encaminhar ou retomar pela condição comprovada.** Encaminhar somente a atividade necessária, respeitando R6–R8 e a ordem integração completa → revisão → AppSec → QA → pacote → PR → aceite → conferência de merge → encerramento. Retomar o ponto pendente com provas ainda válidas; complemento não conclui atividade nem libera gate. Mudança de código/composição exige os controles afetados. Residual de segurança segue AppSec/tratamento; residual de produto fica vinculado sem ampliar escopo. Pendência mantém dono/retomada, sem ciclo automático.

**Pronto:** próximo resultado, responsável, versão e pré-condições identificados; todas as condições do destino satisfeitas. Conclusão de tarefa não aprova a entrega inteira. Aplicam-se as regras comuns R1–R10 da descrição.

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

<a id="process-env"></a>

### Preparar, recuperar ou encerrar o ambiente

**Referência:** `env`. **Responsável:** Engenheiro DevOps.

Preparação/recuperação durante o trabalho e encerramento somente após a conferência pós-merge. Usar a skill env carregada e seu contrato de bancos compartilhados; não implementar outro destruidor de ambientes.

1. **Conferir alvos e autorização.** Usar env para conferir projeto, manifesto/base/contexto, recursos e ação: preparar, reutilizar, recuperar ou encerrar. Registrar durante a tarefa repositório, branch da worktree, caminho, ambiente associado e contexto Docker. Na limpeza, receber prova de merge e tratamento das issues; resolver `{{current-worktree-branch}}` pela branch da tarefa registrada, não pela branch do terminal após trocar de diretório. Na criação, escolher a descrição curta de R5 e passar esse nome à ENV, que cria a branch e `.worktrees/<nome>`; não criar outra worktree com nome ou prefixo imposto pelo aplicativo. Conferir colisões antes de criar; quando precisar distinguir tarefas, acrescentar uma palavra ou número significativo, sem reutilizar ambiente alheio. Em ambientes preexistentes, conferir a associação exata no estado da skill: nomes podem diferir e devem ser preservados, sem renomear branch, pasta, dados ou estado automaticamente. Ausência/ambiguidade mantém pendência, sem adivinhar nomes ou criar ambiente para destruí-lo.

2. **Executar a operação pertinente.** Aplicar o procedimento de env e, quando houver pools, sua referência de bancos compartilhados. Entregar prova de isolamento de arquivos, banco, filas, portas e storage conforme R5; arquivos sempre comprovados, demais dimensões não aplicáveis somente com motivo. Em pools, comprovar recursos/credenciais próprios, configuração dos consumidores e recusa de acesso cruzado. Preservar dados/configurações; não usar produção nem limpeza como teste. Para encerrar, preservar arquivos rastreados/não rastreados/ignorados, commits, dados e backups necessários fora da worktree; verificar a preservação. Executar o destroy da skill no projeto correto com o nome de ambiente associado e confirmação exata `projeto/ambiente`, a partir de um diretório que não será removido. Não usar força, excluir por prefixo ou remover pools/imagens/infraestrutura compartilhada. Squash/rebase pode impedir a prova de ancestralidade: não contornar a proteção; conservar worktree/branch e reportar o que ficou pendente. `--keep-worktree` permite apenas o encerramento parcial autorizado do ambiente após preservar dados, nunca declarar remoção completa da worktree.

3. **Entregar provas e ponto de retomada.** Entregar ao TL identificação, versões, provas e limitações. Na preparação/recuperação, comprovar isolamento e indicar provas invalidadas. No encerramento, verificar recursos removidos e preservados, worktree/branch e resultado da skill; falha ou remoção parcial mantém pendência. Se já destruído, conferir o registro e a ausência dos alvos, sem repetir por nome aproximado. Sem ambiente gerenciado, registrar não aplicável com evidência; não usar limpeza genérica como substituta.

**Pronto:** preparação/recuperação com isolamento comprovado; ou encerramento do alvo exato confirmado, com preservação e resultado documentados. Remoção parcial não é conclusão completa.

| Saída | Tipo | Destino |
|---|---|---|
| Ambiente/prova entregue: TL | Conclusão da atividade | Coordenar a entrega |
| Encerramento conferido: TL | Conclusão da atividade | Conferir merge e encerrar a tarefa |
| Impedimento ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.

<a id="process-bank"></a>

### Preparar a proposta de banco

**Referência:** `bank`. **Responsável:** Tech Lead.

Proposta HTML temporária quando há estrutura, qualquer migration ou transformação complexa de relações. A fonte é o código/schema/migrations da base real identificada no projeto; não consultar produção para produzir a proposta.

1. **Conferir impacto e base.** Identificar repositório, commit/base, estrutura, dados, relações, consumidores e escopo. Toda migration, inclusive de dados, exige decisão anterior à implementação dependente. Relações complexas exigem parecer técnico identificado do TL ou revisor competente disponível, sem ferramenta específica obrigatória. Falta de fonte/evidência material bloqueia; não inventar estado atual.

2. **Preparar o HTML revisável.** Partir do [template HTML](templates/database-review.html) e salvar somente a cópia da tarefa em `.bezalel/reviews/database-<tarefa>-<versao>.html`. Antes de gerar, conferir/adicionar `/reviews/` ao `.bezalel/.gitignore` preservando regras existentes; a cópia não entra em Git. Mostrar estrutura atual e proposta lado a lado: tabelas, colunas/tipos/nulabilidade/defaults, chaves, índices, restrições e relações/cardinalidades; identificar adições, alterações, remoções e o que permanece. Em mudança só de dados, mostrar seleção e transformação antes/depois, sem inventar mudança estrutural. Explicar necessidade, alternativas, consumidores, compatibilidade, migração/backfill, locks/volume, validação e recuperação. clean-architecture apoia fronteiras; verification-planning apoia provas. HTML autocontido, UTF-8, sem scripts remotos, credenciais ou dados pessoais; inspecionar a renderização antes de apresentar. Não implementar a migration para ilustrar a proposta.

3. **Submeter e preservar a decisão.** Apresentar o HTML acessível, base/escopo e versão exatos ao humano. Registrar referência, resumo suficiente da estrutura/diferenças, hash dos bytes e eventual parecer na issue ou conversa; hash não é aprovação. Ajuste solicitado mantém a proposta pendente: atualizar o HTML, identificar nova versão e reapresentar. Após aprovação ou rejeição final, registrar a interação real e o conteúdo decidido fora do HTML, excluir somente as cópias temporárias dessa proposta e verificar a ausência. Falha de registro ou exclusão mantém pendência; não remover o template do pacote. Nova mudança material exige novo HTML e decisão.

**Pronto:** HTML apresentado com base e conteúdo verificáveis; após decisão final, registro preservado e cópias temporárias excluídas. Aprovação não é inferida da exclusão.

| Saída | Tipo | Destino |
|---|---|---|
| Proposta identificada: decisão humana | Conclusão da atividade | Decidir a proposta de banco |
| Ajuste solicitado | Encaminhamento | Preparar a proposta de banco |
| Fonte, registro ou exclusão pendente | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Fonte, registro ou exclusão pendente**: Base/estrutura real ou análise necessária indisponível.
- Etapa 3 → **Ajuste solicitado**: Humano pede reformulação; não interpretar como aprovação ou rejeição final.
- Etapa 3 → **Fonte, registro ou exclusão pendente**: Não foi possível preservar a decisão ou excluir o HTML após a decisão final.

<a id="process-bankDecision"></a>

### Decidir a proposta de banco

**Referência:** `bankDecision`. **Responsável:** APROVADOR HUMANO.

Decisão sobre o HTML apresentado antes da implementação dependente, incluindo estrutura e diferença entre estado atual e proposta.

1. **Conferir conteúdo e alcance.** Examinar HTML, base/versão, estrutura, impactos, alternativas e limites. Esclarecer lacunas antes de decidir; não requer envio a outra ferramenta.

2. **Decidir a versão exata.** Aprovar, pedir ajuste ou rejeitar a proposta final em interação real. Pedido de ajuste volta ao TL para novo HTML e nova avaliação; não é autorização para implementar. Aprovação anterior só vale para o conteúdo/base/escopo que efetivamente cobre.

3. **Devolver ao TL.** TL preserva decisão e resumo, exclui/verifica o HTML temporário após decisão final e só então retoma interface ou implementação dependente com demais condições satisfeitas. Rejeição não cancela a intenção automaticamente; TL/PM tratam o próximo passo. Se o humano voltar a mudar a proposta, reapresentar uma nova versão.

**Pronto:** decisão final identificada ou ajuste claramente solicitado; nenhum agente decide pelo humano.

| Saída | Tipo | Destino |
|---|---|---|
| Aprovação final registrada | Encaminhamento | Coordenar a entrega, após excluir o HTML |
| Ajuste solicitado | Encaminhamento | Preparar a proposta de banco |
| Rejeição final | Encaminhamento | Coordenar a entrega, após registrar e excluir o HTML |
| Aguardando decisão ou esclarecimento | Estado próprio | Permanecer nesta atividade |

**Condições locais das etapas:**

- Etapa 2 → **Aguardando decisão ou esclarecimento**: Resposta ausente, ambígua ou de outra versão.
- Etapa 2 → **Ajuste solicitado**: Alteração solicitada sem aprovação do conteúdo novo.

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
| Parecer UI/UX registrado: TL | Conclusão da atividade | Coordenar a entrega |
| Pré-condição ausente ou UI/UX reprovada: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Candidato revisado: AppSec | Conclusão da atividade | Analisar ou revalidar segurança |
| Entrega incompleta ou revisão reprovada: TL | Impedimento/reprovação | Coordenar a entrega |

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
| Adiamento registrado: consolidar parecer | Conclusão da atividade | Analisar ou revalidar segurança |
| Corrigir ou rever tratamento: TL | Encaminhamento | Coordenar a entrega |
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
| QA completo aprovado: preparar aceite | Conclusão da atividade | Preparar o aceite humano |
| Complemento de prova concluído: TL | Encaminhamento | Coordenar a entrega |
| Falha ou cobertura obrigatória ausente: TL | Impedimento/reprovação | Coordenar a entrega |

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

3. **Apresentar o pacote.** Apresentar pacote, links, instruções, limites e decisões pendentes; humanizer pode revisar apenas a apresentação. Encaminhar a abertura da PR com roteiro pronto para o humano executar e avaliar. Falha de acesso/apresentação mantém pendência.

**Pronto:** QA integral válido e pacote realmente acessível, com casos humanos ainda não executados.

| Saída | Tipo | Destino |
|---|---|---|
| Roteiro e candidato preparados: PR | Conclusão da atividade | Abrir PRs e entregar próximos passos |
| Versão, prova ou acesso insuficiente: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Versão, prova ou acesso insuficiente: TL**: Há alteração material, evidência obrigatória ausente ou resultado invalidado.
- Etapa 2 → **Versão, prova ou acesso insuficiente: TL**: Roteiro/acesso/ambiente obrigatório não pôde ser preparado ou verificado.

<a id="process-accept"></a>

### Executar roteiro e decidir aceite

**Referência:** `accept`. **Responsável:** APROVADOR HUMANO.

Aceite funcional externo na PR já aberta, sobre a versão apresentada. A execução do humano permanece distinta do QA; abertura de PR não depende deste aceite.

1. **Conferir candidato e roteiro.** Abrir pacote/ambiente identificados; esclarecer impedimentos de acesso, dados ou versão antes de executar.

2. **Executar e registrar o observado.** Executar os casos humanos aplicáveis e registrar observado, resultado, data/executor e evidência. Casos não executados permanecem assim; não herdar resultado do QA.

3. **Decidir o aceite do conjunto.** Aceitar a versão validada ou descrever falhas/ajustes. Mudança de necessidade vai a PM/TL; defeito segue correção e revisões afetadas. Registrar decisão real; aceite não autoriza merge/deploy nem cobre versão alterada por inferência.

**Pronto:** execução humana suficiente e aceite explícito vinculado à versão.

| Saída | Tipo | Destino |
|---|---|---|
| Aceite registrado: conferir merge | Conclusão da atividade | Conferir merge e encerrar a tarefa |
| Falha, impedimento ou ajuste: TL | Encaminhamento | Coordenar a entrega |
| Roteiro ou decisão pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Falha, impedimento ou ajuste: TL**: Acesso, dados ou candidato impedem a execução e precisam de ação/decisão.
- Etapa 2 → **Roteiro ou decisão pendente**: Execução humana permanece pendente, com condição e responsável identificados.
- Etapa 3 → **Falha, impedimento ou ajuste: TL**: Humano rejeita ou solicita alteração/esclarecimento; não concluir a entrega.
- Etapa 3 → **Roteiro ou decisão pendente**: Aceite ausente ou ambíguo.

<a id="process-pr"></a>

### Abrir PRs e entregar próximos passos

**Referência:** `pr`. **Responsável:** Tech Lead.

Entrega técnica com todas as PRs necessárias abertas/verificadas assim que desenvolvimento e validações terminarem. O aceite humano e a conferência de merge vêm depois, na PR; manter o ambiente para essa avaliação.

1. **Conferir autorização, candidato e evidências.** Identificar repositórios e branch de produção nas instruções do projeto, sem presumir nome. A adoção deste fluxo com o pedido de desenvolvimento inclui publicar a branch da tarefa e abrir a PR após as validações, salvo restrição expressa do usuário/projeto. Conferir candidato completo, banco/UI/UX, review, AppSec, QA e roteiro; todos na versão correspondente. Aceite funcional posterior não bloqueia a abertura. Comparar composição, base/head/diff, contratos, schema/dados, dependências/configuração. Sem mudança material, reutilizar pareceres válidos; diferença material ou dúvida de impacto exige revalidação afetada. Checks obrigatórios disponíveis antes da abertura precisam passar.

2. **Abrir e verificar as PRs reais.** Publicar somente branches autorizadas e abrir/verificar todas as PRs necessárias com base/head, issues e evidências corretos, abertas e prontas para revisão (`draft: false` no serviço); humanizer pode revisar a descrição antes da publicação. Preservar PRs já abertas e retomar somente o faltante após falha, sem duplicar. Se uma PR anterior estiver em draft, marcá-la como pronta para revisão após as validações e conferir o estado; não entregá-la como draft. Sem verificação, manter pendência; divergência confirmada volta ao TL/revalidação. Não habilitar auto-merge.

3. **Conferir até o handoff e orientar Rafael.** Reler estado/base/head das PRs e candidato até o handoff: divergência confirmada, inclusive pós-abertura, retorna à coordenação. Informar CI disparado apenas pela PR no estado observado, inclusive pendente/falho e distinguindo checks prévios, sem espera/correção automática posterior. Entregar links, ordem de integração/liberação, validações, riscos/pendências e passos manuais de merge/deploy/dados/recuperação; humanizer pode revisar a orientação. Concluir a entrega técnica com todas as PRs verificadas e roteiro apresentado. Rejeição ou ajuste humano posterior retoma correção e validações afetadas na mesma PR; aprovação ou aviso de merge retoma a conferência pós-merge.

**Pronto:** todas as PRs abertas, prontas para revisão e sem draft, com próximo passo manual entregue para a versão validada. PR aberta não prova merge, deploy ou publicação em produção.

| Saída | Tipo | Destino |
|---|---|---|
| PRs verificadas e roteiro entregue | Encaminhamento | Executar roteiro e decidir aceite |
| Aprovação ou aviso de merge recebido | Encaminhamento | Conferir merge e encerrar a tarefa |
| Versão divergente ou revalidação necessária: TL | Impedimento/reprovação | Coordenar a entrega |
| Abertura, verificação ou orientação pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Versão divergente ou revalidação necessária: TL**: Versão/condição mudou materialmente ou falta evidência obrigatória que exige ação de outro responsável.
- Etapa 1 → **Abertura, verificação ou orientação pendente**: Falta autorização/acesso já encaminhado; manter rascunho e condição de retomada.
- Etapa 2 → **Versão divergente ou revalidação necessária: TL**: A leitura comprova base/head/composição divergente do candidato validado.
- Etapa 2 → **Abertura, verificação ou orientação pendente**: Não foi possível abrir ou verificar alguma PR; preservar as existentes e retomar o faltante.
- Etapa 3 → **Versão divergente ou revalidação necessária: TL**: Antes do handoff, foi confirmada divergência material ou nova questão de segurança, mesmo com PR já aberta.
- Etapa 3 → **Abertura, verificação ou orientação pendente**: Orientação não entregue ou estado das PRs não verificável, sem divergência confirmada.
- Etapa 3 → **PRs verificadas e orientação entregue**: Todas as PRs necessárias foram abertas/verificadas no candidato válido e a orientação foi apresentada a Rafael.

<a id="process-postMerge"></a>

### Conferir merge e encerrar a tarefa

**Referência:** `postMerge`. **Responsável:** Tech Lead.

Retomada por aprovação humana da entrega ou aviso de merge, sem serviço de monitoramento. Pode ocorrer depois de outra sessão; reutilizar identidade das PRs, candidato e branch da tarefa, nunca o diretório atual como único indício.

1. **Consultar todas as PRs da entrega.** Registrar a interação humana e consultar GitHub pelo MCP/API/CLI disponível. Confirmar repositório, URL, base, head validado, estado merged, data e commit de merge para cada PR. PR aprovada, fechada sem merge, inacessível ou com versão divergente impede fechamento/limpeza; informar o estado e aguardar nova orientação ou evento real. Não executar merge, auto-merge, deploy ou polling por inferência.

2. **Encerrar somente o escopo concluído.** Confirmar que todas as PRs necessárias foram mergeadas e que não resta trabalho nas issues abrangidas. Fechar a issue existente e as histórias integralmente resolvidas; reler e verificar o estado. Se já fechada automaticamente, apenas verificar. Sem issue, registrar não aplicável. Não fechar história alheia, intenção residual ou principal com pendências; falha mantém a retomada registrada e precede a limpeza.

3. **Encaminhar e conferir o encerramento do ambiente.** Passar ao DevOps a identidade registrada de projeto/branch/worktree/ambiente, evidência de merge e estado das issues. O pedido deste fluxo autoriza encerrar somente esse ambiente após preservar o necessário. Receber e registrar resultado, alvos removidos/preservados e pendências. Guardar evidências na conversa/PR/issue ou fora da worktree antes da remoção. Se não houver ambiente gerenciado, registrar a verificação; não simular destruição. Falha de limpeza não reabre uma issue resolvida nem repete o fechamento.

**Pronto:** merges reais verificados, issues aplicáveis conferidas e ambiente encerrado ou comprovadamente não aplicável. Branch/worktree preservada por bloqueio significa encerramento parcial, informado ao usuário.

| Saída | Tipo | Destino |
|---|---|---|
| Merge ainda não comprovado | Estado próprio | Aguardar orientação/evento real, preservando ambiente e issues |
| Versão divergente ou trabalho restante | Encaminhamento | Coordenar a entrega |
| Issues verificadas: encerrar ambiente | Encaminhamento | Preparar, recuperar ou encerrar o ambiente |
| Encerramento concluído | Estado próprio | Informar resultado final |
| Encerramento parcial | Estado próprio | Registrar bloqueio, dono e condição de retomada |

**Condições locais das etapas:**

- Etapa 1 → **Merge ainda não comprovado**: Qualquer PR necessária não está mergeada/verificável.
- Etapa 2 → **Encerramento parcial**: Falha ao fechar/verificar issue; não passar à limpeza.
- Etapa 3 → **Encerramento parcial**: Preservação, identificação ou execução da limpeza ficou incompleta.

## Diferenças aplicadas nas participações

### Cenário 1

- **Qualificar e conduzir o bug**: Bug: fonte, observado/esperado, reprodução, impacto e critério de correção. Comportamento esperado exige decisão humana e fechamento verificado.
- **Coordenar a entrega**: Consolidar diagnóstico já realizado; delimitar menor correção segura. Separar residual sem dispensar segurança.
- **Analisar ou revalidar segurança**: Examinar causa, correção e regressões de segurança no fluxo atingido.
- **Validar critérios e jornadas**: Validar reprodução original, correção, regressões e integração da versão; considerar acesso/dados de outros usuários. Relato não reproduzido não significa ausência de defeito.
- **Preparar o aceite humano**: Roteiro manual proporcional ao bug, com reprodução, resultado esperado e regressões relevantes.

### Cenário 2

- **Qualificar e conduzir a melhoria**: Melhoria: necessidade, benefício, limites e critérios observáveis; escopo pequeno é confirmado tecnicamente após investigação.
- **Coordenar a entrega**: Confirmar escopo pequeno após investigação. Se necessário, propor transferência humana à feature.
- **Analisar ou revalidar segurança**: Examinar entradas/API, permissões, dados e dependências alteradas; tamanho não define risco.
- **Validar critérios e jornadas**: Validar benefício/critério esperado, limites acordados e regressões do comportamento existente na integração real.
- **Preparar o aceite humano**: Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.

### Cenário 3

- **Definir e conduzir o escopo da feature**: Feature: principal e histórias, comentários de submissão vN, decisão humana correspondente e handoff da mesma versão ao TL.
- **Coordenar a entrega**: Exigir recebimento da vN aprovada; planejar todas as histórias/dependências e um integrador do conjunto.
- **Analisar ou revalidar segurança**: Analisar histórias/jornadas integradas, ativos, perfis e fronteiras de confiança; parecer de parte isolada não aprova o conjunto.
- **Validar critérios e jornadas**: No mesmo candidato completo, validar critérios de cada história e depois jornadas globais, dependências e integração entre serviços. Uma história isolada aprovada não conclui a feature.
- **Preparar o aceite humano**: Arquivo Excel .xlsx real, acessível e vinculado ao candidato; casos humanos começam não executados.

## Fonte e manutenção

Este documento, o catálogo e os contratos dos papéis são as fontes do fluxo.
Mantenha cenários, etapas, decisões, condições e referências coerentes entre os
arquivos. IDs existentes permanecem estáveis; não é necessário enviar propostas
ou sincronizar o fluxo com um serviço externo. O checker confere estrutura e
vínculos, sem provar equivalência semântica, decisão humana ou execução real.
