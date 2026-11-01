# Skills e procedimentos por etapa do fluxo da DreamTeam

As **20 skills estão presentes no Bezalel**. Destas, **13 orientam métodos em 24 das 63 etapas**, distribuídas por 16 dos 21 processos. As demais etapas mantêm pré-condições, encaminhamentos e decisões, reutilizando o resultado do método já aplicado. Os quatro processos humanos não recebem execução por skill.

O fluxo define o que entregar, quem responde, quando avançar e como retomar. A skill reúne o procedimento técnico. Uma mesma auditoria/plano pode atravessar várias etapas sem ser reiniciada. As descrições atuais estão nos [processos do fluxo](dream-team.md#processos); o [inventário](skills-inventario.md) registra todas as origens e decisões.

## Como aplicar

As etapas indicam objetivo, responsável, condição e entrega; o método fica na skill indicada, em skills/<nome>/SKILL.md do Bezalel, com suas referências. Aplicar somente o modo/fase pertinente. Uma aplicação pode atender várias etapas do mesmo trabalho: não reiniciar auditoria, plano ou redação a cada passagem; reutilizar artefatos/provas ainda válidos. Apoios condicionais só entram quando úteis. Skill não cria agente, gate, autorização ou transferência de responsabilidade. Se indisponível, registrar o limite e usar procedimento equivalente disponível; prova/ferramenta obrigatória ausente segue [R4](dream-team.md#r4-interrupção-e-retomada).
iss-audit: qualificação PM ou investigação dev, conforme fase. pr-audit: revisão TL sem editar/testar. clean-code inclui simplificação; clean-architecture aplica-se a fronteiras afetadas. implementar-snapshots só para construir/corrigir a funcionalidade. verification-planning orienta provas proporcionais; TL planeja/confere e executores produzem evidência. Pesquisa dependente de @librarian indisponível fica registrada, sem inventar agente ou conclusão; infraestrutura de verificação depende da autorização própria.
agent-browser exige CLI/guia da versão e alvo isolado autorizado; não instalar por inferência. MCP continua preferido para operações do serviço. Browser apoia a prova da interface, sem substituir regressão automatizada, acessibilidade completa, serviços/persistência ou mobile nativo. humanizer é opcional na redação antes da submissão/publicação; não muda fatos, critérios, respostas, resultados ou decisões versionadas.
security-audit fica em auditoria/validação: correção de produto volta a TL/dev; não ampliar credenciais, remover GITHUB_TOKEN, alterar/encerrar alertas ou cancelar CI por esta indicação. Cópias originais permanecem intactas; pr-audit e iss-audit usam variantes autorizadas. Skills reservadas ao uso manual e candidatas pendentes no inventário ficam fora das etapas; nenhuma é disparada ao concluir PR/auditoria.

O [inventário completo](skills-inventario.md) registra origem, cópias e adaptações pendentes. As adaptações autorizadas de pr-audit e iss-audit estão identificadas; as demais cópias preservam o conteúdo original. Os agentes referenciam essas skills sem duplicar seus procedimentos.

Aplique também as condições da etapa. A tabela abaixo é um índice; o procedimento vigente fica no
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
| [depurar-bug](../skills/depurar-bug/SKILL.md) | Reproduzir, provar a causa, escrever o teste que falha e aplicar a menor correção. | Dev corrige na fase autorizada; decisão de produto/banco volta ao TL; revisão independente continua com TL, QA e AppSec. |
| [proposta-banco](../skills/proposta-banco/SKILL.md) | Montar o HTML antes/depois por entidade a partir do schema real, com riscos e reversão, apresentar e fechar após a decisão. | TL prepara; o humano decide toda migration, inclusive pequena ou só de dados; implementação dependente só depois da aprovação da versão exata. |
| [implementar-snapshots](../skills/implementar-snapshots/SKILL.md) | Implementar a funcionalidade com seleção, sanitização, proteção e verificação. | Só usar nessa tarefa específica; não é autorização de restore ou leitura de produção. |
| [agent-browser](../skills/agent-browser/SKILL.md) | Interagir com a interface web conforme o guia da versão disponível. | Critérios e registro de evidência; mock, integração real, acessibilidade e mobile nativo continuam distintos. |
| [pr-audit](../skills/pr-audit/SKILL.md) | Fixar candidato, confrontar alegações/diff/provas e fechar um parecer. | TL sem executar testes/correções; candidatos incompletos não seguem a AppSec. |
| [security-audit](../skills/security-audit/SKILL.md) | Modelo de ameaças, checklist, inspeção, validação adversarial e parecer. | Limites de acesso, correção pelo dev, tratamento de riscos e decisão humana conforme R8. |
| [development-test-workbook](../skills/development-test-workbook/SKILL.md) | Derivar casos, gerar e conferir o .xlsx pelo contrato da pasta. | Mesmo candidato; Excel na feature ou quando a classe pedir; execução humana ainda pendente. |
| [humanizer](../skills/humanizer/SKILL.md) | Revisar redação quando necessário, preservando o conteúdo. | Critérios, fatos, decisões e registros de execução não são reescritos. |

A proposta-banco prepara e apresenta a mudança de banco, mas não transfere a uma skill a decisão humana de banco, a avaliação completa de acessibilidade/mobile, a integração final, o aceite ou a abertura de PR. Essas atividades precisam de regras, ferramentas ou decisões que as skills atuais não cobrem integralmente.

## Relação dos processos

A relação de skills por processo e etapa fica no [índice de processos](dream-team.md#índice-de-processos),
gerado a partir dos arquivos de processo; cada arquivo traz o procedimento completo.

Os passos sem skill específica fazem controle do fluxo, decisão humana ou reaproveitam
resultados válidos. Ao mudar uma indicação, alinhe o processo, esta tabela e o
catálogo e regenere o índice; o checker confere a cobertura por processo, não a
qualidade semântica da seleção.

O processo **Conferir merge e encerrar a tarefa** não executa uma skill própria: TL consulta PRs e issues e passa ao DevOps a limpeza pelo processo de ambiente. O HTML de banco é temporário; a decisão e o resumo sobrevivem à exclusão.
