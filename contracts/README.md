# DreamTeam — equipe de agentes do Bezalel

DreamTeam é a equipe de nove agentes do plugin **Bezalel**. Seu fluxo é mantido
neste pacote, sem envio obrigatório a ferramenta externa.

Os agentes definem papéis; o [fluxo](dream-team.md) define processos e
condições; as [skills](dream-team-skills.md) descrevem métodos. O contexto de
arquitetura e negócio pertence ao projeto consumidor em `.bezalel/project.json`.
O [catálogo](catalog.json) relaciona nove agentes e o aprovador humano externo aos
21 processos locais, sem criar um agente por etapa.

## Papéis

| Agente | Processos | Responsabilidade |
|---|---|---|
| [Product Manager](roles/produto.md) | bug, improvement, feature | Qualificar intenção, versionar escopo e registrar destinos nas issues. |
| [Tech Lead](roles/coordenador.md) | plan, bank, review, package, pr, postMerge | Coordenar e revisar; preparar HTML/roteiro, abrir PRs e conferir merge/issues. Não implementa nem testa. |
| [Engenheiro DevOps](roles/infraestrutura.md) | env | Comprovar isolamento e preparar/recuperar o ambiente e encerrá-lo após merge verificado. |
| [Desenvolvedor fullstack](roles/dev-fullstack.md) | fullstack | Investigar, preparar ou implementar uma fatia vertical pequena. |
| [Desenvolvedor backend](roles/backend.md) | backend | Regras, dados, mocks e contratos de serviços. |
| [Desenvolvedor frontend web](roles/frontend-web.md) | web | Telas, estados, acessibilidade e integração web. |
| [Desenvolvedor mobile](roles/mobile.md) | mobile | Plataforma, versões, conectividade e integração nativa. |
| [Engenheiro de QA](roles/qa.md) | ui, qa | UI/UX e validação independente dos critérios e jornadas. |
| [AppSec](roles/appsec.md) | security | Segurança, hipóteses, achados e revalidação do candidato. |

O [APROVADOR HUMANO](actors/aprovador-humano.md) decide produto/escopo, banco,
adiamento elegível de risco e aceite. Não há adaptador que o personifique.
Observação de produção/negócio não integra este pacote de entrega. As definições
futuras sem uso foram removidas; nenhuma coleta foi ativada.

## Carregamento e atribuição

1. Leia o `AGENTS.md` do projeto e sua configuração; consulte os documentos de
   contexto pertinentes à atribuição, preservando instruções obrigatórias.
2. Identifique cenário, issue real e versão; leia R1–R10 do fluxo e o contrato do
   papel. Fonte indisponível não autoriza inventar regra ou procedimento.
