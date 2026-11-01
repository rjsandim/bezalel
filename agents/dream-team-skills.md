# Skills e procedimentos por etapa do fluxo da DreamTeam

As **18 skills estão presentes no Bezalel**. Destas, **11 orientam métodos em 24 das 63 etapas**, distribuídas por 16 dos 21 processos. As demais etapas mantêm pré-condições, encaminhamentos e decisões, reutilizando o resultado do método já aplicado. Os quatro processos humanos não recebem execução por skill.

O fluxo define o que entregar, quem responde, quando avançar e como retomar. A skill reúne o procedimento técnico. Uma mesma auditoria/plano pode atravessar várias etapas sem ser reiniciada. As descrições atuais estão nos [processos do fluxo](dream-team.md#processos); o [inventário](skills-inventario.md) registra todas as origens e decisões.

## Como aplicar

Use a [orientação comum](dream-team.md#seleção-de-skills-nas-etapas) e as
condições da etapa. A tabela abaixo é um índice; o procedimento vigente fica no
fluxo e o método na skill. Os [contratos de agentes](README.md) definem os limites
do executor. As cinco skills manuais, vps-deploy e limpar-orbstack ficam fora do fluxo.

## O que fica no procedimento da skill

| Skill | Procedimento aproveitado | Responsabilidade que permanece no fluxo |
|---|---|---|
| [iss-audit](../skills/iss-audit/SKILL.md) | Separar fatos/hipóteses; investigar, reproduzir e refutar causas no modo dev. | PM qualifica; dev investiga depois do isolamento; humano decide regra/escopo. |
| [verification-planning](../skills/verification-planning/SKILL.md) | Escolher provas por afirmação/risco, custo e validade; reutilizar o plano existente. | Donos da execução, independência QA e critérios obrigatórios. |
| [env](../skills/env/SKILL.md) | Avaliar e operar ambiente conforme manifesto, contexto e referências de pools. | Isolamento durante o trabalho; após merge/issue, preservação e destroy do alvo registrado, com resultado e retorno ao TL. |
| [clean-code](../skills/clean-code/SKILL.md) | Clareza, simplificação, contratos e correção do código tocado. | Escopo autorizado e distinção entre dev que altera e TL que revisa. |
| [clean-architecture](../skills/clean-architecture/SKILL.md) | Analisar responsabilidades/fronteiras e orientar a menor mudança pertinente. | Regras do projeto, aprovação de banco e integração dos consumidores reais. |
| [implementar-snapshots](../skills/implementar-snapshots/SKILL.md) | Implementar a funcionalidade com seleção, sanitização, proteção e verificação. | Só usar nessa tarefa específica; não é autorização de restore ou leitura de produção. |
| [agent-browser](../skills/agent-browser/SKILL.md) | Interagir com a interface web conforme o guia da versão disponível. | Critérios e registro de evidência; mock, integração real, acessibilidade e mobile nativo continuam distintos. |
| [pr-audit](../skills/pr-audit/SKILL.md) | Fixar candidato, confrontar alegações/diff/provas e fechar um parecer. | TL sem executar testes/correções; candidatos incompletos não seguem a AppSec. |
| [security-audit](../skills/security-audit/SKILL.md) | Modelo de ameaças, checklist, inspeção, validação adversarial e parecer. | Limites de acesso, correção pelo dev, tratamento de riscos e decisão humana conforme R8. |
| [development-test-workbook](../skills/development-test-workbook/SKILL.md) | Derivar casos, gerar e conferir o .xlsx pelo contrato da pasta. | Mesmo candidato; Excel obrigatório em melhoria/feature; execução humana ainda pendente. |
| [humanizer](../skills/humanizer/SKILL.md) | Revisar redação quando necessário, preservando o conteúdo. | Critérios, fatos, decisões e registros de execução não são reescritos. |

Não foi transferida para uma skill genérica a decisão humana de banco, a avaliação completa de acessibilidade/mobile, a integração final, o aceite ou a abertura de PR. Essas atividades precisam de regras, ferramentas ou decisões que as skills atuais não cobrem integralmente.

## Relação dos processos

A relação de skills por processo e etapa fica no [índice de processos](dream-team.md#índice-de-processos),
gerado a partir dos arquivos de processo; cada arquivo traz o procedimento completo.

Os passos sem skill específica fazem controle do fluxo, decisão humana ou reaproveitam
resultados válidos. Ao mudar uma indicação, alinhe o processo, esta tabela e o
catálogo e regenere o índice; o checker confere a cobertura por processo, não a
qualidade semântica da seleção.

O processo **Conferir merge e encerrar a tarefa** não executa uma skill própria: TL consulta PRs e issues e passa ao DevOps a limpeza pelo processo de ambiente. O HTML de banco é temporário; a decisão e o resumo sobrevivem à exclusão.
