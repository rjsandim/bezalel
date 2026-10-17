# Inventário de skills para o fluxo Bezalel v2

Inventário solicitado em 16/10/2026, limitado às skills do Bezalel e ao
[repositório akitaonrails/my-skills](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a).
A base inicial tinha **8 pacotes locais e 23 externos**, com security-audit em ambos:
**30 skills distintas examinadas**. Após as duas rodadas autorizadas, o Bezalel
contém **18 pacotes**: **11 indicados condicionalmente na v2**, cinco novas skills
somente manuais e os dois procedimentos operacionais anteriores fora do fluxo.

O repositório completo foi baixado em `.local-review/skill-sources/my-skills-20261016/`,
na revisão `7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a`. O diretório é local e ignorado.
Os originais do clone permanecem intactos. Esta é uma fotografia da seleção,
não um mecanismo de atualização automática nem certificação de execução.

## Skills que já estavam no Bezalel

| Skill | Finalidade | Indicação |
|---|---|---|
| [clean-code](../skills/clean-code/SKILL.md) | Revisão e correção do código alterado, com verificações proporcionais. | Selecionada para devs e revisão TL; no TL, somente análise sem edição. |
| [clean-architecture](../skills/clean-architecture/SKILL.md) | Responsabilidades, fronteiras, dependências e contratos. | Selecionada quando houver impacto arquitetural; apoio à proposta de banco sem substituir o DB Reviewer. |
| [env](../skills/env/SKILL.md) | Ambientes locais com worktree, Docker e isolamento por projeto. | Selecionada no DevOps, preservando manifesto, contexto explícito e autorizações. |
| [development-test-workbook](../skills/development-test-workbook/SKILL.md) | Roteiro manual em Excel com dados, evidências e backlog. | Selecionada no pacote de aceite: obrigatória para produzir o .xlsx dos cenários 2/3; opcional no bug. |
| [implementar-snapshots](../skills/implementar-snapshots/SKILL.md) | Construir/corrigir funcionalidade de snapshots full/tiny. | Selecionada condicionalmente para backend/fullstack quando essa funcionalidade for a tarefa; não é ferramenta de restore avulso. |
| [security-audit](../skills/security-audit/SKILL.md) | Modelo de ameaças, auditoria e verificação adversarial. | Já importada da mesma revisão externa; selecionada no AppSec com os limites de responsabilidade e acesso da v2. |
| [vps-deploy](../skills/vps-deploy/SKILL.md) | Operação e diagnóstico de VPS/Coolify por projeto. | Fora da execução dos três cenários: eles terminam na entrega da PR. Operação remota depende de outra tarefa autorizada. |
| [limpar-orbstack](../skills/limpar-orbstack/SKILL.md) | Auditoria e remoção de ambientes concluídos. | Fora da execução dos três cenários: abrir PR não prova integração nem autoriza limpeza. |

## Todas as skills do repositório externo

“Não incorporada” significa preservada apenas no clone de referência. Conteúdo original e variantes autorizadas estão diferenciados abaixo.

