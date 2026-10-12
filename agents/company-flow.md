# Correspondência com Company Flow

## Fonte e sequência de trabalho

Discuta decisões no desenho visual quando ele facilitar a compreensão. Após uma
mudança acordada, atualize os arquivos versionados: eles são a fonte canônica dos
papéis, responsabilidades e contratos. Atualize o visual correspondente e confira
**os dois sentidos**, sem considerar uma ligação ou teste verde prova de equivalência.
Não há sincronizador nem execução de agentes por este documento.

Mapa: **Fluxo de IA**, Company Flow, ID
`534d1f66-90a5-462d-bf78-29c6ccf9ef94`. Base da alteração: revisão **71**,
atualizada em 09/10/2026 às 21:46:44 UTC. Revisão de nomenclatura em 12/10/2026.
A releitura após escrita confirmou a revisão **97**, em 12/10/2026.

## Papéis, IDs estáveis e responsabilidades

| Nome canônico | ID no catálogo | ID no Company Flow | Contrato |
|---|---|---|---|
| Product Manager | `produto` | `4bb78990-d145-46b4-b911-a49beff62f4b` | [roles/produto.md](roles/produto.md) |
| Tech Lead | `coordenador` | `cc7a23e0-2ac7-432b-91dc-66bbeea85aca` | [roles/coordenador.md](roles/coordenador.md) |
| Engenheiro DevOps | `infraestrutura` | `5b5765f9-16d8-4c3f-aaa6-87259affea50` | [roles/infraestrutura.md](roles/infraestrutura.md) |
| Desenvolvedor fullstack | `dev-fullstack` | `569b69d4-cb29-4283-9e18-4eae9d9ce306` | [roles/dev-fullstack.md](roles/dev-fullstack.md) |
| Desenvolvedor backend | `backend` | `8d6ff12f-df6e-4591-a813-5d13f5eb7949` | [roles/backend.md](roles/backend.md) |
| Desenvolvedor frontend web | `frontend-web` | `8beb1f6e-8ad4-470e-b6fc-cf3dd22b0ea7` | [roles/frontend-web.md](roles/frontend-web.md) |
| Desenvolvedor mobile | `mobile` | `b99885ab-857d-436f-9fd2-6c4bc4f0b5a8` | [roles/mobile.md](roles/mobile.md) |
| Engenheiro de QA | `qa` | `47628627-92df-4d54-9065-82b4a6d9cb25` | [roles/qa.md](roles/qa.md) |
| Analista de Produto | `observador-negocio` | `46220d58-c6cf-4be3-a98c-b13a2e2d2853` | [roles/observador-negocio.md](roles/observador-negocio.md) |

O [APROVADOR HUMANO](actors/aprovador-humano.md), ID visual
`f846e7b0-f729-4ada-b1fa-fee244da6885`, é externo e não conta nos nove agentes.
Mantém os processos “Decidir sobre a proposta de banco” e “Decidir ações de
publicação e operação”; a decisão de produto também permanece com o usuário.

Confiabilidade deixou de ser agente separado. O processo
`10a0341e-4341-4bb0-b438-fb66c45fc3be` pertence ao Engenheiro DevOps;
[seu procedimento](responsibilities/observacao-confiabilidade.md) permanece
**DESATIVADO / somente propositivo**. O processo de observação de negócio
`49776827-f4c1-48b4-a40e-e26e3da176fc` pertence ao Analista de Produto e permanece
no mesmo estado. `catalog.json` e `.bezalel/project.example.json` registram
`enabled: false` separadamente dos nomes; no visual, o estado está no indicador,
na descrição e no procedimento dos processos. Isso não é um interruptor de runtime.

O MCP consultado não oferece arquivamento/consolidação de cargo. O registro antigo
`ea992eda-7b3b-4184-a3f7-55b8a1778754` fica como **Observação de confiabilidade**, sem
processos, apenas referência legada. Não é um décimo agente. A interface ainda
lista esse cadastro adicional; não alegar que o cadastro bruto tem apenas dez
entradas. Sua remoção/consolidação suportada fica pendente, sem exclusão nesta rodada.

