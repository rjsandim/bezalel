# DreamTeam — equipe de agentes do Bezalel

DreamTeam é a equipe de nove agentes que atua no fluxo de desenvolvimento
**Bezalel v2**. Company Flow é a ferramenta usada para representar o fluxo visualmente.

Os agentes definem papéis; o [fluxo](bezalel-v2.md) define processos e
condições; as [skills](bezalel-v2-skills.md) descrevem métodos. O contexto de
arquitetura e negócio pertence ao projeto consumidor em `.bezalel/project.json`.
O [catálogo](catalog.json) relaciona nove agentes e o aprovador humano externo aos
20 processos da revisão 1179, sem criar um agente por etapa.

## Papéis

| Agente | Processos | Responsabilidade |
|---|---|---|
| [Product Manager](roles/produto.md) | bug, improvement, feature | Qualificar intenção, versionar escopo e registrar destinos nas issues. |
| [Tech Lead](roles/coordenador.md) | plan, bank, review, package, pr | Coordenar e revisar; preparar proposta/aceite e entregar PRs. Não implementa nem testa. |
| [Engenheiro DevOps](roles/infraestrutura.md) | env | Comprovar isolamento e preparar/recuperar o ambiente autorizado. |
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

1. Leia o `AGENTS.md` do projeto, sua configuração e os documentos de contexto.
2. Identifique cenário, issue real e versão; leia R1–R10 do fluxo e o contrato do
   papel. Fonte indisponível não autoriza inventar regra ou procedimento.
3. Receba uma tarefa com objetivo/fase, dono, entrada/versão, entrega e condição de
   conclusão. Carregue o procedimento pertinente e somente as skills necessárias.
4. Registre resultado/evidência ou bloqueio e retomada na mesma issue, usando o
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
com nome `bezalel-<id>`, descrição e
instruções de carregamento. São adaptadores curtos dos contratos, sem modelo fixo,
credenciais ou alteração de permissões. Instale-os conforme o
[README principal](../README.md#como-adotar-o-bezalel-em-um-projeto).

Os agentes usam o namespace técnico `bezalel-<id>` do pacote. Os documentos do fluxo
usam o prefixo `bezalel-`; seus caminhos ficam no catálogo. Os campos `company_flow` e
`company_flow_role_id` do catálogo mantêm a correspondência com a ferramenta
visual; a nomenclatura do fluxo é Bezalel e a da equipe é DreamTeam.

O formato segue a [documentação oficial de agentes](https://learn.chatgpt.com/docs/agent-configuration/subagents):
arquivos por projeto ficam em `.codex/agents/`; permissões e MCPs vêm da sessão
principal. A validação local confere TOML e referências, não certifica o loader
ou cria uma barreira técnica de execução. Confirme descoberta na versão do
aplicativo e faça o piloto no projeto antes de alegar operação validada.

No Claude, o formato segue a [referência de subagentes](https://code.claude.com/docs/en/sub-agents),
com `name`, `description` e instruções; a instalação direta usa `.claude/agents/`.
O pacote nativo separa contratos de prompts descobertos e declara os nove adaptadores
no manifesto. Não existe agente humano, modelo obrigatório ou runtime próprio.

O instalador atualiza agentes, skills e referências juntos, preservando o contexto
e as customizações do projeto. O hook não inicia o fluxo; ele reconcilia a versão
adotada. Distribuição e política de atualização estão no README principal.

Para iniciar uma demanda, forneça o cenário e a intenção ao PM; a passagem para
TL e especialistas segue o fluxo. Peça delegação aos agentes pertinentes quando
suportada/autorizada pelo aplicativo. Não use os agentes de entrega para executar
merge, deploy ou as skills reservadas ao uso manual.

## Registros e validação

O [contrato de registro v2](record-contract.md) permite conferir um snapshot local
opcional das declarações da issue, sem criar outra fonte de requisitos. O checker
não executa os comandos do projeto, consulta GitHub ou autentica pessoas.

O teste estrutural cobre catálogo, processos, skills, adaptadores e links. Os testes
sintéticos cobrem interrupção/retomada nos três cenários, candidato alterado,
investigação, banco/UI, revisões, segurança, aceite e PRs. Eles não substituem o
piloto com ferramentas reais e decisões humanas reais. Ausência de uma capacidade
é registrada; nenhuma dependência é instalada silenciosamente.
