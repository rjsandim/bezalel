# Skills e procedimentos por etapa do fluxo Bezalel v2

As **18 skills estão presentes no Bezalel**. Destas, **11 orientam métodos em 24 das 60 etapas**, distribuídas por 16 dos 20 processos. As demais etapas mantêm pré-condições, encaminhamentos e decisões, reutilizando o resultado do método já aplicado. Os quatro processos humanos não recebem execução por skill.

O fluxo define o que entregar, quem responde, quando avançar e como retomar. A skill reúne o procedimento técnico. Uma mesma auditoria/plano pode atravessar várias etapas sem ser reiniciada. As descrições atuais estão na [fonte canônica](company-flow-v2.md); o [inventário](company-flow-skills-inventario.md) registra todas as origens e decisões.

## Como aplicar

Use a [orientação comum](company-flow-v2.md#seleção-de-skills-nas-etapas) e as
condições da etapa. A tabela abaixo é um índice; o procedimento vigente fica no
fluxo e o método na skill. Os [contratos de agentes](README.md) definem os limites
do executor. As cinco skills manuais, vps-deploy e limpar-orbstack ficam fora do fluxo.

## O que fica no procedimento da skill

| Skill | Procedimento aproveitado | Responsabilidade que permanece no fluxo |
|---|---|---|
| [iss-audit](../skills/iss-audit/SKILL.md) | Separar fatos/hipóteses; investigar, reproduzir e refutar causas no modo dev. | PM qualifica; dev investiga depois do isolamento; humano decide regra/escopo. |
| [verification-planning](../skills/verification-planning/SKILL.md) | Escolher provas por afirmação/risco, custo e validade; reutilizar o plano existente. | Donos da execução, independência QA e critérios obrigatórios. |
| [env](../skills/env/SKILL.md) | Avaliar e operar ambiente conforme manifesto, contexto e referências de pools. | Autorização, prova das dimensões de isolamento e retorno ao TL. |
| [clean-code](../skills/clean-code/SKILL.md) | Clareza, simplificação, contratos e correção do código tocado. | Escopo autorizado e distinção entre dev que altera e TL que revisa. |
| [clean-architecture](../skills/clean-architecture/SKILL.md) | Analisar responsabilidades/fronteiras e orientar a menor mudança pertinente. | Regras do projeto, aprovação de banco e integração dos consumidores reais. |
| [implementar-snapshots](../skills/implementar-snapshots/SKILL.md) | Implementar a funcionalidade com seleção, sanitização, proteção e verificação. | Só usar nessa tarefa específica; não é autorização de restore ou leitura de produção. |
| [agent-browser](../skills/agent-browser/SKILL.md) | Interagir com a interface web conforme o guia da versão disponível. | Critérios e registro de evidência; mock, integração real, acessibilidade e mobile nativo continuam distintos. |
| [pr-audit](../skills/pr-audit/SKILL.md) | Fixar candidato, confrontar alegações/diff/provas e fechar um parecer. | TL sem executar testes/correções; candidatos incompletos não seguem a AppSec. |
| [security-audit](../skills/security-audit/SKILL.md) | Modelo de ameaças, checklist, inspeção, validação adversarial e parecer. | Limites de acesso, correção pelo dev, tratamento de riscos e decisão humana conforme R8. |
| [development-test-workbook](../skills/development-test-workbook/SKILL.md) | Derivar casos, gerar e conferir o .xlsx pelo contrato da pasta. | Mesmo candidato; Excel obrigatório em melhoria/feature; execução humana ainda pendente. |
| [humanizer](../skills/humanizer/SKILL.md) | Revisar redação quando necessário, preservando o conteúdo. | Critérios, fatos, decisões e registros de execução não são reescritos. |

Não foi transferida para uma skill genérica a revisão de banco/DB Reviewer, a avaliação completa de acessibilidade/mobile, a integração final, o aceite ou a abertura de PR. Essas atividades precisam de regras, ferramentas ou decisões que as skills atuais não cobrem integralmente.

## Relação dos processos

| Processo | Skills pertinentes | Etapas com método indicado |
|---|---|---|
| Qualificar e conduzir o bug · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [humanizer](../skills/humanizer/SKILL.md) | 2 — Definir a necessidade |
| Qualificar e conduzir a melhoria · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [humanizer](../skills/humanizer/SKILL.md) | 2 — Definir resultado e limites |
| Definir e conduzir o escopo da feature · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [humanizer](../skills/humanizer/SKILL.md) | 1 — Registrar visão e histórias |
| Decidir regra ou escopo · v2 | Nenhuma | Decisão/execução humana. |
| Coordenar a entrega · v2 | [verification-planning](../skills/verification-planning/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md) | 2 — Definir o próximo resultado e suas condições |
| Preparar ou recuperar o ambiente · v2 | [env](../skills/env/SKILL.md) | 1 — Conferir alvos e autorização; 2 — Preparar e comprovar isolamento |
| Executar contribuição fullstack · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [clean-code](../skills/clean-code/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md), [implementar-snapshots](../skills/implementar-snapshots/SKILL.md), [agent-browser](../skills/agent-browser/SKILL.md) | 2 — Executar a fase atribuída |
| Executar contribuição backend · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [clean-code](../skills/clean-code/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md), [implementar-snapshots](../skills/implementar-snapshots/SKILL.md) | 2 — Executar a fase atribuída |
| Executar contribuição web · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [clean-code](../skills/clean-code/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md), [agent-browser](../skills/agent-browser/SKILL.md) | 2 — Executar a fase atribuída |
| Executar contribuição mobile · v2 | [iss-audit](../skills/iss-audit/SKILL.md), [clean-code](../skills/clean-code/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md) | 2 — Executar a fase atribuída |
| Preparar a proposta de banco · v2 | [clean-architecture](../skills/clean-architecture/SKILL.md), [verification-planning](../skills/verification-planning/SKILL.md) | 2 — Preparar a alternativa revisável |
| Decidir a proposta de banco · v2 | Nenhuma | Decisão/execução humana. |
| Revisar interface e contrato · v2 | [agent-browser](../skills/agent-browser/SKILL.md) | 2 — Exercitar as jornadas previstas |
| Revisar a entrega integrada · v2 | [pr-audit](../skills/pr-audit/SKILL.md), [clean-code](../skills/clean-code/SKILL.md), [clean-architecture](../skills/clean-architecture/SKILL.md) | 1 — Conferir o candidato completo; 2 — Revisar código e contratos; 3 — Entregar conclusão identificada |
| Analisar ou revalidar segurança · v2 | [security-audit](../skills/security-audit/SKILL.md) | 1 — Definir objeto e cobertura; 2 — Examinar e validar hipóteses; 3 — Concluir parecer ou tratamento |
| Decidir adiamento de risco · v2 | Nenhuma | Decisão/execução humana. |
| Validar critérios e jornadas · v2 | [verification-planning](../skills/verification-planning/SKILL.md), [agent-browser](../skills/agent-browser/SKILL.md) | 1 — Conferir versão e cobertura necessária; 2 — Executar critérios e jornadas |
| Preparar o aceite humano · v2 | [development-test-workbook](../skills/development-test-workbook/SKILL.md), [humanizer](../skills/humanizer/SKILL.md) | 2 — Preparar roteiro e acesso; 3 — Apresentar o pacote |
| Executar roteiro e decidir aceite · v2 | Nenhuma | Decisão/execução humana. |
| Abrir PRs e entregar próximos passos · v2 | [humanizer](../skills/humanizer/SKILL.md) | 2 — Abrir e verificar as PRs reais; 3 — Conferir até o handoff e orientar Rafael |

Os passos sem skill específica fazem controle do fluxo, decisão humana ou reaproveitam
resultados válidos. Ao mudar uma indicação, alinhe fluxo, esta relação e catálogo;
o checker confere a cobertura por processo, não a qualidade semântica da seleção.