IDs de papéis, incluindo `coordenador`, `infraestrutura` e `observador-negocio`, e
seus caminhos existentes permanecem estáveis. O campo `display_name` define a
nomenclatura; não são agentes nativos registrados no Codex. O Analista de Produto
preserva o escopo de observação de negócio; não passa a decidir visão ou prioridade.

## Conferência semântica reutilizável

1. Leia a revisão do mapa antes de escrever e use controle de revisão em cada
   alteração. Preserve mudanças concorrentes; em conflito, releia e reavalie.
2. Para cada processo/decisão, confronte dono, entradas, saídas, condição de avanço,
   bloqueios, retorno de falha, critérios de pronto e handoff com o texto canônico.
3. Faça o inverso: para cada obrigação no texto, localize a etapa, condição ou
   procedimento visual correspondente. Diferencie procedimento textual de aresta.
4. Registre presente, ausente, ambíguo ou divergente; não transforme silêncio em
   aprovação. Compare catálogo geral e cenários entre si, não só os títulos.
5. Releia o mapa após escrever. Confirme identidades, vínculos, decisões humanas,
   estados desativados e preservação das portas/conexões fora do escopo.
6. Quando houver revisão independente, informe quem revisou e o alcance; não
   atribua independência ao próprio autor nem alegue equivalência automática.

O checker verifica nomes/metadados, referências, donos e estados declarados do
catálogo. Não consulta Company Flow e não verifica equivalência semântica.

## Matriz desta revisão

Nomes de etapa abaixo identificam os processos existentes; a alteração desta
rodada só muda nomenclatura, responsabilidade de confiabilidade e estado explícito.

| Etapa/decisão visual | Referência canônica | Resultado / limite |
|---|---|---|
| Definir a história e os critérios | [Product Manager](roles/produto.md), [fluxo §2](workflow.md), [história](templates/user-story.md) | Necessidade, AC, dependências, limites e decisão do usuário preservados. |
| Preparar e comprovar isolamento | [DevOps](roles/infraestrutura.md), [fluxo §1](workflow.md), [registro](record-contract.md) | Cinco dimensões, evidência/não aplicável e bloqueio preservados. |
| Analisar impactos e planejar a entrega | [Tech Lead](roles/coordenador.md), [fluxo §2](workflow.md) | Responsável integrado, contratos e análise de banco preservados. |
| Selecionar somente os desenvolvedores necessários | [Tech Lead](roles/coordenador.md), [guia](README.md) | Seleção proporcional prevista no texto; nó de decisão visual não possui campo de cargo explícito. Dono implícito no planejamento. |
| Preparar proposta estrutural de banco | [fluxo §3](workflow.md), [proposta](templates/database-review.md) | Antes/depois, impacto, alternativas e recuperação preservados. |
| Decidir sobre a proposta de banco | [aprovador](actors/aprovador-humano.md), [registro](record-contract.md) | Aprovação humana da versão exata antes de implementar; revisão retorna à proposta; pendência/recusa bloqueia. |
| Implementar uma entrega vertical | [fullstack](roles/dev-fullstack.md), [fluxo §4](workflow.md) | Pré-condições, escopo, verificações e handoff preservados. |
| Implementar regras e contratos backend | [backend](roles/backend.md) | Autorização, persistência, falhas e compatibilidade preservadas. |
| Implementar e integrar o fluxo web | [web](roles/frontend-web.md) | Estados observáveis, contratos e distinção mock/real preservados. |
| Implementar e validar o fluxo mobile | [mobile](roles/mobile.md) | Versões, conectividade e plataformas não verificadas preservadas; web não certifica comportamento nativo. |
| Validar os critérios de forma independente | [Engenheiro de QA](roles/qa.md), [fluxo §5](workflow.md) | Outra identidade, todos os AC, cenários adicionais e bloqueios preservados. Divergência de retorno de defeitos descrita abaixo. |
| Conferir a integração da história inteira | [Tech Lead](roles/coordenador.md), [fluxo §5](workflow.md) | Dono integrado, evidência, pronto/bloqueado e retorno à análise preservados. |
| Preparar PR e roteiro manual | [fluxo §6](workflow.md), [template](templates/pull-request.md), [registro](record-contract.md) | Artefatos, evidências, limitações e publicação pendente preservados. |
| Decidir ações de publicação e operação | [aprovador](actors/aprovador-humano.md), [fluxo §6](workflow.md) | Escopo humano por ação, sem concessão permanente. |
| Executar e verificar somente o autorizado | [DevOps](roles/infraestrutura.md), [fluxo §6](workflow.md) | Alvos, preservação, resultado real e falhas parciais preservados. |
| Propor investigação de confiabilidade | [responsabilidade DevOps](responsibilities/observacao-confiabilidade.md) | Novo dono explícito; coleta e correção continuam desativadas. |
| Propor investigação de negócio | [Analista de Produto](roles/observador-negocio.md) | Calendário/fuso/janela/tolerância e dado ausente indeterminado preservados; desativado. |

