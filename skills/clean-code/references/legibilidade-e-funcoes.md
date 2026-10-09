# Legibilidade e funções

Use esta referência ao corrigir nomes, fluxo de leitura, parâmetros, duplicação, comentários ou formatação.

## Nomes que explicam o contrato

| Sinal | Correção a considerar |
|---|---|
| Abreviação ou unidade implícita | Nomeie o papel e a unidade, como quantidade, duração ou valor em centavos. |
| Mesma operação com vocabulário inconsistente | Use os termos adotados no domínio; reserve palavras diferentes para diferenças reais de significado. |
| Abstração nomeada por uma implementação | Nomeie o conceito que todas as variantes representam. |
| Consulta que também cria, grava ou reinicializa | Explicite o efeito ou separe responsabilidades mantendo o contrato e a sequência necessários. |
| Muitos prefixos para explicar um identificador | Forneça contexto por módulo, classe ou parâmetro, sem repetir toda a hierarquia no nome. |
| Valor literal cujo significado exige investigação | Nomeie a regra de domínio e centralize-a quando precisar mudar em conjunto. |

Use nomes pronunciáveis e pesquisáveis, proporcionais ao alcance do identificador. Índices curtos em laços pequenos e literais evidentes não precisam de nomes cerimoniosos. Diferencie operações que modificam o receptor daquelas que retornam um novo valor. Um nome melhor não autoriza remover efeitos nem alterar retornos públicos.

## Funções e fluxo compreensíveis

Uma função pode executar várias etapas e ainda representar uma tarefa quando elas estão no nível de abstração imediatamente abaixo de seu nome. Evite misturar regras de negócio com montagem de strings, protocolo, persistência e apresentação no mesmo fluxo.

- Extraia uma função quando ela nomear um conceito. Se a extração apenas transferir linhas e aumentar a navegação, mantenha o trecho junto.
- Nomeie condições e resultados intermediários quando isso revelar a decisão ou o cálculo. Preserve sinais, precisão e condições de limite. Se o mesmo ajuste de fronteira aparece na comparação e na execução, calcule-o uma vez com um nome como `proximoIndice`; confirme primeiro se as duas ocorrências devem observar o mesmo estado.
- Um booleano que apenas seleciona procedimentos diferentes pode pedir operações nomeadas. Um booleano que representa um dado legítimo do domínio pode permanecer como parâmetro.
- Agrupe argumentos quando formarem um conceito, como coordenadas de um ponto. Não esconda parâmetros em um objeto genérico ou em campos apenas para diminuir a contagem.
- Seleções por tipo repetidas em várias operações podem justificar polimorfismo ou uma fábrica. Um `switch` local, estável e claro pode continuar sendo a melhor solução.
- Expresse dependências de ordem por dados realmente necessários ou por uma função que coordene a sequência. Não invente parâmetros sem significado apenas para impor ordenação.
- Evite consultas com mutações surpreendentes. Se o contrato existente combina esses efeitos, torne-o explícito antes de considerar uma separação compatível.

Funções curtas e poucos parâmetros são heurísticas. Não imponha cotas de linhas, quantidade fixa de argumentos ou uma regra absoluta de retorno único.

## Duplicação, comentários e formatação

Reconheça duplicação de conhecimento além de linhas idênticas: fórmulas para a mesma regra, conversões equivalentes e decisões que precisam mudar juntas. A abstração compartilhada deve ter a mesma semântica e motivo de mudança. Se a unificação exigir vários seletores para acomodar regras independentes, reavalie-a.

Comentários devem explicar razões, restrições, contratos externos e consequências não óbvias. Preserve alertas úteis, justificativas de desempenho ou concorrência e informações legais. Atualize comentários que prometem algo diferente da implementação. Substitua explicações do óbvio por nomes claros; não proíba comentários nem documente toda assinatura por obrigação.

Remova código desativado e elementos aparentemente mortos somente depois de compreender seus usos, inclusive os indiretos. Não elimine uma capacidade apenas porque uma busca textual local não encontrou chamadas.

Aproxime conceitos relacionados, separe grupos distintos e organize a leitura do geral para o detalhe quando isso combinar com o projeto. Use o formatador existente e o estilo da equipe. Evite reformatar arquivos alheios à alteração.

## Exemplos de decisão

**Nome que revela efeito.** Se `obterSessao()` cria uma sessão quando ela não existe, `obterOuCriarSessao()` comunica melhor o contrato. Antes de renomear, localize consumidores. Se o nome fizer parte de uma API estável, melhorar a implementação interna e documentar o efeito pode ser a alteração compatível; não introduza silenciosamente uma migração pública.

**Parâmetros que formam um conceito.** Coordenadas `x` e `y` podem formar um ponto recebido por `criarCirculo(centro, raio)`. Isso tem valor quando o ponto possui significado próprio. Empacotar destinatário, tentativas, formato e prazo num objeto genérico apenas para reduzir a assinatura não demonstra uma abstração útil.

**Booleano de domínio versus seletor.** `salvarPreferencia(receberNotificacoes)` recebe um dado do usuário. Já um `executar(pedido, true)` cujo sinal alterna entre duas tarefas diferentes esconde uma decisão na chamada. Nesse segundo caso, considere operações com nomes próprios ou um tipo de opção explícito, conforme o contrato e as convenções locais.

**Extração que ajuda versus navegação adicional.** Um predicado como `podeCancelar(pedido)` é útil se nomeia uma regra coerente. Extrair cada comparação trivial para uma função distante pode obrigar o leitor a abrir várias definições sem aprender nada sobre o domínio. Avalie a leitura do chamador depois da mudança.

## Perguntas para a revisão local

- O leitor consegue prever a operação, a unidade e os efeitos pelos nomes?
- A decomposição separa níveis de abstração ou apenas distribui linhas?
- As partes unificadas devem realmente mudar juntas?
- Um comentário preserva uma razão que desapareceria com sua remoção?
- A formatação segue o projeto e evidencia a hierarquia das operações?

Use essas perguntas quando houver o sinal correspondente; não transforme toda mudança em uma revisão completa de estilo.
