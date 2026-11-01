# DreamTeam — fluxo de desenvolvimento

Fonte canônica do fluxo de desenvolvimento da [DreamTeam](README.md), equipe de
agentes do plugin Bezalel. São três cenários, 21 processos reutilizáveis e 63
etapas, com 19 processos em cada cenário; os quatro devs são opções de especialidade.
Os contratos em [agents](README.md) distribuem os processos por responsabilidade,
sem criar um agente por etapa. O aprovador humano é externo.

Este arquivo reúne as regras comuns, os percursos dos cenários e o índice dos
processos. Cada papel lê estas regras e somente os [processos](#processos) que o
[catálogo](catalog.json) lhe atribui.

## Regras comuns

Estas regras são a fonte local comum aos três cenários. O fluxo é mantido neste repositório e não exige envio, sincronização ou aprovação em serviço de modelagem. Cada atividade usa as pré-condições do destino, inclusive nas retomadas. Condições locais complementam, sem substituir, o procedimento e estas regras.

### R1 Registro e autorização

Usar a mesma issue, quando existir, como registro da intenção, escopo, decisões e evidências; sem issue, usar a conversa da tarefa e depois a PR. Referências à issue nas etapas seguem essa regra; não criar issue fictícia ou obrigatória apenas para encerrar. Anexos ficam vinculados. Registrar o mínimo antes de qualquer destino. Efeitos externos dependem da autorização concreta da tarefa, aproveitando a já concedida. Ausência de acesso/autorização mantém pendência e rascunho verificável. O mapa documenta responsabilidades; não executa ferramentas, autentica pessoas ou concede permissão.

### R2 Responsabilidade e evidência

TL planeja, coordena e revisa código/evidências; nunca implementa, compõe branches de implementação ou executa testes. Escolhe somente os especialistas necessários e um dev responsável pela integração inteira. Devs executam investigação, preparação, implementação e testes próprios; DevOps cuida do isolamento; QA e AppSec verificam independentemente dos autores. Evidência identifica escopo e candidato: repositórios, base/head, componentes/builds, contratos, dados/schema, dependências e configuração pertinentes. Revisor diferente no texto não comprova executor independente: TL, QA e AppSec não podem revisar sua própria implementação. Executores distintos exigem ferramentas de delegação/coordenação da aplicação ou um operador que conduza as atribuições; não simular subagentes mudando o nome do papel numa única execução.

### Seleção proporcional de modelos

O agente que inicia a conversa avalia a demanda e indica, antes de delegar, o modelo
mais apropriado para a coordenação e para cada atividade prevista, com justificativa
curta. Identifique o modelo inicial quando a aplicação o informar; se desconhecido,
registre essa limitação. A indicação não troca automaticamente o modelo da conversa.

Em toda atribuição, inclusive novas delegações por um recebedor, tente primeiro
selecionar o menor modelo disponível capaz de cumprir a tarefa, priorizando opções
menores que o modelo que iniciou a conversa. Não herde o modelo inicial por
conveniência e não use o modelo mais potente para todos os papéis. Escolha pela
complexidade, incerteza, impacto, contexto e ferramentas necessários, não pelo título
do agente. Leitura delimitada, ajustes simples e verificações objetivas favorecem
modelos menores; raciocínio amplo, diagnóstico difícil ou risco elevado podem
justificar maior capacidade já na seleção, sem exigir uma tentativa inadequada.

Consulte as opções e capacidades expostas pela aplicação na sessão, sem fixar nomes
ou presumir uma ordem de capacidade a partir deles. Passe o modelo escolhido
explicitamente na ferramenta de delegação quando houver suporte. Se a escolha
exigir contexto novo em vez de herança da conversa, forneça objetivo, instruções,
fontes, decisões, versão e critérios suficientes no handoff. Não reduza isolamento,
independência de QA/AppSec, verificações ou critérios de entrega para economizar.

Registre no handoff o modelo inicial conhecido, o recomendado, a razão da escolha e
o modelo efetivo apenas quando confirmado pela ferramenta. Uso do mesmo modelo ou
de um maior exige motivo concreto: capacidade necessária, insuficiência observada
ou ausência de opção menor disponível. Escale quando houver limitação demonstrada,
preservando contexto e provas; reavalie a escolha na próxima atividade, sem manter
a escalada como padrão. Não repita tentativas inadequadas apenas para cumprir a regra.

Sem seleção de modelo na ferramenta, informe a recomendação e a limitação, seguindo
com o modelo disponível quando suficiente e autorizado. Não alegue redução executada,
não invente IDs, nem altere configurações globais ou a conversa por inferência.
Esta política orienta os executores; arquivos e instalação não impõem roteamento
nem comprovam qual modelo foi usado.

### R3 Passagem entre atividades

Cada tarefa informa objetivo/fase, responsável, entrada/versão, entrega esperada e condição de conclusão. Fases dos devs: investigar, preparar interface/mock ou implementar/corrigir. Concluir uma tarefa ou complementar prova não aprova a entrega inteira. Selecionar somente os destinos necessários; saídas não disparam todos os participantes. Provas válidas são reutilizadas; só mudança com impacto exige refazer a cobertura afetada.

### Economia de contexto e coordenação

Aplicar estas regras à passagem R3 em todos os papéis e cenários, mantendo R2 e
R5–R9, a ordem das revisões e as condições de cada etapa:

- **Comunicar por mudança relevante.** Enviar resultado, bloqueio, dúvida necessária
  ou alteração de escopo/versão/dependência que afete outro responsável. Evitar
  confirmações repetidas, pedidos de andamento sem motivo e mensagens que apenas
  repitam estado já registrado. Bloqueios e riscos são comunicados assim que
  identificados; economia não justifica silêncio sobre impedimentos. Preservar as
  atualizações ao usuário exigidas pela aplicação. Preferir notificações de conclusão
  das ferramentas; sem esse suporte, usar espera apropriada à duração prevista e
  consultas pontuais quando necessárias, sem ciclos curtos de consulta/mensagem
  apenas para constatar que nada mudou. Isso não autoriza monitoramento contínuo.
- **Delimitar o contexto de cada atribuição.** Fornecer objetivo/fase, escopo,
  responsável, candidato/base/versão, decisões e restrições aplicáveis, critérios,
  dependências, fontes e evidências relevantes. Preferir referências e trechos
  pertinentes a copiar o histórico integral ou carregar todos os documentos/skills.
  Manter as fontes completas acessíveis; o recebedor consulta o necessário e amplia
  a leitura quando houver ambiguidade, risco ou dependência. Não omitir instruções
  obrigatórias, decisões humanas, achados pendentes ou contratos de integração.
  Se a ferramenta permitir contexto novo, preferi-lo com esse handoff suficiente;
  não alegar isolamento de contexto quando a ferramenta herdar a conversa.
- **Reutilizar provas com validade conferida.** Identificar origem, executor,
  candidato/versão, cobertura e limitações antes de aproveitar evidência existente.
  Conferir diferenças de código, composição, schema, dependências, configuração e
  ambiente pertinentes. Sem impacto, referenciar o resultado válido em vez de
  repetir leitura, teste ou parecer. Mudança material invalida a cobertura afetada;
  dúvida de impacto exige investigação/revalidação, nunca aprovação presumida.
  O revisor independente avalia as fontes e lacunas por conta própria: testes do
  autor não substituem QA/AppSec nem suas verificações obrigatórias. Reutilização
  não dispensa testes exigidos para o candidato nem converte prova parcial em aceite.
- **Delegar uma entrega completa por fase.** Agrupar investigação, preparação,
  implementação/correção ou revisão em uma atribuição com resultado verificável,
  limites, dependências e condição de conclusão. Dentro do escopo autorizado, o
  executor realiza os passos necessários e correções ordinárias sem nova atribuição
  para cada comando, arquivo ou teste. Retorna resultado/evidências ou impedimento;
  esclarecimentos necessários continuam permitidos. Retomadas trazem a diferença,
  o ponto pendente e as provas válidas, sem reiniciar a fase inteira. Não agrupar
  fases para atravessar aprovação pendente, mudar responsabilidades ou eliminar
  revisão independente; mudança de escopo segue PM/humano.

Estas orientações não alteram quantidade de papéis, seleção de modelos, testes,
critérios de entrega ou autorizações. São contratos documentais, sem medição ou
limitação automática de tokens; a economia efetiva precisa ser observada no uso.

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

Cada cenário tem entrada, foco e início próprios; a partir do TL, os três seguem o
[percurso comum](#percurso-comum). A cobertura específica de cada participação fica
nas diferenças por cenário do respectivo processo.

### 1 Bug investigar e entregar a correção

**Entrada:** Relato de possível defeito ou retomada humana, com esperado/observado/evidências a esclarecer.

Foco: separar hipótese, comportamento esperado e defeito; investigar antes de definir a menor correção segura. Diagnóstico suficiente é a investigação obrigatória. Residual de produto fica vinculado; suspeita/achado de segurança precisa de tratamento. Humano decide regra, comportamento esperado e reclassificação. Transferências permitidas: 2 ou 3, iniciadas/verificadas pelo PM na mesma issue.

**Início:** PM qualifica a intenção e resolve decisões de produto necessárias.

### 2 Melhoria delimitar e validar a mudança

**Entrada:** Melhoria de comportamento existente ou transferência humana do bug; benefício e limite a confirmar.

Foco: resultado observável e escopo pequeno, confirmado pelo TL após investigação de comportamento, contratos e dependências. Mudança de regra/escopo precisa de decisão humana; aproveitar o pedido já claro. Se a investigação revelar trabalho de feature, humano decide transferência a 3 e PM inicia/verifica o destino na mesma issue. Roteiro de aceite em Excel .xlsx real.

**Início:** PM qualifica a intenção e resolve decisões de produto necessárias.

### 3 Feature aprovar e entregar o conjunto

**Entrada:** Capacidade nova ou mudança grande, inclusive transferência humana de bug/melhoria; exige visão, histórias e critérios globais.

Foco: principal e histórias curtas vinculadas, critérios individuais/globais, dependências e um dev integrador. Humano aprova o escopo vN; PM confere e entrega a mesma versão ao TL antes da investigação/planejamento técnico. Investigar viabilidade obrigatoriamente e confirmar plano do conjunto. Uma única atividade de QA verifica histórias e depois jornadas globais na feature completa. Roteiro de aceite em Excel .xlsx real.

**Início:** PM registra principal/histórias → humano decide vN → PM entrega ao TL.

### Percurso comum

**Percurso:** início do cenário → TL delimita investigação → DevOps comprova ambiente → devs investigam → TL confirma plano → interface/mock e UI/UX quando pertinentes, banco na ordem definida → devs implementam e integram → TL revisa o conjunto → AppSec analisa → QA valida → TL prepara roteiro → TL abre/verifica PRs e apresenta roteiro → humano avalia → ao aprovar ou avisar merge, TL confere merge/fecha issues aplicáveis → DevOps encerra o ambiente identificado.

**Resultado:** Com implementação: todas as PRs necessárias abertas/verificadas para a branch de produção real, na versão tecnicamente validada, com roteiro e orientação entregues a Rafael. Encerramento posterior exige merge consultado no serviço, issues aplicáveis verificadas e ambiente tratado conforme o processo pós-merge. Sem implementação: destinos documentados pelo PM e estados verificados. Espera/revisão/bloqueio não são conclusão. Merge, deploy e produção permanecem manuais.

## Processos

Os identificadores curtos organizam a correspondência documental; não são um runtime. As entradas de retorno recebem contexto, fase/objeto, versão e origem. Cada processo tem uma entrada de retorno; os três processos PM também têm entrada inicial. As saídas de cada processo são exclusivas/selecionadas conforme a condição, exceto tarefas independentes explicitamente atribuídas a mais de um dev.

Cada processo fica em [`processes/<referência>.md`](processes/), com etapas, saídas, condições locais
e diferenças por cenário. O [índice de processos](#índice-de-processos) relaciona
responsáveis, etapas e skills para consulta.

## Fonte e manutenção

Este documento, os processos em `processes/`, o catálogo e os contratos dos papéis
são as fontes do fluxo.
Mantenha cenários, etapas, decisões, condições e referências coerentes entre os
arquivos. IDs existentes permanecem estáveis; não é necessário enviar propostas
ou sincronizar o fluxo com um serviço externo. O índice abaixo e os adaptadores
dos agentes são gerados por `scripts/dream_team.py`; altere o processo, o contrato,
o catálogo ou o template e regenere. O checker confere estrutura, vínculos e
arquivos gerados, sem provar equivalência semântica, decisão humana ou execução real.

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
3. **Conferir até o handoff e orientar Rafael.** Skills: humanizer.

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
