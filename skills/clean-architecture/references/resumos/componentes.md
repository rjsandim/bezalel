# Coesão, ciclos e estabilidade dos componentes

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill; não dependem do PDF nem de arquivos externos.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0094 — Releases coerentes e mudanças concentradas](#pagina-0094)
- [Página 0095 — Fechamento comum e classes reutilizadas em conjunto](#pagina-0095)
- [Página 0096 — Reutilização comum evita dependências excedentes](#pagina-0096)
- [Página 0097 — O equilíbrio de coesão muda com a maturidade](#pagina-0097)
- [Página 0100 — Um grafo acíclico torna os impactos previsíveis](#pagina-0100)
- [Página 0101 — Ciclos transformam componentes separados em um bloco](#pagina-0101)
- [Página 0102 — Quebrar ciclos com inversão de dependência](#pagina-0102)
- [Página 0103 — Extrair um componente comum e acompanhar a evolução](#pagina-0103)
- [Página 0104 — A estrutura de componentes evolui para isolar mudanças](#pagina-0104)
- [Página 0105 — Estabilidade significa dificuldade de mudança](#pagina-0105)
- [Página 0107 — A métrica de instabilidade e sua direção desejada](#pagina-0107)
- [Página 0110 — Componentes estáveis devem ser abstratos](#pagina-0110)
- [Página 0111 — Medir abstração e relacioná-la à instabilidade](#pagina-0111)
- [Página 0112 — Zonas de rigidez e de abstrações sem usuários](#pagina-0112)
- [Página 0113 — Sequência principal e distância como sinal de revisão](#pagina-0113)
- [Página 0114 — Usar métricas para investigar a evolução do projeto](#pagina-0114)

<a id="pagina-0094"></a>

## Página 0094 — Releases coerentes e mudanças concentradas

Componentes reutilizados precisam de identificação de versão, comunicação e documentação de alterações para que consumidores escolham quando atualizar. As classes reunidas devem compartilhar um propósito e fazer sentido como uma única entrega. O autor reconhece que esse critério isolado é pouco preciso e introduz o CCP para aprofundá-lo: agrupar classes que mudam pelas mesmas razões e no mesmo momento, separando as demais. Como manutenção frequentemente importa mais que reutilização, concentrar uma mudança em poucos componentes reduz o trabalho de validação e implantação associado a cada evolução do sistema.

---

<a id="pagina-0095"></a>

## Página 0095 — Fechamento comum e classes reutilizadas em conjunto

O CCP reúne classes que tendem a mudar juntas, reduzindo o número de componentes afetados por um requisito. Seu vínculo com OCP é estratégico: não se pode fechar o sistema contra toda mudança, mas é possível proteger as situações mais frequentes ou esperadas. Ele também amplia o SRP para a escala dos componentes. A página introduz o CRP: classes usadas em conjunto, como um contêiner e seus iteradores, devem permanecer juntas. O princípio também orienta quais classes separar para evitar que um consumidor dependa de funções que não precisa.

---

<a id="pagina-0096"></a>

## Página 0096 — Reutilização comum evita dependências excedentes

Usar uma única classe ainda cria dependência de todo o componente que a contém. Mudanças em partes não utilizadas podem exigir recompilação, testes e nova implantação do consumidor. O CRP recomenda, por isso, reunir somente classes fortemente relacionadas e normalmente usadas juntas, evitando obrigações desnecessárias. É a ampliação do ISP: não depender do que não se utiliza. A página apresenta então a tensão entre critérios de coesão: REP e CCP tendem a formar componentes maiores, enquanto CRP tende a separá-los. O arquiteto precisa equilibrar essas forças.

---

<a id="pagina-0097"></a>

## Página 0097 — O equilíbrio de coesão muda com a maturidade

O triângulo de coesão mostra o custo de privilegiar dois princípios e negligenciar o terceiro: alterações espalhadas, releases desnecessários ou dificuldade de reutilização. A posição adequada depende das preocupações atuais da equipe. No início, concentrar mudanças costuma importar mais do que preparar reutilização externa; com a maturidade e novos consumidores, essa prioridade pode mudar. A conclusão rejeita uma definição de coesão limitada a uma única função. A composição dos componentes resulta do equilíbrio entre desenvolvimento e reutilização e deve evoluir conforme a maneira como o projeto é construído e usado.

---

<a id="pagina-0100"></a>

## Página 0100 — Um grafo acíclico torna os impactos previsíveis

O diagrama de componentes forma um grafo dirigido sem caminho que retorne ao ponto de partida. Com essa organização, seguir as dependências ao contrário revela quem precisa avaliar uma nova versão: alterações em Presenters afetam View e Main, enquanto mudanças em Main não afetam outros componentes. Para testar Presenters, bastam suas dependências Interactors e Entities, reduzindo o preparo e as variáveis envolvidas. O texto também inicia a ordem de construção de baixo para cima, mostrando como um grafo acíclico torna claras a validação, a integração e a liberação do sistema.

---

<a id="pagina-0101"></a>

## Página 0101 — Ciclos transformam componentes separados em um bloco

Uma nova dependência de Entities para Authorizer fecha um ciclo com Interactors. Com isso, até Database passa a precisar de compatibilidade com mais partes do sistema. Entities, Authorizer e Interactors comportam-se como um único componente grande, obrigando suas equipes a coordenar versões e prejudicando a autonomia. Testar Entities exige agora construir e integrar os outros participantes do ciclo. O autor associa esse acoplamento à dificuldade de isolar testes, liberar componentes e determinar uma ordem de construção. O diagrama mostra como uma única aresta pode espalhar esses efeitos.

---

<a id="pagina-0102"></a>

## Página 0102 — Quebrar ciclos com inversão de dependência

A página conclui que ciclos podem impedir uma ordem correta de construção, especialmente quando declarações dependem de arquivos já compilados. Em seguida apresenta o primeiro mecanismo para restaurar um grafo acíclico: aplicar DIP. No exemplo, uma interface com as operações necessárias a User fica em Entities e é implementada em Authorizer. A dependência antes dirigida de Entities para Authorizer passa a apontar para a abstração em Entities, rompendo o ciclo. A explicação e os diagramas dessa reorganização continuam nas páginas seguintes.

---

<a id="pagina-0103"></a>

## Página 0103 — Extrair um componente comum e acompanhar a evolução

O primeiro diagrama conclui a solução por DIP, colocando a interface de permissões em Entities e sua implementação em Authorizer. A segunda alternativa cria um componente Permissions com as classes compartilhadas, do qual ambos passam a depender. O autor destaca que remover ciclos pode exigir novos componentes e reorganizações ao longo do crescimento da aplicação. Por isso, o grafo deve ser acompanhado continuamente. A página começa a discussão de por que a estrutura de componentes não pode ser fixada inteiramente de cima para baixo antes do desenvolvimento.

---

<a id="pagina-0104"></a>

## Página 0104 — A estrutura de componentes evolui para isolar mudanças

Os diagramas de dependência refletem principalmente as necessidades de construir e manter o sistema, e não apenas suas funções. A estrutura emerge conforme classes, mudanças recorrentes e oportunidades de reutilização ficam conhecidas. SRP e CCP ajudam a concentrar alterações; CRP influencia os elementos reutilizáveis; ADP corrige ciclos. Uma preocupação central é proteger políticas valiosas de detalhes voláteis, como alterações cosméticas da interface. A página introduz então o princípio das dependências estáveis: componentes destinados a mudar precisam depender em direção à estabilidade, preservando sua liberdade de evolução.

---

<a id="pagina-0105"></a>

## Página 0105 — Estabilidade significa dificuldade de mudança

Um componente projetado para mudar facilmente pode perder essa liberdade se outro, difícil de modificar, passar a depender dele. O SDP evita essa inversão. A estabilidade é definida pelo esforço necessário para mudar, e não pela frequência com que algo de fato muda; uma moeda equilibrada ilustra a diferença. Em software, muitas dependências de entrada criam obrigações de compatibilidade. O exemplo X recebe dependências de três componentes e não depende de nenhum outro: é responsável perante consumidores e independente de influências externas, tornando-se estruturalmente estável.

---

<a id="pagina-0107"></a>

## Página 0107 — A métrica de instabilidade e sua direção desejada

A instabilidade é calculada por I = fan-out / (fan-in + fan-out), variando de zero a um. No exemplo, Cc recebe dependências de três classes externas e depende de uma classe externa, resultando em I = 1/4. Zero caracteriza um componente com consumidores e sem dependências de saída; um caracteriza o inverso. A página relaciona a contagem a referências como imports e includes. Segundo o SDP, a instabilidade deve diminuir no sentido das dependências: um componente deve depender de outros mais estáveis que ele.

---

<a id="pagina-0110"></a>

## Página 0110 — Componentes estáveis devem ser abstratos

O texto observa que linguagens dinâmicas podem inverter dependências sem declarar componentes explícitos de interfaces. Depois apresenta o princípio das abstrações estáveis: quanto mais estável um componente, mais abstrato deve ser. Políticas de alto nível precisam permanecer protegidas, mas também extensíveis; abstrações permitem essa combinação. Componentes instáveis podem concentrar implementações concretas, pois são mais fáceis de alterar. SAP e SDP juntos transportam DIP à escala dos componentes: dependências seguem para estabilidade e, consequentemente, para abstração. Diferentemente de uma classe isolada, um componente pode possuir graus intermediários dessas características.

---

<a id="pagina-0111"></a>

## Página 0111 — Medir abstração e relacioná-la à instabilidade

A métrica A divide o número de interfaces e classes abstratas pelo total de classes do componente. Varia entre zero, totalmente concreto, e um, totalmente abstrato. O gráfico coloca instabilidade I no eixo horizontal e abstração A no vertical. Dois extremos desejáveis aparecem em (0,1), estável e abstrato, e (1,0), instável e concreto. Como componentes reais combinam graus dessas propriedades, o autor procura posições intermediárias aceitáveis. Para identificá-las, propõe primeiro localizar regiões problemáticas do gráfico, introduzindo as zonas de exclusão desenvolvidas a seguir.

---

<a id="pagina-0112"></a>

## Página 0112 — Zonas de rigidez e de abstrações sem usuários

Próximo de (0,0), um componente é concreto e difícil de alterar: essa zona de dor reúne estruturas pouco extensíveis e com muitos consumidores, como esquemas de banco. A volatilidade agrava o problema; elementos concretos que raramente mudam, como bibliotecas consolidadas, podem ser aceitáveis nessa posição. Próximo de (1,1), aparecem abstrações sem dependentes, caracterizadas como zona de inutilidade, frequentemente resíduos de implementações nunca realizadas.

Observação: o parágrafo sobre biblioteca utilitária menciona I = 1 ao situá-la perto de (0,0); essa notação é inconsistente no original, também conferido visualmente.

---

<a id="pagina-0113"></a>

## Página 0113 — Sequência principal e distância como sinal de revisão

A sequência principal é a linha entre (0,1) e (1,0), afastada das zonas de rigidez e abstração sem uso. Nela, o grau de abstração se equilibra com a estabilidade; os extremos são preferidos, mas posições intermediárias podem ser adequadas. A métrica D = |A + I − 1| mede o afastamento dessa linha, entre zero e um. Valores elevados sugerem examinar o componente. Média, variância e limites estatísticos podem destacar desvios dentro de um sistema, funcionando como sinais para investigação e eventual reorganização.

---

<a id="pagina-0114"></a>

## Página 0114 — Usar métricas para investigar a evolução do projeto

O gráfico de dispersão mostra componentes próximos da sequência principal e alguns afastados, merecendo análise. Outro gráfico acompanha D do componente Payroll entre releases: em R2.1, o valor ultrapassa o limite ilustrativo de 0,1, indicando que novas dependências podem ter desequilibrado sua estrutura. A conclusão ressalva que métricas representam uma comparação com um padrão escolhido, não uma verdade absoluta. Elas expressam a experiência do autor sobre dependências e abstração, mas permanecem imperfeitas e devem servir como instrumentos de investigação, sem substituir o julgamento arquitetural.
