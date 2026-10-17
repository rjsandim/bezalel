# Skills reservadas à chamada manual

As cinco skills abaixo foram copiadas a pedido de Rafael em 16/10/2026, da revisão
`7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a` de
[akitaonrails/my-skills](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a).
**Nenhuma é indicada nas etapas do Company Flow.** A conclusão de uma auditoria
ou a entrega da PR não dispara essas rotinas.

| Skill | Uso pretendido | Condições concretas |
|---|---|---|
| [release](../skills/release/SKILL.md) | Preparar/publicar uma versão expressamente solicitada. | Confirmar estratégia, versão e alvo. O original exige pr-post-audit quando o intervalo não satisfaz sua dispensa; a dependência está copiada. Conferir os checks no SHA final, inclusive após alterações de versão/lockfile. A limpeza da origem não autoriza força ou remoção por prefixo. |
| [reflect](../skills/reflect/SKILL.md) | Rever padrões recorrentes e propor melhorias. | O original usa contexto OpenCode/oh-my-opencode-slim. Usar somente evidência pertinente e disponível; não inventar logs/configuração, criar agentes ou alterar instalações sem pedido. |
| [github-resolution](../skills/github-resolution/SKILL.md) | Executar um conjunto de resoluções previamente auditado e autorizado. | Os relatórios das variantes pr-audit/iss-audit são recomendações; conferir a aprovação humana real, objeto e escopo. Regras locais prevalecem sobre carry-through e a lista fechada de bloqueios da origem. Acima de três tickets, a origem exige pr-post-audit, agora disponível. Não ampliar a execução para todo o backlog. |
| [pr-bump](../skills/pr-bump/SKILL.md) | Consolidar atualizações de dependências de bots. | O original contém exemplos Rails/Bundler e publica na branch padrão. Confirmar stack, comandos, estratégia e autorização do projeto; os valores de teste do exemplo são sintéticos. Checks obrigatórios falhos impedem publicação; a orientação “fix forward” não permite publicar uma quebra conhecida. |
| [pr-post-audit](../skills/pr-post-audit/SKILL.md) | Auditar a composição de um intervalo integrado ou candidato de publicação. | Apoio manual autorizado para release/github-resolution. Identificar intervalo/árvore exatos; não presumir SHA para alterações não commitadas. Auditoria e eventual correção respeitam o pedido; deploy, produção e tag só entram quando expressamente autorizados. |

## Preservação e invocação

Os cinco `SKILL.md` permanecem idênticos aos originais. Nas quatro pastas sem
adaptador, foi acrescentado `agents/openai.yaml` com interface em português e
`policy.allow_implicit_invocation: false`. Em pr-post-audit, a interface original
foi preservada e somente essa política foi acrescentada. Esses arquivos são
metadados de invocação, não definições de novos agentes.

A interpretação da política depende do aplicativo e não foi certificada em um
loader nesta tarefa. As skills ficam nesta árvore; não foram instaladas globalmente.
Para usar em outro aplicativo, copiar a pasta completa e conferir suas instruções
e pré-requisitos. Neste repositório, pode-se pedir a leitura da skill pelo caminho.

As condições acima descrevem compatibilidade e limites de uso; não são alterações
ocultas nos originais. Ao transportar uma skill para outro projeto, as instruções
daquele projeto e a autorização real devem ser conferidas novamente. Não se presume
que este documento externo à pasta será carregado automaticamente.

## Relação com as auditorias adaptadas

`pr-audit` e `iss-audit` deixaram de executar resoluções/merge. Mantêm recomendações
que podem alimentar github-resolution, mas a skill manual original ainda faz
referência às seções de carry-through e Approved Implementation da origem.
Essas referências não reinserem o comportamento removido: o relatório real,
as decisões vigentes e as regras do projeto são necessários antes de executar.

A orientação de branches foi mantida em iss-audit; não existe um procedimento de
Approved Implementation dentro dessa variante. Se uma chamada manual depender
de regras da origem incompatíveis ou ausentes, explicitar a divergência e preparar
o plano da ação dentro do escopo autorizado. Não inventar autorização ou afirmar
que essa interoperabilidade já foi validada por uma execução real.

## O que foi validado

Conteúdo original e permissões das cópias, presença das dependências entre essas
skills, metadados de invocação e links locais. Não houve chamada dos workflows,
publicação de PR, resolução/fechamento de tickets, limpeza, deploy ou release.
A presença das pastas comprova disponibilidade documental, não prontidão de
ferramentas, autenticação, CI ou infraestrutura do projeto onde serão usadas.
