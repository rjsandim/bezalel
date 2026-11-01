# Fundamentos e SOLID

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0015 — Arquitetura medida pelo custo da mudança](#pagina-0015)
- [Página 0016 — Arquitetura como investigação contínua](#pagina-0016)
- [Página 0026 — Qualidade arquitetural medida pelo esforço necessário](#pagina-0026)
- [Página 0035 — Importância, urgência e o custo proibitivo das mudanças](#pagina-0035)
- [Página 0054 — Interfaces permitem inverter dependências do código](#pagina-0054)
- [Página 0058 — Separar processamento imutável de estado mutável](#pagina-0058)
- [Página 0059 — Mutação protegida e concentração da lógica imutável](#pagina-0059)
- [Página 0060 — Event sourcing: reconstruir estado a partir de transações](#pagina-0060)
- [Página 0065 — Um módulo responde a um ator](#pagina-0065)
- [Página 0066 — Reutilização acidental entre regras de atores diferentes](#pagina-0066)
- [Página 0070 — Aberto para extensão e fechado para modificação](#pagina-0070)
- [Página 0074 — Inversão de dependência e ocultação de informação](#pagina-0074)
- [Página 0075 — Substituição de Liskov e contratos de subtipos](#pagina-0075)
- [Página 0078 — Uma divergência no contrato cria tratamento especial](#pagina-0078)
- [Página 0081 — Interfaces específicas reduzem dependências desnecessárias](#pagina-0081)
- [Página 0083 — Preferir abstrações sem ignorar dependências estáveis](#pagina-0083)
- [Página 0085 — Fábricas isolam dependências concretas](#pagina-0085)

<a id="pagina-0015"></a>

## Página 0015 — Arquitetura medida pelo custo da mudança

O prefácio reconhece que o software funciona sob limites físicos de processamento, rede, memória e armazenamento. Propõe, porém, avaliar decisões arquiteturais também por tempo, dinheiro, esforço e custo de mudança. Uma boa arquitetura atende às necessidades atuais e mantém essa capacidade ao longo do tempo, tornando mudanças frequentes parte do trabalho normal. O desafio é projetar sem conhecer o futuro. A página critica duas respostas: impedir mudanças por autoridade e burocracia ou criar generalizações especulativas, parâmetros e código desnecessário que aumentam a complexidade.

---

<a id="pagina-0016"></a>

## Página 0016 — Arquitetura como investigação contínua

O prefácio conclui defendendo a preservação da flexibilidade do software. Como o conhecimento é incompleto, a arquitetura deve evoluir por perguntas, experiências, observação e aprendizado, em vez de ser tratada como um objeto definitivamente encerrado. Decisões arquiteturais funcionam como hipóteses que precisam ser confrontadas com implementação e medição. O texto associa essa postura a cuidado, prática e princípios: a velocidade sustentável depende da qualidade do trabalho. A conclusão é assinada por Kevlin Henney, em maio de 2017.

---

<a id="pagina-0026"></a>

## Página 0026 — Qualidade arquitetural medida pelo esforço necessário

No software, decisões amplas e detalhes formam uma estrutura contínua, sem divisão clara entre arquitetura e projeto. A meta proposta é reduzir o esforço humano necessário para construir e manter o sistema exigido. Assim, a qualidade deve ser avaliada pelo trabalho para atender ao cliente ao longo da vida do produto: esforço baixo e estável indica um bom projeto; crescimento a cada versão indica deterioração. A página inicia um estudo com dados reais de uma empresa anônima, começando pelo aumento de sua equipe de engenharia.

---

<a id="pagina-0035"></a>

## Página 0035 — Importância, urgência e o custo proibitivo das mudanças

O texto reconhece que a impossibilidade de mudar costuma ser econômica: a alteração custa mais do que o benefício esperado. Gestores podem priorizar funções atuais, mas continuam esperando flexibilidade quando novas necessidades surgem. A matriz de Eisenhower organiza problemas por importância e urgência. Martin situa o comportamento como frequentemente urgente, sem ser sempre importante, e a arquitetura como importante, embora raramente urgente. A distinção prepara uma hierarquia de prioridades para evitar que pressões imediatas eliminem o investimento na estrutura do sistema.

---

<a id="pagina-0054"></a>

## Página 0054 — Interfaces permitem inverter dependências do código

O diagrama mostra HL1 chamando a operação F de ML1 por uma interface I. Em execução, o controle continua indo de HL1 a ML1, mas a dependência da implementação aponta para a interface, em sentido oposto. Essa separação entre fluxo de controle e dependência do código é a inversão de dependência. Para Martin, o polimorfismo permite escolher a direção das relações entre módulos sem alterar quem chama quem. A página prepara a aplicação dessa capacidade para fazer interface de usuário e banco dependerem das regras de negócio.

---

<a id="pagina-0058"></a>

## Página 0058 — Separar processamento imutável de estado mutável

Martin relaciona condições de corrida, atualizações concorrentes e deadlocks à existência de estado mutável. A imutabilidade interessa à arquitetura porque reduz esse conjunto de problemas em sistemas com múltiplas threads e processadores. Entretanto, restrições de armazenamento e processamento exigem compromissos práticos. Uma solução é separar componentes que calculam sem alterar variáveis daqueles responsáveis por mudanças de estado. O diagrama mostra vários componentes imutáveis ligados a um componente mutável, por sua vez associado à memória transacional, preparando a explicação de como proteger as alterações inevitáveis.

---

<a id="pagina-0059"></a>

## Página 0059 — Mutação protegida e concentração da lógica imutável

A memória transacional trata alterações de variáveis com mecanismos semelhantes aos de transações ou repetição de operações. O exemplo Clojure usa um atom e swap! para incrementar um contador mediante comparação e nova tentativa quando o valor muda concorrentemente. A página ressalva que vários valores dependentes exigem mecanismos mais elaborados. A recomendação arquitetural é concentrar o máximo de processamento em componentes imutáveis e reduzir a lógica nos componentes mutáveis, protegendo-os com disciplinas adequadas. Ao final, introduz event sourcing e o exemplo de saldos bancários para discutir alternativas ao estado atualizado diretamente.

---

<a id="pagina-0060"></a>

## Página 0060 — Event sourcing: reconstruir estado a partir de transações

No exemplo bancário, o saldo pode ser calculado somando depósitos e retiradas registrados, em vez de ser continuamente sobrescrito. Essa é a ideia de event sourcing: preservar transações e derivar o estado delas. O custo de reconstrução pode ser reduzido salvando estados intermediários, como um saldo diário, e aplicando apenas eventos posteriores. O autor relaciona o modelo à disponibilidade crescente de armazenamento e aos sistemas de controle de versão. A página encerra retomando os três paradigmas como disciplinas restritivas: controle direto, controle indireto e atribuição de variáveis.

---

<a id="pagina-0065"></a>

## Página 0065 — Um módulo responde a um ator

A formulação do SRP passa a ser a responsabilidade de um módulo perante um único ator, entendido como um grupo de pessoas com a mesma origem de solicitações. Um módulo pode ser um arquivo ou um conjunto coeso de funções e dados. O exemplo Employee reúne calculatePay, reportHours e save, atendendo, respectivamente, à contabilidade ligada ao CFO, aos recursos humanos ligados ao COO e aos administradores de banco ligados ao CTO. A classe viola o princípio ao concentrar decisões de três atores distintos, preparando efeitos concretos desse acoplamento.

---

<a id="pagina-0066"></a>

## Página 0066 — Reutilização acidental entre regras de atores diferentes

O exemplo mostra calculatePay e reportHours compartilhando regularHours para calcular horas sem adicional. A área financeira pede uma alteração nesse cálculo, mas recursos humanos precisa manter o comportamento anterior. Um desenvolvedor modifica a função comum, testa e valida o pagamento; os relatórios de RH passam silenciosamente a apresentar números incorretos. A semelhança inicial dos algoritmos esconde razões de mudança independentes. Martin usa o caso para defender a separação do código utilizado por atores diferentes, mesmo quando evitar uma aparente duplicação parece conveniente. A página abre ainda o problema dos conflitos de integração.

---

<a id="pagina-0070"></a>

## Página 0070 — Aberto para extensão e fechado para modificação

O capítulo 8 apresenta o OCP, associado a Bertrand Meyer: o comportamento de um artefato deve poder crescer sem exigir mudanças em sua implementação existente. O princípio é usado para avaliar a arquitetura, pois pequenas extensões não deveriam provocar alterações disseminadas. Embora conhecido no projeto de classes e módulos, ganha importância na organização dos componentes. A página inicia um experimento com um sistema que mostra um resumo financeiro na web, com rolagem e números negativos em vermelho, estabelecendo o ponto de partida para uma nova forma de apresentação.

---

<a id="pagina-0074"></a>

## Página 0074 — Inversão de dependência e ocultação de informação

As interfaces do exemplo cumprem papéis distintos. FinancialDataGateway, a interface do apresentador e as interfaces de visualização invertem dependências que, sem elas, apontariam para detalhes periféricos. FinancialReportRequester oculta os elementos internos do interactor, evitando que o controlador adquira dependências transitivas de entidades que não usa diretamente. Assim, além de proteger a política central, o projeto limita conhecimento desnecessário entre componentes. A conclusão do OCP defende a extensão com baixo impacto, obtida pela divisão do sistema e por uma hierarquia de dependências que protege componentes de maior nível.

---

<a id="pagina-0075"></a>

## Página 0075 — Substituição de Liskov e contratos de subtipos

O capítulo 9 apresenta a definição de subtipos de Barbara Liskov: uma implementação deve poder substituir outra prevista pelo tipo sem alterar o comportamento esperado dos programas que a utilizam. Para tornar a ideia concreta, introduz uma aplicação de cobrança que chama calcFee em License. PersonalLicense e BusinessLicense calculam taxas com algoritmos diferentes, mas se apresentam como variações da mesma abstração. O exemplo prepara a discussão de substituição como critério de herança válida e, depois, como orientação para contratos arquiteturais.

---

<a id="pagina-0078"></a>

## Página 0078 — Uma divergência no contrato cria tratamento especial

O agregador envia endereço de coleta, horário e destino às empresas de táxi por uma interface REST comum. Uma empresa usa dest no lugar de destination, quebrando a uniformidade esperada. A solução ingênua, verificar o nome da empresa no código, espalha casos especiais e fica vulnerável a mudanças como aquisições e unificações de sistemas. O arquiteto acaba precisando de um gerador de comandos orientado por configuração, com formatos associados a URIs. A página mostra como uma pequena divergência de contrato introduz mecanismos adicionais na arquitetura inteira.

---

<a id="pagina-0081"></a>

## Página 0081 — Interfaces específicas reduzem dependências desnecessárias

Quando User1 depende de OPS inteira, mudanças em operações que ele não utiliza podem exigir recompilação e nova implantação. A solução apresentada cria U1Ops, U2Ops e U3Ops, deixando cada cliente depender somente da interface pertinente, embora OPS implemente todas. O texto distingue as dependências explícitas das linguagens estáticas das resolvidas em execução em linguagens dinâmicas. Em seguida, amplia o argumento: o problema arquitetural não se limita à tipagem. Depender de módulos que carregam funcionalidades desnecessárias pode trazer custos e riscos além do código diretamente usado.

---

<a id="pagina-0083"></a>

## Página 0083 — Preferir abstrações sem ignorar dependências estáveis

O capítulo 11 apresenta o DIP como preferência por dependências do código voltadas a abstrações, em lugar de implementações concretas. Em linguagens estáticas, isso aparece nas declarações importadas; a orientação também vale para linguagens dinâmicas. O autor reconhece que uma proibição absoluta é inviável: aplicações dependem de recursos concretos da plataforma, como String em Java. A estabilidade dessas classes torna a dependência aceitável. O foco do princípio começa, portanto, a se deslocar das implementações em geral para aquelas sujeitas a alterações frequentes.

---

<a id="pagina-0085"></a>

## Página 0085 — Fábricas isolam dependências concretas

Application usa Service e pede sua criação à interface ServiceFactory. ServiceFactoryImpl conhece ConcreteImpl, cria o objeto e o devolve pela abstração Service. A fronteira desenhada separa política abstrata e detalhes concretos; as dependências do código a atravessam na direção das abstrações, enquanto o controle pode seguir o sentido contrário. O autor admite que dependências concretas não desaparecem por completo: devem ser concentradas em poucos componentes. O componente main normalmente monta os objetos iniciais, incluindo a fábrica, e entrega ao sistema acesso por um tipo abstrato.