| Skill de origem | Finalidade | Decisão | Motivo ou condição |
|---|---|---|---|
| [agent-browser](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/agent-browser/SKILL.md) | Automação web/Electron e exploração de interfaces. | Copiada sem alterações; indicação condicional. | Reprodução/exploração web nos devs fullstack/web, UI/UX e QA/E2E. Exige CLI e guias dinâmicos disponíveis; não foi encontrado no PATH local. MCP continua preferido para operações do serviço; navegador serve à prova da interface. |
| [blog-cost-charts](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/blog-cost-charts/SKILL.md) | Gráficos de custo/desempenho para blog bilíngue. | Fora do escopo. | Acoplada ao blog Hugo, ao bucket do autor e à leitura de segredos do shell; não resolve etapa de entrega de software da v2. |
| [clonedeps](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/clonedeps/SKILL.md) | Inspecionar código-fonte de dependências relevantes. | Candidata a adaptação; não incorporada. | Útil na investigação, mas exige @librarian, estado .slim e alterações em AGENTS/.ignore; a adaptação proposta está abaixo. |
| [codemap](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/codemap/SKILL.md) | Mapeamento hierárquico de repositório desconhecido. | Candidata a adaptação; não incorporada. | Caminho fixo do OpenCode, agentes fixer, mapas por pasta e hashes persistentes. Não convém impor esse custo a toda investigação. |
| [deepwork](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/deepwork/SKILL.md) | Orquestração de trabalhos grandes em fases. | Não selecionada. | Define outro protocolo de agentes, estado local, gates e commits; concorreria com a coordenação já desenhada na v2. |
| [effect](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/effect/SKILL.md) | Desenvolvimento com Effect v4/effect-smol. | Específica de outro contexto. | Pressupõe esse stack, diretórios e helpers de teste do OpenCode. Só reavaliar para um projeto que realmente os use; não instalar o stack por causa da skill. |
| [fact-check](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/fact-check/SKILL.md) | Verificação factual de artigos em duas passagens. | Fora do escopo. | Voltada a textos editoriais, com CLIs/modelos de terceiros e fanout de verificadores; não substitui análise de requisitos, QA ou auditoria de código. |
| [github-resolution](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/github-resolution/SKILL.md) | Executar correções e resolver tickets auditados. | Copiada; somente chamada manual. | Fora do fluxo Bezalel. Preservado o conteúdo; metadado de invocação explícita acrescentado. Conferir aprovação real e compatibilidade com as auditorias adaptadas; ver guia manual. |
| [humanizer](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/humanizer/SKILL.md) | Revisar redação preservando conteúdo e voz. | Copiada integralmente; selecionada. | Modo incorporado serve para histórias, descrição de PR e instruções ao humano. Opcional; não decide requisitos, valida fatos ou reescreve decisões já submetidas. |
| [improve-codebase-architecture](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/improve-codebase-architecture/SKILL.md) | Encontrar módulos rasos e oportunidades de aprofundamento. | Candidata a adaptação; não incorporada. | Pressupõe CONTEXT.md/ADRs e agente Explore; contém links para grill-with-docs ausente deste repositório. Nossa clean-architecture já cobre a revisão corrente. |
| [iss-audit](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/iss-audit/SKILL.md) | Verificar relatos, reprodução, causa e adequação de issues. | Copiada e adaptada com autorização; selecionada. | Qualificação PM separada da investigação dev. Preserva evidência/refutação e retira resolução/merge obrigatórios, acesso amplo e decisões automáticas de produto. |
| [loop-engineering](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/loop-engineering/SKILL.md) | Entrevista e monitoramento de loops de execução. | Não selecionada. | Depende de runtime, callbacks e agentes externos concretos; não é um procedimento portátil para este refinamento documental. |
| [post-refactor](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/post-refactor/SKILL.md) | Revisar regressões e qualidade após refatorações. | Não selecionada nesta rodada. | Há sobreposição com clean-code, clean-architecture e QA; também encaminha a especialistas @explorer/@oracle/@fixer/@designer. Reavaliar se houver lacuna concreta. |
| [pr-audit](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/pr-audit/SKILL.md) | Auditar alegações, código e segurança de PRs. | Copiada e adaptada com autorização; selecionada. | Revisão TL do candidato integrado, antes ou depois da PR, sem editar/testar/mesclar. Preserva conferência de alegações, fronteiras, consumidores, regressões e validade de provas. |
| [pr-bump](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/pr-bump/SKILL.md) | Consolidar atualizações de dependências de bots. | Copiada; somente chamada manual. | Fora do fluxo Bezalel. Conteúdo original com exemplos Rails/Bundler e metadado explícito; confirmar stack e autorização antes de uso. |
| [pr-post-audit](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/pr-post-audit/SKILL.md) | Auditar a composição após merges. | Copiada como apoio manual autorizado. | Dependência de release e github-resolution em certos casos. Fora das etapas dos três cenários; conteúdo original e interface preservados, política explícita acrescentada. |
| [reflect](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/reflect/SKILL.md) | Analisar fricções recorrentes e sugerir melhorias. | Copiada; somente chamada manual. | Fora do fluxo Bezalel. Conteúdo original e metadado explícito; avaliar padrões somente quando solicitado, sem criar agentes por inferência. |
| [release](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/release/SKILL.md) | Versionar, publicar e verificar releases. | Copiada; somente chamada manual. | Fora do fluxo Bezalel. Conteúdo original e metadado explícito; publicação/CI/limpeza dependem do pedido e regras do projeto. |
| [release-smoke-test](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/release-smoke-test/SKILL.md) | Testar artefato do oh-my-opencode-slim. | Específica de outro produto. | Empacota plugin, configura OpenCode/modelos e usa diretórios temporários próprios; não é um smoke test genérico dos projetos do Bezalel. |
| [security-audit](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/security-audit/SKILL.md) | Auditoria de segurança por evidência. | Reutilizada da cópia existente. | Não houve recópia/atualização. O conteúdo já coincide com a revisão externa; limites de uso da v2 e diferenças preexistentes estão abaixo. |
| [simplify](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/simplify/SKILL.md) | Simplificar código preservando comportamento. | Não incorporada; mantida clean-code. | Comparação concluída e recomendação comunicada antes: clean-code já cobre simplificação, comportamento e escopo, além de erros, contratos e concorrência. Evita duplicar a mesma passagem. |
| [verification-planning](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/verification-planning/SKILL.md) | Planejar um caminho de evidências por afirmação e risco. | Copiada integralmente; selecionada com condição. | Usar quando as capacidades/caminho são conhecidos pelo projeto. Se depender do @librarian citado no original e ele não existir, registrar a limitação; não criar um agente para satisfazê-la. |
| [worktrees](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/worktrees/SKILL.md) | Orquestrar trabalho paralelo por worktrees OMO. | Não selecionada. | Sobrepõe ENV e define outros caminhos, donos, confirmações e integração pelo orquestrador. Manter ENV e o dev integrador da v2. |

