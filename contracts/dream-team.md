# DreamTeam — fluxo de desenvolvimento

Fonte canônica do fluxo de desenvolvimento da [DreamTeam](README.md), equipe de
agentes do plugin Bezalel. São três cenários, 21 processos reutilizáveis e 63
etapas, com 19 processos em cada cenário; os quatro devs são opções de especialidade.
Os contratos em [agents](README.md) distribuem os processos por responsabilidade,
sem criar um agente por etapa. O aprovador humano é externo.

Este arquivo reúne as regras comuns, os percursos dos cenários e o índice dos
processos. Cada papel lê estas regras e somente os [processos](#processos) que o
[catálogo](catalog.json) lhe atribui.

## Glossário

- **Solicitante:** pessoa que pediu a demanda e decide o aceite; é o aprovador humano externo.
- **Candidato:** versão integrada (repositórios, base/head e composição) em revisão, validação e entrega.
- **vN:** versão numerada do escopo aprovado da feature; mudança de escopo gera nova versão.
- **Destino:** resultado registrado de uma intenção (corrigir, adiar, descartar, transferir) ou processo indicado numa saída.
- **Classe:** pequena, normal ou grande; ver [Classes de demanda](#classes-de-demanda).
- **Mudança material:** alteração que invalida prova já feita; ver [R3](#r3-passagem-entre-atividades).
- **Tipos de saída:** *Encaminhamento* passa a outro processo; *Conclusão da atividade* encerra o processo e segue ao destino; *Estado próprio* aguarda sem encaminhar; *Impedimento/reprovação* devolve com motivo e retomada.
- **Entrada de retorno:** retomada de um processo já iniciado, com contexto, fase, versão e origem.
- **R1–R11:** regras comuns abaixo; valem para todos os papéis. Como aplicar skills nas etapas: [relação por etapa](dream-team-skills.md#como-aplicar).

## Regras comuns

Estas regras são a fonte local comum aos três cenários. O fluxo é mantido neste repositório e não exige envio, sincronização ou aprovação em serviço de modelagem. Cada atividade usa as pré-condições do destino, inclusive nas retomadas. Condições locais complementam, sem substituir, o procedimento e estas regras.

### R1 Registro e autorização

Usar a mesma issue, quando existir, como registro da intenção, escopo, decisões e evidências; sem issue, usar a conversa da tarefa e depois a PR. Referências à issue nas etapas seguem essa regra; não criar issue fictícia ou obrigatória apenas para encerrar. Anexos ficam vinculados. Registrar o mínimo antes de qualquer destino. Efeitos externos dependem da autorização concreta da tarefa, aproveitando a já concedida. Ausência de acesso/autorização mantém pendência e rascunho verificável. Estes documentos descrevem responsabilidades; não executam ferramentas, autenticam pessoas nem concedem permissão.

### R2 Responsabilidade e evidência

TL planeja, coordena e revisa código/evidências; nunca implementa, compõe branches de implementação ou executa testes. Escolhe somente os especialistas necessários e um dev responsável pela integração inteira. Devs executam investigação, preparação, implementação e testes próprios; DevOps cuida do isolamento; QA e AppSec verificam independentemente dos autores. Evidência identifica escopo e candidato: repositórios, base/head, componentes/builds, contratos, dados/schema, dependências e configuração pertinentes. Revisor diferente no texto não comprova executor independente: TL, QA e AppSec não podem revisar sua própria implementação. Executores distintos exigem ferramentas de delegação/coordenação da aplicação ou um operador que conduza as atribuições; não simular subagentes mudando o nome do papel numa única execução.

Tarefas transversais têm dono fixo: **CI que falha depois de abrir a PR** → o dev integrador corrige na mesma branch e o TL revalida só o afetado (R3); **plano de reversão** (código, dados e configuração) → o dev integrador prepara, o TL confere e publica na PR; **dados de teste** → o QA define o que precisa no plano e o DevOps provisiona dados sintéticos ou sanitizados no ambiente isolado.

### R3 Passagem entre atividades

Cada tarefa informa objetivo/fase, responsável, entrada/versão, entrega esperada e condição de conclusão. Fases dos devs: investigar, preparar interface/mock ou implementar/corrigir. Concluir uma tarefa ou complementar prova não aprova a entrega inteira. Selecionar somente os destinos necessários; saídas não disparam todos os participantes. Provas válidas são reutilizadas; só mudança com impacto exige refazer a cobertura afetada.

**Mudança material** é a que invalida prova já feita. A lista é fechada:

| Alteração no candidato | Refazer |
|---|---|
| Código de produção, migrations, schema/dados ou dependências | Revisão TL e QA das partes afetadas |
| Autenticação/autorização, entrada externa, dados sensíveis, configuração ou dependências | Também AppSec |
| Contrato de API/integração ou interface | Também UI/UX e QA das jornadas afetadas |
| Apenas comentários, formatação, documentação ou testes sem mudança de comportamento | Nada; registrar a diferença |

Na dúvida sobre impacto, tratar como material e revalidar. Ao passar trabalho adiante:
comunicar só mudança relevante, dar contexto delimitado com fontes acessíveis, delegar
uma entrega completa por fase e reutilizar provas cuja validade foi conferida. Quem
delega segue também a [coordenação de atribuições](coordenacao.md), com a seleção
proporcional de modelos.

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

### R11 Desempate e limite de ciclos

Quando papéis discordam, decide o dono do tema; quem discorda registra a evidência e não
repete a mesma objeção sem fato novo.

| Tema | Decide | Escala ao humano quando |
|---|---|---|
| Severidade, falso positivo e tratamento de segurança | AppSec; TL contesta só com prova | Adiamento de médio/baixo ou conflito persistente |
| Defeito funcional versus comportamento esperado | QA reporta; TL decide se é defeito | Esperado depende de regra de produto |
| Regra de negócio, escopo e critério de aceite | PM com o humano | Sempre que não houver decisão registrada |
| Desenho técnico, ordem e divisão do trabalho | TL | Afeta escopo, prazo ou risco aceito |
| Ambiente e isolamento | DevOps | Exige recurso compartilhado ou autorização |

O ciclo correção → revisão → AppSec → QA tem limite de **dois retornos pelo mesmo
problema**. No terceiro, o TL interrompe (R4), resume as tentativas, as provas e as
alternativas, e leva a decisão ao solicitante.

## Classes de demanda

No planejamento, o TL classifica a demanda e registra a classe na issue. A classe define
os artefatos; as revisões independentes continuam em todas.

| | Pequena | Normal | Grande |
|---|---|---|---|
| Quando | Bug ou melhoria localizada: poucos arquivos, sem migration/schema, sem contrato de API/integração, sem tocar autenticação, entrada externa, dados sensíveis, dependências ou configuração | Demais bugs e melhorias | Feature (cenário 3) |
| Qualificação | TL registra esperado, observado e reprodução; PM só se o esperado for duvidoso | PM | PM e escopo vN aprovado |
| Isolamento | Worktree própria; demais dimensões não aplicáveis com motivo em uma linha | Prova completa (R5) | Prova completa (R5) |
| Dev | Uma atribuição: teste que falha, correção e teste de regressão | Investigação, plano e implementação | Investigação de viabilidade e plano do conjunto |
| Revisão TL | pr-audit sobre o diff | Completa | Completa |
| AppSec | Triagem curta: toca superfície de segurança? Se sim, análise completa | Completa | Completa |
| QA independente | Reprodução, regressão e 2 a 3 casos vizinhos | Completo | Histórias e jornadas |
| Roteiro | Checklist em Markdown na PR | Checklist em Markdown; Excel com 8 ou mais casos, conferência de dados ou pedido | Excel .xlsx |
| Banco | Não se aplica: migration torna a demanda normal | Proposta HTML e decisão humana (R6) | Proposta HTML e decisão humana (R6) |

A demanda pequena passa a normal assim que surgir migration, mudança de contrato, achado
de segurança, segundo retorno do QA ou sinal de feature; registre o motivo e siga o
percurso completo a partir do ponto atual, reaproveitando provas válidas.

## Percursos dos cenários

Cada cenário tem entrada, foco e início próprios; a partir do TL, os três seguem o
[percurso comum](#percurso-comum). A cobertura específica de cada participação fica
nas diferenças por cenário do respectivo processo.

### 1 Bug investigar e entregar a correção

**Entrada:** Relato de possível defeito ou retomada humana, com esperado/observado/evidências a esclarecer.

Foco: separar hipótese, comportamento esperado e defeito; investigar antes de definir a menor correção segura. Diagnóstico suficiente é a investigação obrigatória. Residual de produto fica vinculado; suspeita/achado de segurança precisa de tratamento. Humano decide regra, comportamento esperado e reclassificação. Transferências permitidas: 2 ou 3, iniciadas/verificadas pelo PM na mesma issue.

**Início:** PM qualifica a intenção e resolve decisões de produto necessárias; na classe pequena, o TL registra o relato.

### 2 Melhoria delimitar e validar a mudança

**Entrada:** Melhoria de comportamento existente ou transferência humana do bug; benefício e limite a confirmar.

Foco: resultado observável e escopo pequeno, confirmado pelo TL após investigação de comportamento, contratos e dependências. Mudança de regra/escopo precisa de decisão humana; aproveitar o pedido já claro. Se a investigação revelar trabalho de feature, humano decide transferência a 3 e PM inicia/verifica o destino na mesma issue. Roteiro de aceite conforme a [classe](#classes-de-demanda).

**Início:** PM qualifica a intenção e resolve decisões de produto necessárias; na classe pequena, o TL registra o relato.

### 3 Feature aprovar e entregar o conjunto

**Entrada:** Capacidade nova ou mudança grande, inclusive transferência humana de bug/melhoria; exige visão, histórias e critérios globais.

Foco: principal e histórias curtas vinculadas, critérios individuais/globais, dependências e um dev integrador. Humano aprova o escopo vN; PM confere e entrega a mesma versão ao TL antes da investigação/planejamento técnico. Investigar viabilidade obrigatoriamente e confirmar plano do conjunto. Uma única atividade de QA verifica histórias e depois jornadas globais na feature completa. Roteiro de aceite em Excel .xlsx real.

**Início:** PM registra principal/histórias → humano decide vN → PM entrega ao TL.

### Percurso comum

**Percurso:** início do cenário → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → TL abre/verifica PRs e apresenta roteiro → humano avalia → ao aprovar ou avisar merge, TL confere merge/fecha issues aplicáveis → DevOps encerra o ambiente identificado.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão tecnicamente validada, com roteiro e orientação entregues ao solicitante. Encerramento posterior exige merge consultado no serviço, issues aplicáveis verificadas e ambiente tratado conforme o processo pós-merge. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

## Processos

Os identificadores curtos organizam a correspondência documental; não são um runtime. As entradas de retorno recebem contexto, fase/objeto, versão e origem. Cada processo tem uma entrada de retorno; os três processos PM também têm entrada inicial. As saídas de cada processo são exclusivas/selecionadas conforme a condição, exceto tarefas independentes explicitamente atribuídas a mais de um dev.

Cada processo fica em [`processes/<referência>.md`](processes/), com etapas, saídas, condições locais
e diferenças por cenário. O [índice de processos](#índice-de-processos) relaciona
responsáveis, etapas e skills para consulta.

## Índice de processos

Gerado por `scripts/dream_team.py` a partir dos arquivos de processo; não edite à mão.
Lista os processos por responsável, na ordem do catálogo, com as skills de cada etapa.
Serve para consulta; cada papel lê somente os arquivos dos processos atribuídos.
As âncoras preservam os links `dream-team.md#process-<referência>`.

<a id="process-bug"></a>

### Qualificar e conduzir o bug

**Referência:** `bug`. **Responsável:** Product Manager.

Procedimento: [processes/bug.md](processes/bug.md).

1. **Garantir o registro mínimo.**
2. **Definir a necessidade.** Skills: iss-audit, humanizer.
3. **Entregar contexto ou registrar destino.**

<a id="process-improvement"></a>

### Qualificar e conduzir a melhoria

**Referência:** `improvement`. **Responsável:** Product Manager.

Procedimento: [processes/improvement.md](processes/improvement.md).

1. **Garantir o registro mínimo.**
2. **Definir resultado e limites.** Skills: iss-audit, humanizer.
3. **Entregar contexto ou registrar destino.**

<a id="process-feature"></a>

### Definir e conduzir o escopo da feature

**Referência:** `feature`. **Responsável:** Product Manager.

Procedimento: [processes/feature.md](processes/feature.md).

1. **Registrar visão e histórias.** Skills: iss-audit, humanizer.
2. **Submeter ou conferir a versão do escopo.**
3. **Entregar a mesma versão ou registrar destino.**

<a id="process-plan"></a>

### Coordenar a entrega

**Referência:** `plan`. **Responsável:** Tech Lead.

Procedimento: [processes/plan.md](processes/plan.md).

1. **Confirmar contexto e o que falta.**
2. **Definir o próximo resultado e suas condições.** Skills: verification-planning, clean-architecture.
3. **Encaminhar ou retomar pela condição comprovada.**

<a id="process-bank"></a>

### Preparar a proposta de banco

**Referência:** `bank`. **Responsável:** Tech Lead.

Procedimento: [processes/bank.md](processes/bank.md).

1. **Conferir impacto e base.**
2. **Preparar o HTML revisável.** Skills: clean-architecture, verification-planning, proposta-banco.
3. **Submeter e preservar a decisão.**

<a id="process-review"></a>

### Revisar a entrega integrada

**Referência:** `review`. **Responsável:** Tech Lead.

Procedimento: [processes/review.md](processes/review.md).

1. **Conferir o candidato completo.** Skills: pr-audit.
2. **Revisar código e contratos.** Skills: pr-audit, clean-code, clean-architecture.
3. **Entregar conclusão identificada.** Skills: pr-audit.

<a id="process-package"></a>

### Preparar o aceite humano

**Referência:** `package`. **Responsável:** Tech Lead.

Procedimento: [processes/package.md](processes/package.md).

1. **Conferir evidências do conjunto.**
2. **Preparar roteiro e acesso.** Skills: development-test-workbook.
3. **Apresentar o pacote.** Skills: humanizer.

<a id="process-pr"></a>

### Abrir PRs e entregar próximos passos

**Referência:** `pr`. **Responsável:** Tech Lead.

Procedimento: [processes/pr.md](processes/pr.md).

1. **Conferir autorização, candidato e evidências.**
2. **Abrir e verificar as PRs reais.** Skills: humanizer.
3. **Conferir até o handoff e orientar o solicitante.** Skills: humanizer.

<a id="process-postMerge"></a>

### Conferir merge e encerrar a tarefa

**Referência:** `postMerge`. **Responsável:** Tech Lead.

Procedimento: [processes/postMerge.md](processes/postMerge.md).

1. **Consultar todas as PRs da entrega.**
2. **Encerrar somente o escopo concluído.**
3. **Encaminhar e conferir o encerramento do ambiente.**

<a id="process-env"></a>

### Preparar, recuperar ou encerrar o ambiente

**Referência:** `env`. **Responsável:** Engenheiro DevOps.

Procedimento: [processes/env.md](processes/env.md).

1. **Conferir alvos e autorização.** Skills: env.
2. **Executar a operação pertinente.** Skills: env.
3. **Entregar provas e ponto de retomada.**

<a id="process-fullstack"></a>

### Executar contribuição fullstack

**Referência:** `fullstack`. **Responsável:** Desenvolvedor fullstack.

Procedimento: [processes/fullstack.md](processes/fullstack.md).

1. **Receber a tarefa e conferir pré-condições.**
2. **Executar a fase atribuída.** Skills: iss-audit, clean-code, clean-architecture, implementar-snapshots, agent-browser, depurar-bug.
3. **Entregar a contribuição identificada.**

<a id="process-backend"></a>

### Executar contribuição backend

**Referência:** `backend`. **Responsável:** Desenvolvedor backend.

Procedimento: [processes/backend.md](processes/backend.md).

1. **Receber a tarefa e conferir pré-condições.**
2. **Executar a fase atribuída.** Skills: iss-audit, clean-code, clean-architecture, implementar-snapshots, depurar-bug.
3. **Entregar a contribuição identificada.**

<a id="process-web"></a>

### Executar contribuição web

**Referência:** `web`. **Responsável:** Desenvolvedor frontend web.

Procedimento: [processes/web.md](processes/web.md).

1. **Receber a tarefa e conferir pré-condições.**
2. **Executar a fase atribuída.** Skills: iss-audit, clean-code, clean-architecture, agent-browser, depurar-bug.
3. **Entregar a contribuição identificada.**

<a id="process-mobile"></a>

### Executar contribuição mobile

**Referência:** `mobile`. **Responsável:** Desenvolvedor mobile.

Procedimento: [processes/mobile.md](processes/mobile.md).

1. **Receber a tarefa e conferir pré-condições.**
2. **Executar a fase atribuída.** Skills: iss-audit, clean-code, clean-architecture, depurar-bug.
3. **Entregar a contribuição identificada.**

<a id="process-ui"></a>

### Revisar interface e contrato

**Referência:** `ui`. **Responsável:** Engenheiro de QA.

Procedimento: [processes/ui.md](processes/ui.md).

1. **Conferir a demonstração.**
2. **Exercitar as jornadas previstas.** Skills: agent-browser.
3. **Devolver parecer e impacto.**

<a id="process-qa"></a>

### Validar critérios e jornadas

**Referência:** `qa`. **Responsável:** Engenheiro de QA.

Procedimento: [processes/qa.md](processes/qa.md).

1. **Conferir versão e cobertura necessária.** Skills: verification-planning.
2. **Executar critérios e jornadas.** Skills: agent-browser.
3. **Consolidar o resultado independente.**

<a id="process-security"></a>

### Analisar ou revalidar segurança

**Referência:** `security`. **Responsável:** Especialista em Segurança de Aplicações (AppSec).

Procedimento: [processes/security.md](processes/security.md).

1. **Definir objeto e cobertura.** Skills: security-audit.
2. **Examinar e validar hipóteses.** Skills: security-audit.
3. **Concluir parecer ou tratamento.** Skills: security-audit.

<a id="process-product"></a>

### Decidir regra ou escopo

**Referência:** `product`. **Responsável:** APROVADOR HUMANO.

Procedimento: [processes/product.md](processes/product.md).

1. **Conferir o objeto.**
2. **Decidir sobre o conteúdo identificado.**
3. **Devolver a decisão ao PM.**

<a id="process-bankDecision"></a>

### Decidir a proposta de banco

**Referência:** `bankDecision`. **Responsável:** APROVADOR HUMANO.

Procedimento: [processes/bankDecision.md](processes/bankDecision.md).

1. **Conferir conteúdo e alcance.**
2. **Decidir a versão exata.**
3. **Devolver ao TL.**

<a id="process-risk"></a>

### Decidir adiamento de risco

**Referência:** `risk`. **Responsável:** APROVADOR HUMANO.

Procedimento: [processes/risk.md](processes/risk.md).

1. **Ler a proposta de AppSec.**
2. **Decidir o tratamento.**
3. **Devolver o resultado pertinente.**

<a id="process-accept"></a>

### Executar roteiro e decidir aceite

**Referência:** `accept`. **Responsável:** APROVADOR HUMANO.

Procedimento: [processes/accept.md](processes/accept.md).

1. **Conferir candidato e roteiro.**
2. **Executar e registrar o observado.**
3. **Decidir o aceite do conjunto.**