## Divergências preexistentes e propostas ainda não aplicadas

- **Retorno de defeitos:** cenário 01 encaminha QA à análise; conexões gerais vão
  direto aos desenvolvedores. O procedimento de QA fala em devolver ao dev, e o
  texto do Tech Lead admite receber QA. Falta uma regra única de triagem/reteste.
- **Ordem inicial:** o texto apresenta isolamento antes da análise da história;
  o visual explicita definir a história antes de isolar. Os pré-requisitos exigem
  história/alvo em ambos; a separação entre definição e análise merece ser explícita.
- **Seleção de especialistas:** cenário 01 tem decisão dedicada; o catálogo geral
  liga planejamento/aprovação aos quatro caminhos diretamente. O texto já exige
  seleção proporcional. Não interpretar ramificação como obrigação de todos.
- **Pronto da proposta de banco:** o nó de preparação herda um critério global
  do Tech Lead que já exige decisão humana, embora ela seja o próximo nó.
  O procedimento específico exige apresentar a proposta antes da aprovação;
  esclarecer pronto da proposta versus pronto da entrega fica pendente.
- **Demais propostas discutidas:** cenários planejados antes do código; divisão dev
  unidade/integração e QA com E2E crítico real; versão integrada pronta para E2E;
  revalidação de evidências após mudanças; retomada de bloqueios; critérios após
  deploy e recuperação. Continuam propostas, não garantias já implementadas.
- O requisito de não concluir com zero E2E crítico, assim como usar React Native
  em modo web quando suportado, ainda não foi incorporado aos contratos/validador.
  Validação de NFC, permissões e comportamento nativo exige análise própria.
- Não há equivalência executável: texto e mapa não iniciam agentes, autenticam
  aprovações ou impõem gates. Observadores não foram ativados.

## Resultado da leitura após escrita

Releitura real da revisão **97**, em 12/10/2026, e revisão independente por um
segundo agente, somente leitura, concluídas. Foram confrontados os nove contratos,
ator humano, responsabilidade de confiabilidade, workflow, registro e esta matriz
com os 16 processos, a decisão e os três cenários, nos dois sentidos.

- Os nove nomes do catálogo correspondem aos cargos visuais usados pelos agentes;
  APROVADOR HUMANO externo preservado; cadastro legado com zero processos.
- Confiabilidade pertence ao DevOps e negócio ao Analista de Produto, ambas com
  estado desativado separado do nome e sem aumento de acesso/permissão.
- IDs, portas, decisão, 28 conexões gerais e 25 conexões dos cenários preservados.
  Os procedimentos mudaram apenas na nomenclatura/referência e no dono da observação;
  condições de avanço, erro, decisão humana e critérios de pronto não foram alterados.
- O aplicativo normalizou `sidebarOrder` dos processos de isolamento, operação e
  confiabilidade do DevOps de 1/13/14 para 0/1/2; a ordem relativa e coordenadas
  permaneceram iguais. Não houve mudança de percurso.
- A revisão independente não identificou divergência nova de responsabilidade ou
  permissão. As diferenças anteriores listadas acima continuam pendentes; não há
  afirmação de equivalência integral ou executável dos dois modelos.

Validação estrutural local: checker e **25 testes** com fixtures passaram.
Isso confere metadados e contratos declarados, não substitui a revisão semântica
nem demonstra execução, E2E, identidade humana ou eficácia dos gates.