## Cópias realizadas e preservação

Na primeira rodada, humanizer (9 arquivos) e verification-planning (1 arquivo)
foram copiadas integralmente; as oito anteriores ficaram intactas. Na segunda,
foram acrescentadas **oito pastas**:

- **agent-browser:** original integral, sem instalar seu CLI.
- **pr-audit e iss-audit:** cópias adaptadas com autorização explícita; entrada
  em português, referências próprias e interface coerente.
- **release, reflect, github-resolution e pr-bump:** SKILL.md original; somente
  adaptador de interface/invocação explícita acrescentado.
- **pr-post-audit:** cópia adicional autorizada como dependência manual; SKILL.md
  e interface originais, com política de invocação explícita acrescentada.

As dez pastas que já existiam antes da segunda rodada foram preservadas em
conteúdo e modo de arquivo. A security-audit tem duas diferenças preexistentes
ante a origem: .DS_Store ignorado e scripts/security-surface.sh sem bit de execução
(0644 local, 0755 na origem). Seu conteúdo coincide; o procedimento o chama por bash.

A checagem do Bezalel mantém exceções de formato **nominais** para nove importações
com conteúdo original. Identidade, descrição e links continuam verificados.
pr-audit e iss-audit seguem as seis seções comuns do Bezalel. Não há instalação
global, runtime, mudança de papéis ou execução dos workflows nesta seleção.

## Adaptações autorizadas e resultado