3. Quem inicia a conversa indica o modelo apropriado para a demanda e atribuições.
   Aplique a [seleção proporcional de modelos](dream-team.md#seleção-proporcional-de-modelos):
   priorize modelos menores que o inicial e explicite a escolha quando suportada.
4. Receba uma tarefa com objetivo/fase, dono, entrada/versão, entrega e condição de
   conclusão. Carregue o procedimento pertinente e somente as skills necessárias.
5. Aplique a [economia de contexto e coordenação](dream-team.md#economia-de-contexto-e-coordenação):
   entrega completa por fase, fontes pertinentes, provas válidas e comunicação
   por mudança relevante, preservando revisões independentes e testes.
6. Registre resultado/evidência ou bloqueio e retomada na mesma issue, usando o
   [handoff curto](templates/handoff.md). Não crie um MD paralelo por demanda.

O TL seleciona apenas os especialistas necessários e um dev responsável pela
integração inteira. Investigação, preparação de interface/mock e implementação
são fases distintas. Revisor diferente no texto não comprova executor independente:
TL, QA e AppSec não podem revisar sua própria implementação. Ferramenta obrigatória
indisponível mantém pendência. Uma skill não transfere responsabilidade do papel.

A aplicação precisa disponibilizar ferramentas de delegação/coordenação para
executores distintos, ou um operador precisa conduzir as atribuições. Não simule
subagentes mudando o nome do papel numa única execução. Aplicam-se a autorização
da tarefa e as regras do aplicativo; este pacote não inicia uma equipe por si só.

## Adaptadores do Codex e do Claude Code

A pasta `codex/` contém um TOML por agente; `claude/` contém um Markdown por agente,
com nome `dream-team-<id>`, descrição e
instruções de carregamento. São adaptadores curtos dos contratos, sem modelo fixo,
credenciais ou alteração de permissões. Instale-os conforme o
[README principal](../README.md#como-adotar-o-bezalel-em-um-projeto).

Os nomes e caminhos dos adaptadores ficam no catálogo e coincidem entre as duas
plataformas. O fluxo e sua relação de skills usam o prefixo `dream-team`; inventário
e guia de uso manual são documentos gerais do plugin, sem prefixo. Os campos
`workflow` e `id` descrevem o fluxo e identidades locais; não exigem consulta
ou sincronização externa. O plugin e seus comandos manuais continuam usando `bezalel`.

O formato segue a [documentação oficial de agentes](https://learn.chatgpt.com/docs/agent-configuration/subagents):
arquivos por projeto ficam em `.codex/agents/`; permissões e MCPs vêm da sessão
principal. A validação local confere TOML e referências, não certifica o loader
ou cria uma barreira técnica de execução. Confirme descoberta na versão do
aplicativo e faça o piloto no projeto antes de alegar operação validada.

No Claude, o formato segue a [referência de subagentes](https://code.claude.com/docs/en/sub-agents),
com `name`, `description` e instruções; a instalação direta usa `.claude/agents/`.
O pacote nativo separa contratos de prompts descobertos e declara os nove adaptadores
no manifesto. Não existe agente humano, modelo obrigatório ou runtime próprio.

O alvo `grok` da integração direta reutiliza os adaptadores Claude, conforme a
compatibilidade documentada do Grok Build. Não há um terceiro conjunto de papéis
ou IDs. Consulte [adoção e limites](../README.md#grok-build-e-modelos-glm);
validação em fixtures não comprova descoberta nem execução no aplicativo.

O instalador atualiza agentes, skills e referências juntos, preservando o contexto
e as customizações do projeto. O hook não inicia o fluxo; ele reconcilia a versão
adotada. Distribuição e política de atualização estão no README principal.

Para iniciar uma demanda, forneça o cenário e a intenção ao PM; a passagem para
TL e especialistas segue o fluxo. Peça delegação aos agentes pertinentes quando
suportada/autorizada pelo aplicativo. Não use os agentes de entrega para executar
merge, deploy ou as skills reservadas ao uso manual.

## Nomes de branches e ambientes

Use uma descrição curta em minúsculas, sem acentos, separada por hífens, como
`corrigir-login`. Números são permitidos quando têm significado. Não acrescente
prefixos como `codex/` ou `feat/`, identificadores do agente ou sufixos aleatórios.
A criação pela ENV mantém branch, `.worktrees/<nome>` e ambiente com o mesmo nome;
preserve a associação real de ambientes preexistentes. Veja R5 e o processo de
ambiente no [fluxo](dream-team.md#process-env).

## Entrega e encerramento

Concluir validações técnicas abre a PR normal, pronta para revisão e sem draft, com roteiro pronto. Aceite humano vem na PR;
aprovação ou aviso de merge faz o TL consultar o serviço. Somente com todos os
merges confirmados e escopo concluído, fechar/verificar issues existentes e passar
para DevOps o encerramento do ambiente associado à branch registrada. Falha ou
limpeza parcial permanece pendente; não inventar issue, ambiente ou resultado.
Para banco, apresentar HTML com estrutura/diferenças e, após decisão final
registrada, excluir a cópia temporária da tarefa. Ajuste exige nova apresentação.

## Registros e validação

O [contrato de registro](record-contract.md) permite conferir um snapshot local
opcional das declarações da issue, sem criar outra fonte de requisitos. O checker
não executa os comandos do projeto, consulta GitHub ou autentica pessoas.

O teste estrutural cobre catálogo, processos, skills, adaptadores e links. Os testes
sintéticos cobrem interrupção/retomada nos três cenários, candidato alterado,
investigação, HTML/decisão/exclusão, banco/UI, revisões, segurança, PR antes do
aceite e encerramento somente após merge confirmado. Eles não substituem o
piloto com ferramentas reais e decisões humanas reais. Ausência de uma capacidade
é registrada; nenhuma dependência é instalada silenciosamente.