| Skill | Benefício mantido | Mudança aplicada e motivo |
|---|---|---|
| [iss-audit](../skills/iss-audit/SKILL.md) | Relato separado da hipótese, reprodução segura, refutação, recorrência e plano de evidências. | Modos PM/dev separados. Retirados implementação/merge/fechamento obrigatórios, ampliação de credenciais e lista fechada de bloqueios. Decisão de negócio/banco permanece humana; segurança segue ao AppSec. |
| [pr-audit](../skills/pr-audit/SKILL.md) | Conferir alegações, diff hostil, contratos, consumidores, regressões e validade de provas. | Inclui candidato anterior à PR e restringe-se à revisão sem execução. TL solicita provas aos executores; não corrige, testa, cancela CI ou faz merge. |
| clean-code versus simplify | Simplificação preservando comportamento e limitando escopo. | Mantida a clean-code existente, sem alterá-la. Ela cobre o objetivo de simplify e acrescenta referências para erros, contratos e concorrência. Recomendação comunicada antes da atualização; simplify permanece apenas no clone. |

A procedência e os motivos detalhados estão nas referências de
[iss-audit](../skills/iss-audit/references/origem.md) e
[pr-audit](../skills/pr-audit/references/origem.md). As adaptações não constituem
aprovação de tarefas futuras nem certificam decisões humanas.

## Uso manual fora do fluxo

As cinco novas skills manuais e suas condições estão no
[guia de uso manual](bezalel-skills-uso-manual.md). Não são uma continuação
automática após a PR. A política `allow_implicit_invocation: false` foi registrada
nos adaptadores; sua interpretação no aplicativo não foi certificada.

release e github-resolution encontram a dependência pr-post-audit nesta árvore.
Os originais ainda têm convenções do autor; pr-bump, por exemplo, contém comandos
Rails/Bundler, e github-resolution menciona seções removidas das auditorias
adaptadas. O guia explica a compatibilidade e a necessidade de autorização real,
sem editar esses originais nem alegar validação operacional.

## Adaptações ainda não autorizadas

| Candidata | Benefício | Motivo para eventual adaptação | Recomendação |
|---|---|---|---|
| clonedeps | Inspecionar a versão certa de uma dependência. | Desacoplar @librarian/OpenCode e .slim, sem editar AGENTS/.ignore automaticamente. | Só quando houver necessidade concreta. |
| codemap | Compreender um repositório desconhecido. | Retirar caminhos fixos/agentes fixer e tornar mapas persistentes proporcionais. | Não adaptar sem um caso concreto. |
| improve-codebase-architecture | Avaliar módulos e interfaces. | Resolver dependência ausente grill-with-docs e acoplamento Explore/CONTEXT.md. | clean-architecture já atende à revisão corrente. |

Também não foram aplicadas as sugestões de desacoplar verification-planning de
@librarian ou restringir dentro de security-audit seu modo de execução/credenciais.
As condições já documentadas nas etapas continuam valendo; não se ocultou a
dependência e não se alterou o conteúdo dessas cópias.

## Limites da cobertura

agent-browser apoia exploração e execução de jornadas web, mas copiar o stub
não instala o programa nem valida seus guias dinâmicos. QA deve registrar versão,
pré-condições, caso e resultado. Uma jornada pelo browser não substitui regressão
automatizada persistente, prova de serviços/persistência, avaliação completa de
acessibilidade ou testes de aplicativo mobile nativo.

Ainda não há skill portátil específica de DB Reviewer/modelagem e migrations
nesses conjuntos. Os processos e ferramentas de verificação continuam exigidos;
uma skill opcional indisponível não dispensa evidência obrigatória.

A [relação por processo e etapa](bezalel-v2-skills.md) registra as 11 skills
indicadas em 24 etapas de 16 processos. Os 20 processos, 60 etapas, responsáveis,
decisões e caminhos permanecem. Os [contratos e adaptadores](README.md) usam essa
seleção; as skills não foram alteradas na conversão. Não houve execução de produto,
produção, publicação ou infraestrutura para validar o pacote.
