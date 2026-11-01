# Fronteiras, domínio e casos de uso

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0117 — Arquitetura e participação contínua no código](#pagina-0117)
- [Página 0119 — Equilibrar desenvolvimento, implantação e operação](#pagina-0119)
- [Página 0120 — Políticas independentes permitem adiar detalhes](#pagina-0120)
- [Página 0126 — Operação e equipes exigem componentes isolados](#pagina-0126)
- [Página 0127 — Implantação simples e opções preservadas](#pagina-0127)
- [Página 0128 — Camadas horizontais e casos de uso verticais](#pagina-0128)
- [Página 0129 — Independência de execução, desenvolvimento e implantação](#pagina-0129)
- [Página 0130 — Duplicação real, semelhança acidental e formas de separação](#pagina-0130)
- [Página 0131 — O modo de desacoplamento deve poder evoluir](#pagina-0131)
- [Página 0132 — Antecipar mudanças sem exigir uma troca trivial](#pagina-0132)
- [Página 0133 — Fronteiras adiam decisões alheias ao negócio](#pagina-0133)
- [Página 0134 — O custo de distribuir um sistema antes da necessidade](#pagina-0134)
- [Página 0137 — A fronteira da persistência preserva tempo e alternativas](#pagina-0137)
- [Página 0138 — A fronteira atravessa a implementação da interface](#pagina-0138)
- [Página 0139 — O banco depende das regras, e não o contrário](#pagina-0139)
- [Página 0140 — Interface como plugin de um modelo independente](#pagina-0140)
- [Página 0141 — Plugins tornam substituições viáveis](#pagina-0141)
- [Página 0142 — Responsabilidade única orienta onde traçar fronteiras](#pagina-0142)
- [Página 0144 — Anatomia das fronteiras e dependências do código](#pagina-0144)
- [Página 0145 — Um monólito também contém fronteiras relevantes](#pagina-0145)
- [Página 0146 — Inversão na fronteira e componentes implantáveis](#pagina-0146)
- [Página 0147 — Threads e processos locais têm papéis distintos](#pagina-0147)
- [Página 0148 — Serviços e a combinação de tipos de fronteira](#pagina-0148)
- [Página 0149 — Políticas agrupadas conforme suas mudanças](#pagina-0149)
- [Página 0151 — A política de criptografia controla seus contratos](#pagina-0151)
- [Página 0154 — Entidades reúnem dados e regras essenciais](#pagina-0154)
- [Página 0155 — Casos de uso coordenam regras e entidades](#pagina-0155)
- [Página 0156 — Entidades independentes e modelos de entrada e saída](#pagina-0156)
- [Página 0158 — A arquitetura deve revelar a finalidade da aplicação](#pagina-0158)
- [Página 0160 — Arquitetura reconhecível e testável sem infraestrutura](#pagina-0160)
- [Página 0162 — A regra de dependência da arquitetura limpa](#pagina-0162)
- [Página 0163 — Responsabilidades das três camadas internas](#pagina-0163)
- [Página 0164 — Detalhes externos e inversão ao cruzar camadas](#pagina-0164)
- [Página 0165 — Um fluxo completo entre controlador, caso de uso e apresentador](#pagina-0165)
- [Página 0166 — Camadas testáveis e detalhes substituíveis](#pagina-0166)
- [Página 0174 — O jogo revela fronteiras além de três componentes](#pagina-0174)
- [Página 0175 — Idiomas e armazenamento dependem das regras do jogo](#pagina-0175)
- [Página 0176 — Idioma e meio de entrega são eixos independentes](#pagina-0176)
- [Página 0177 — Fluxos distintos convergem para políticas superiores](#pagina-0177)
- [Página 0178 — Rede e subdivisões dentro das regras do jogo](#pagina-0178)
- [Página 0179 — Uma política superior pode tornar-se serviço remoto](#pagina-0179)
- [Página 0220 — Estudo de caso de uma plataforma de venda de vídeos](#pagina-0220)
- [Página 0221 — Quatro atores orientam a análise dos casos de uso](#pagina-0221)
- [Página 0222 — Dos atores aos componentes e abstrações de catálogo](#pagina-0222)

<a id="pagina-0117"></a>

## Página 0117 — Arquitetura e participação contínua no código

O capítulo 15 questiona a imagem do arquiteto como alguém afastado da programação. Para Martin, ele continua programador e participa de tarefas concretas para conhecer os problemas que suas decisões produzem para a equipe. A arquitetura é definida como a forma do sistema: divisão em componentes, arranjo dessas partes e seus modos de comunicação. Seu propósito é facilitar desenvolvimento, implantação, operação e manutenção. A página relaciona, portanto, o papel técnico do arquiteto ao aumento da produtividade e à experiência real de quem implementa o software.

---

<a id="pagina-0119"></a>

## Página 0119 — Equilibrar desenvolvimento, implantação e operação

Uma arquitetura de muitos microsserviços pode facilitar o trabalho de equipes e, ao mesmo tempo, dificultar configuração, conexões e ordem de inicialização na implantação. Considerar isso cedo poderia levar a menos serviços ou a uma composição híbrida. Sobre operação, o autor argumenta que certos problemas podem ser compensados por hardware, enquanto limitações de desenvolvimento e manutenção consomem mais esforço humano. Ainda assim, a arquitetura deve comunicar claramente casos de uso e comportamentos necessários. A página encerra introduzindo a manutenção como grande consumidora de recursos, devido a novas funções e correções contínuas.

---

<a id="pagina-0120"></a>

## Página 0120 — Políticas independentes permitem adiar detalhes

O custo de manutenção inclui descobrir onde e como alterar o código e o risco de introduzir defeitos. Componentes isolados por interfaces estáveis reduzem essas dificuldades. A página divide o sistema entre políticas, que contêm regras e procedimentos de negócio, e detalhes que permitem interagir com elas, como bancos, dispositivos, servidores e frameworks. O arquiteto deve tornar esses detalhes irrelevantes para a política. Assim, decisões sobre banco de dados ou entrega pela web podem ser adiadas enquanto as regras centrais evoluem sem compromisso com uma tecnologia específica.

---

<a id="pagina-0126"></a>

## Página 0126 — Operação e equipes exigem componentes isolados

Os comportamentos principais devem aparecer em classes, funções ou módulos de destaque, com nomes que expressem sua função. Para a operação, a arquitetura precisa acomodar requisitos concretos de vazão e resposta, usando processos, threads, serviços ou um programa único conforme necessário. Isolar componentes sem pressupor seu mecanismo de comunicação facilita mudar entre essas alternativas. No desenvolvimento, a lei de Conway relaciona o desenho do sistema à comunicação da organização. A resposta arquitetural é dividir o sistema em componentes que equipes possam desenvolver independentemente, reduzindo interferências entre seus trabalhos.

---

<a id="pagina-0127"></a>

## Página 0127 — Implantação simples e opções preservadas

Uma boa arquitetura deve permitir implantar o sistema logo após sua construção, evitando depender de muitos ajustes manuais e roteiros de configuração. Isso requer componentes isolados e mecanismos responsáveis por iniciá-los, integrá-los e supervisioná-los. Equilibrar implantação, operação, desenvolvimento e casos de uso é difícil porque requisitos e equipes são parcialmente desconhecidos e mudam. O texto propõe preservar alternativas mediante uma separação cuidadosa. Ao iniciar a discussão das camadas, aplica responsabilidade única e fechamento comum: interface e regras de negócio mudam por razões distintas e precisam evoluir de forma independente, mantendo os casos de uso reconhecíveis.

---

<a id="pagina-0128"></a>

## Página 0128 — Camadas horizontais e casos de uso verticais

Regras específicas da aplicação, como validação de campos, devem ser separadas das regras gerais do domínio, como juros ou inventário. Banco, linguagem de consulta e esquema também têm razões próprias para mudar. Formam-se assim camadas horizontais independentes. Os casos de uso constituem outra divisão: fatias verticais que atravessam interface, regras e persistência. Separar adicionar pedido de excluir pedido em toda essa extensão reduz o impacto de novos comportamentos sobre os anteriores. A mesma organização ajuda na operação: partes com diferentes necessidades de vazão podem ser distribuídas ou replicadas separadamente.

---

<a id="pagina-0129"></a>

## Página 0129 — Independência de execução, desenvolvimento e implantação

Para distribuir componentes por servidores, não basta separá-los logicamente: eles não podem pressupor o mesmo espaço de memória e precisam comunicar-se como serviços. O texto não estabelece serviços ou microsserviços como solução universal; o próprio modo de separação deve permanecer uma escolha aberta. Camadas e casos de uso desacoplados reduzem conflitos entre equipes, qualquer que seja sua organização. Também oferecem flexibilidade de implantação, podendo permitir substituir partes ou acrescentar casos de uso sem alterar todo o sistema em execução. A página inicia um alerta sobre o medo de duplicação e seus efeitos na arquitetura.

---

<a id="pagina-0130"></a>

## Página 0130 — Duplicação real, semelhança acidental e formas de separação

Duplicação verdadeira exige que mudanças em uma cópia se repitam nas demais; trechos parecidos que evoluem por motivos diferentes representam semelhança acidental. Compartilhar prematuramente telas, algoritmos ou consultas de casos de uso distintos pode criar dependências difíceis de desfazer. O mesmo vale para reutilizar registros do banco diretamente na interface: um modelo de apresentação separado preserva as camadas. A página distingue ainda separação no código-fonte, com chamadas no mesmo executável, e separação entre unidades implantáveis, como bibliotecas e arquivos JAR, permitindo mudanças sem reconstruir ou redistribuir todos os módulos. A segunda modalidade continua na página seguinte.

---

<a id="pagina-0131"></a>

## Página 0131 — O modo de desacoplamento deve poder evoluir

A separação no nível de serviço permite que unidades se comuniquem por pacotes de rede e sejam independentes de alterações no código e nos binários das demais. Porém, adotá-la por padrão custa tempo de desenvolvimento e recursos, além de favorecer divisões excessivamente amplas. O autor prefere preparar componentes que possam virar serviços, mantendo-os no mesmo espaço de memória enquanto isso for suficiente. A evolução pode passar do código-fonte para unidades implantáveis e depois para serviços, conforme necessidades reais. Também deve permitir o caminho inverso, protegendo a maior parte do código dessas mudanças e acomodando instalações de portes diferentes.

---

<a id="pagina-0132"></a>

## Página 0132 — Antecipar mudanças sem exigir uma troca trivial

A conclusão do capítulo reconhece a dificuldade de preservar diferentes modos de desacoplamento. Não afirma que alternar entre monólito, unidades implantáveis e serviços deva sempre se resumir a mudar uma configuração, embora isso às vezes seja adequado. O ponto central é que essa modalidade pode mudar ao longo da vida do sistema, e uma boa arquitetura deve prever e facilitar essa evolução de maneira proporcional às necessidades.

---

<a id="pagina-0133"></a>

## Página 0133 — Fronteiras adiam decisões alheias ao negócio

O capítulo 17 define arquitetura como o desenho de fronteiras que separam elementos e limitam o conhecimento entre eles. Algumas surgem antes do código para impedir que escolhas prematuras contaminem a lógica central; outras aparecem depois. O objetivo é reduzir o trabalho humano necessário para construir e manter o sistema. O acoplamento a decisões antecipadas sobre frameworks, bancos, servidores, bibliotecas e injeção de dependência prejudica esse objetivo. Como não constituem os casos de uso, essas escolhas devem ser secundárias e adiáveis, com pouco impacto sobre a aplicação.

---

<a id="pagina-0134"></a>

## Página 0134 — O custo de distribuir um sistema antes da necessidade

O caso composto da empresa P descreve a migração de uma aplicação de desktop para a web. A equipe adotou três camadas distribuídas, repetiu objetos de domínio e criou protocolos de mensagens entre máquinas. Acrescentar um campo passou a exigir mudanças em classes, mensagens, manipuladores e três executáveis, além dos custos de serialização e comunicação. Durante anos, tudo rodou em processos na mesma máquina; nenhuma instalação chegou a precisar da infraestrutura de servidores imaginada. A decisão antecipada multiplicou o esforço de desenvolvimento e manteve uma complexidade operacional sem benefício comprovado.

---

<a id="pagina-0137"></a>

## Página 0137 — A fronteira da persistência preserva tempo e alternativas

A separação entre regras de negócio e banco permitiu ao FitNesse desenvolver funcionalidades por cerca de dezoito meses sem enfrentar esquemas, consultas, conexões ou administração de servidor, mantendo testes rápidos. A solução por arquivos não impediu uma alternativa posterior com MySQL. O texto defende fronteiras entre interface, banco e regras, pois cada parte pode trabalhar sem conhecer os detalhes das outras. As regras precisam apenas de operações para buscar e salvar dados. Introduz-se então um desenho em que BusinessRules usa DatabaseInterface, enquanto DatabaseAccess implementa essa interface e opera o banco real.

---

<a id="pagina-0138"></a>

## Página 0138 — A fronteira atravessa a implementação da interface

As figuras 17.1 e 17.2 mostram BusinessRules dependendo de DatabaseInterface, implementada por DatabaseAccess, que também conhece o banco concreto. A fronteira passa abaixo da interface e cruza a relação de implementação: o contrato permanece do lado das regras e o acesso concreto fica do outro lado. As duas setas que saem de DatabaseAccess indicam que os demais elementos representados não precisam conhecer essa classe. O texto esclarece que o diagrama é simbólico; aplicações reais terão várias regras, interfaces e implementações seguindo o mesmo padrão. A página prepara a visão desses elementos agrupados em componentes.

---

<a id="pagina-0139"></a>

## Página 0139 — O banco depende das regras, e não o contrário

A figura 17.3 agrupa os elementos em dois componentes e aponta a dependência do banco para as regras de negócio. As interfaces de acesso pertencem às regras; suas implementações ficam no componente de persistência, cujo código traduz chamadas em consultas. Essa direção permite trocar Oracle, MySQL, outros bancos ou arquivos sem obrigar as regras a conhecer a tecnologia. Também permite escrevê-las e testá-las antes da decisão de armazenamento. Ao final, o texto questiona a confusão entre o sistema e sua interface gráfica e introduz a independência em relação à entrada e à saída.

---

<a id="pagina-0140"></a>

## Página 0140 — Interface como plugin de um modelo independente

O exemplo de um videogame distingue a experiência visual e sonora do modelo que calcula seus acontecimentos. Esse modelo pode executar sem exibição na tela; logo, a interface deve depender das regras, conforme a figura 17.4, preservando a possibilidade de substituição. A combinação dessa fronteira com a do banco cria o padrão de arquitetura de plugins. O núcleo de negócio permanece separado de componentes opcionais ou sujeitos a diferentes implementações. A página apresenta esse padrão como um meio de construir sistemas sustentáveis e escaláveis, em que detalhes tecnológicos se conectam a um centro independente.

---

<a id="pagina-0141"></a>

## Página 0141 — Plugins tornam substituições viáveis

O desenho da figura 17.5 mostra banco e interface conectados às regras de negócio por dependências dirigidas para o núcleo. Essa organização admite interfaces web, de console ou cliente-servidor, além de diferentes tecnologias de persistência. O autor ressalta que trocar uma implementação pode exigir trabalho significativo e ajustes na comunicação; a arquitetura torna a mudança praticável, sem prometer que seja trivial. Em seguida, usa ReSharper e Visual Studio para mostrar uma relação assimétrica: o plugin depende da plataforma, de modo que alterações na plataforma podem afetá-lo, enquanto seu desenvolvimento não exige mudanças na plataforma.

---

<a id="pagina-0142"></a>

## Página 0142 — Responsabilidade única orienta onde traçar fronteiras

A dependência de ReSharper em relação ao Visual Studio exemplifica a assimetria desejada entre módulos: certos componentes devem permanecer protegidos de alterações em outros. Uma arquitetura de plugins estabelece barreiras à propagação de mudanças, como as de páginas web ou esquemas de banco para as regras de negócio. As fronteiras devem acompanhar eixos de mudança, separando partes que evoluem em ritmos e por razões diferentes. Essa orientação retoma a responsabilidade única. A conclusão propõe organizar regras centrais e plugins com todas as dependências apontando para o negócio, aplicando inversão de dependência e abstrações estáveis.

---

<a id="pagina-0144"></a>

## Página 0144 — Anatomia das fronteiras e dependências do código

O capítulo 18 começa descrevendo arquitetura como componentes e as fronteiras que os separam. Durante a execução, atravessar uma fronteira pode ser apenas chamar uma função e transmitir dados. A questão arquitetural decisiva está nas dependências do código-fonte, pois mudanças podem exigir alterações, recompilação e nova implantação de outros módulos. As fronteiras buscam conter essa propagação. A forma mais simples não tem uma divisão física rígida: consiste em separar disciplinadamente funções e dados dentro de um processo e espaço de memória, modalidade antes denominada desacoplamento no código-fonte.

---

<a id="pagina-0145"></a>

## Página 0145 — Um monólito também contém fronteiras relevantes

Um executável único pode preservar componentes desenvolvidos de forma independente, mesmo que suas fronteiras não apareçam na implantação. O texto destaca o papel do polimorfismo dinâmico para controlar dependências internas. A figura 18.1 mostra o caso mais simples: um cliente de baixo nível chama um serviço de nível superior, e tanto o fluxo de execução quanto as dependências do código apontam para esse nível superior. A estrutura dos dados transmitidos também pertence ao lado chamado. Quando um cliente de alto nível precisa chamar um serviço inferior, será necessário inverter a dependência em relação ao fluxo de controle.

---

<a id="pagina-0146"></a>

## Página 0146 — Inversão na fronteira e componentes implantáveis

A figura 18.2 mostra o cliente de alto nível chamando uma implementação inferior por meio de uma interface que pertence ao seu próprio lado da fronteira. A estrutura de dados também fica no nível superior, para onde apontam todas as dependências do código. Mesmo em monólitos, isso favorece equipes independentes e proteção contra detalhes inferiores, mantendo chamadas rápidas e baratas. A página introduz então bibliotecas e unidades implantáveis, como DLLs, JARs e Gems: sua entrega pode reunir binários sem recompilar. As regras de separação e dependência permanecem semelhantes às do monólito.

---

<a id="pagina-0147"></a>

## Página 0147 — Threads e processos locais têm papéis distintos

Chamadas entre componentes implantáveis continuam baratas, mesmo com algum custo inicial de ligação dinâmica. Threads organizam a ordem e o agendamento da execução, mas não constituem fronteiras arquiteturais ou unidades de implantação. Processos locais criam uma separação física mais forte, com espaços de memória distintos e comunicação por sockets, filas ou mecanismos do sistema operacional. Cada processo pode conter um monólito ou componentes dinâmicos. As dependências devem continuar apontando para níveis superiores: estes não devem conhecer nomes, endereços ou chaves de localização dos inferiores. A comunicação entre processos tem custo suficiente para exigir controle de sua frequência.

---

<a id="pagina-0148"></a>

## Página 0148 — Serviços e a combinação de tipos de fronteira

Serviços presumem comunicação por rede e não dependem de estarem no mesmo processador. Suas chamadas têm latência muito maior que chamadas de função, o que exige reduzir interações excessivas. A orientação das dependências continua válida: serviços inferiores devem conectar-se aos superiores, cujo código não deve conter detalhes físicos como o URI dos inferiores. A conclusão observa que sistemas normalmente combinam fronteiras de serviços, processos locais e componentes internos. Assim, chamadas locais frequentes convivem com comunicações sensíveis à latência. Uma nota distingue o polimorfismo estático do dinâmico quanto à proteção contra recompilação e reimplantação.

---

<a id="pagina-0149"></a>

## Página 0149 — Políticas agrupadas conforme suas mudanças

O capítulo 19 apresenta programas como políticas detalhadas de transformação de entradas em saídas. Sistemas maiores contêm políticas diversas, como cálculos de negócio, formatação de relatórios e validação. A arquitetura deve separá-las e reagrupar aquelas que mudam pelas mesmas razões e nos mesmos momentos, colocando em componentes distintos as que pertencem a níveis diferentes. Esses componentes formam idealmente um grafo dirigido sem ciclos. As arestas representam dependências do código necessárias à compilação, exemplificadas por importações em Java, declarações using em C# e require em Ruby; não representam simplesmente a sequência de execução.

---

<a id="pagina-0151"></a>

## Página 0151 — A política de criptografia controla seus contratos

O exemplo iniciado antes é inadequado porque a função de alto nível depende diretamente de leitura e escrita inferiores. A alternativa da figura 19.2 reúne Encrypt e as interfaces CharReader e CharWriter dentro da mesma fronteira, enquanto ConsoleReader e ConsoleWriter ficam fora e dependem desses contratos. Assim, a criptografia pode ser reutilizada em diferentes contextos de entrada e saída. O texto relaciona essa separação aos motivos e ritmos de mudança: detalhes próximos aos dispositivos tendem a mudar mais frequentemente, enquanto políticas centrais mudam por razões mais substanciais. Dependências voltadas para cima limitam a propagação dessas mudanças.

---

<a id="pagina-0154"></a>

## Página 0154 — Entidades reúnem dados e regras essenciais

Uma entidade encapsula regras críticas e os dados sobre os quais elas operam. A figura 20.1 exemplifica Loan com principal, taxa e período, oferecendo operações para registrar pagamento, aplicar juros e cobrar multa por atraso. Esse módulo representa um conceito do negócio independente de banco, interface, frameworks ou distribuição entre computadores. Não exige linguagem orientada a objetos: basta reunir regras e dados em uma unidade separada. Ao final, a página distingue outro tipo de regra, associado aos casos de uso, que organiza e limita o funcionamento específico de um sistema automatizado e não faria sentido no processo manual.

---

<a id="pagina-0155"></a>

## Página 0155 — Casos de uso coordenam regras e entidades

O exemplo bancário exige validar os dados de contato e consultar a pontuação de crédito antes de estimar um empréstimo. A figura 20.2 prevê recusa abaixo de 500 pontos; caso contrário, cria o cliente e inicia a estimativa. Um caso de uso descreve entradas, saídas e etapas próprias da aplicação, determinando como e quando acionar regras das entidades. Não define a aparência da interface nem se o acesso ocorre por web, console ou serviço. Pode ser representado por um objeto com funções de coordenação, dados de entrada e saída e referências às entidades utilizadas.

---

<a id="pagina-0156"></a>

## Página 0156 — Entidades independentes e modelos de entrada e saída

Casos de uso dependem de entidades, enquanto estas desconhecem os fluxos que as coordenam. As entidades são mais gerais e distantes da entrada e saída; os casos de uso pertencem a uma aplicação específica. Estes devem receber e devolver estruturas simples, sem herdar de contratos HTTP ou carregar dependências de frameworks. Também não convém reutilizar entidades como modelos de requisição e resposta: são objetos com finalidades e motivos de mudança distintos. A conclusão apresenta as regras de negócio como o núcleo valioso do sistema, que deve permanecer independente de interface e banco para facilitar sua reutilização.

---

<a id="pagina-0158"></a>

## Página 0158 — A arquitetura deve revelar a finalidade da aplicação

O capítulo 21 usa plantas de edifícios para explicar que uma arquitetura comunica sua intenção. A disposição de entrada, cozinha e salas revela uma residência; balcões, áreas de leitura e estantes revelam uma biblioteca. O mesmo deveria ocorrer com diretórios e arquivos centrais de software: eles devem tornar visível que se trata de um sistema de saúde, contabilidade ou inventário. O contraste proposto é com repositórios cuja primeira impressão revela apenas Rails, Spring/Hibernate ou ASP. A página introduz, assim, a arquitetura que anuncia seus casos de uso.

---

<a id="pagina-0160"></a>

## Página 0160 — Arquitetura reconhecível e testável sem infraestrutura

O autor recomenda avaliar frameworks com senso crítico, considerando benefícios, custos e maneiras de preservar a centralidade dos casos de uso. Quando essa separação existe, regras e casos de uso podem ser testados sem servidor web, conexão com banco ou o próprio framework. Entidades permanecem objetos simples e casos de uso coordenam sua atuação. A conclusão volta à legibilidade da estrutura: ao abrir um repositório, uma pessoa deve reconhecer a finalidade do sistema e compreender seus casos de uso antes de descobrir como ele é entregue. Visualizações e controladores aparecem como decisões secundárias que podem ser adiadas.

---

<a id="pagina-0162"></a>

## Página 0162 — A regra de dependência da arquitetura limpa

A arquitetura limpa reúne independência de interface, banco e demais agentes externos. A figura 22.1 representa entidades no centro, seguidas por casos de uso, adaptadores de interface e frameworks/dispositivos na periferia. Quanto mais interna a camada, mais elevada a política; as externas contêm mecanismos. A regra central determina que dependências do código apontem somente para dentro. Código interno não deve mencionar funções, classes, variáveis ou formatos declarados externamente. Isso inclui estruturas produzidas por frameworks: permitir sua entrada vincularia as regras a detalhes que deveriam permanecer substituíveis.

---

<a id="pagina-0163"></a>

## Página 0163 — Responsabilidades das três camadas internas

Entidades encapsulam regras gerais da empresa ou do negócio e devem resistir a mudanças operacionais externas. Casos de uso contêm regras específicas da aplicação e coordenam entidades para alcançar seus objetivos; mudanças em interface ou banco não devem afetá-los, mas alterações no próprio fluxo funcional podem fazê-lo. Adaptadores de interface convertem os dados entre os formatos convenientes ao núcleo e os exigidos por agentes externos. Nessa camada ficam controladores, apresentadores e visualizações, além dos adaptadores de persistência e serviços. Consultas SQL devem permanecer na parte responsável pelo banco, sem aparecer nas camadas internas.

---

<a id="pagina-0164"></a>

## Página 0164 — Detalhes externos e inversão ao cruzar camadas

Frameworks, banco e ferramentas ficam na camada mais externa, acompanhados do código de integração necessário. O modelo não exige exatamente quatro círculos: o que permanece obrigatório é orientar as dependências para políticas cada vez mais internas e abstratas. O fluxo de controle pode ir do controlador ao caso de uso e depois ao apresentador sem inverter essa orientação do código. Para isso, o caso de uso chama uma interface interna de saída que o apresentador implementa. Dados atravessam fronteiras em estruturas simples e isoladas, sem transportar dependências externas por meio de entidades ou registros de banco.

---

<a id="pagina-0165"></a>

## Página 0165 — Um fluxo completo entre controlador, caso de uso e apresentador

Formatos retornados por frameworks de banco não devem atravessar a fronteira para dentro; os dados devem assumir a forma mais conveniente ao núcleo. A figura 22.2 mostra o controlador criando dados simples e chamando o interactor por InputBoundary. O interactor coordena entidades, utiliza DataAccessInterface para obter dados e envia OutputData ao apresentador por OutputBoundary. O apresentador converte essa saída em ViewModel, com datas e valores monetários já formatados, nomes de elementos e indicadores de habilitação. A estrutura preserva dependências internas enquanto distribui a responsabilidade por entrada, negócio, persistência e apresentação.

---

<a id="pagina-0166"></a>

## Página 0166 — Camadas testáveis e detalhes substituíveis

A continuação do exemplo deixa para a visualização apenas transferir os dados preparados no ViewModel para o HTML. Todas as dependências que atravessam fronteiras apontam para dentro. A conclusão associa a separação em camadas e a regra de dependência à testabilidade do sistema. Também destaca que elementos externos envelhecidos, como banco de dados e framework web, podem ser substituídos com menos dificuldade quando sua tecnologia não contamina as regras centrais.

---

<a id="pagina-0174"></a>

## Página 0174 — O jogo revela fronteiras além de três componentes

O capítulo 25 questiona a visão de todo sistema como interface, regras de negócio e banco. Essa divisão pode servir a casos simples, mas frequentemente omite outras separações. O exemplo escolhido é Hunt the Wumpus, jogo textual de 1972 em que o jogador explora cavernas, caça uma criatura e evita perigos por comandos de movimento e disparo. A primeira variação considerada é o idioma. Para atender mercados diferentes, as regras do jogo devem usar uma API independente da língua, deixando a tradução de comandos e respostas sob responsabilidade da interface.

---

<a id="pagina-0175"></a>

## Página 0175 — Idiomas e armazenamento dependem das regras do jogo

A figura 25.1 apresenta interfaces em inglês e espanhol reutilizando o mesmo componente de regras, sem que ele conheça o idioma utilizado. A mesma lógica vale para o armazenamento do estado: memória, flash ou nuvem são alternativas que não devem aparecer no núcleo. Uma API separa as regras dos mecanismos de persistência, e a figura 25.2 orienta as dependências dessas implementações para GameRules. Embora o cenário aceite entidades, casos de uso, fronteiras e dados da arquitetura limpa, a página termina perguntando se todas as separações arquiteturalmente relevantes já foram identificadas.

---

<a id="pagina-0176"></a>

## Página 0176 — Idioma e meio de entrega são eixos independentes

Além do idioma, a interface textual pode variar entre console, SMS ou aplicação de conversa. Surge então uma fronteira entre a tradução linguística e o mecanismo de entrega. A figura 25.3 separa GameRules, Language, TextDelivery e DataStorage, com implementações como English, Spanish, SMS, Console, CloudData e FlashData. As APIs pertencem aos componentes que as utilizam e às políticas superiores, não aos detalhes que as implementam. Interfaces polimórficas permitem comunicação nos dois sentidos mantendo a propriedade e a direção corretas das dependências. A estrutura torna explícitas várias possibilidades de mudança antes misturadas.

---

<a id="pagina-0177"></a>

## Página 0177 — Fluxos distintos convergem para políticas superiores

Eliminando as variantes concretas, a figura 25.4 mostra TextDelivery dependendo de Language, que depende de GameRules, enquanto DataStorage também aponta para GameRules. As regras ocupam o topo por conter as políticas mais elevadas. O fluxo de informação, porém, sobe e desce: entradas são traduzidas em comandos, processadas e persistidas; respostas retornam ao jogador pelo caminho de idioma e entrega. Formam-se dois fluxos, comunicação e persistência, que convergem nas regras. A página amplia o exemplo com a possibilidade de jogo em rede entre vários participantes, exigindo um terceiro fluxo arquitetural.

---

<a id="pagina-0178"></a>

## Página 0178 — Rede e subdivisões dentro das regras do jogo

A figura 25.5 acrescenta Network a Language e DataStorage, todos dependendo de GameRules. Sistemas mais complexos podem ter muitos fluxos, e eles não precisam terminar em um único componente. O texto divide as próprias regras do jogo: a mecânica conhece o mapa, objetos, cavernas e deslocamentos; uma política superior acompanha saúde, ganhos, perdas e vitória ou derrota. Eventos como encontrar alimento ou cair em um poço conectam esses níveis. A separação mostra que políticas aparentemente reunidas em um único núcleo também podem ter responsabilidades e níveis distintos.

---

<a id="pagina-0179"></a>

## Página 0179 — Uma política superior pode tornar-se serviço remoto

A figura 25.6 coloca PlayerManagement acima de MoveManagement, que recebe dependências dos componentes de idioma, armazenamento e rede. O texto pergunta se essa divisão exige uma fronteira própria e amplia o cenário para um jogo massivo: movimentos são tratados no computador do participante, enquanto o estado do jogador é gerido por um servidor. A figura 25.7 introduz implementação remota, proxy e comunicação de rede sob a API de PlayerManagement. Nesse contexto, a separação passa a ser uma fronteira arquitetural completa. O início da conclusão ressalta o caráter deliberadamente extrapolado do exemplo simples.

---

<a id="pagina-0220"></a>

## Página 0220 — Estudo de caso de uma plataforma de venda de vídeos

O capítulo 33 propõe reunir os princípios em um caso pequeno de arquitetura, inspirado na venda de vídeos educacionais do autor. Pessoas físicas podem pagar por streaming ou por download permanente, este mais caro. Empresas compram licenças de streaming em quantidade, com descontos; quem compra nem sempre é quem assiste. Autores fornecem arquivos dos vídeos, descrições e materiais complementares, como avaliações, exercícios, soluções e código-fonte. A página define essas regras e papéis iniciais para que as decisões arquiteturais seguintes partam do produto e de seus usos, em vez de tecnologias específicas.

---

<a id="pagina-0221"></a>

## Página 0221 — Quatro atores orientam a análise dos casos de uso

Administradores criam séries, incluem ou removem vídeos e definem preços de licenças. A figura 33.1 reúne quatro atores: autor, comprador, espectador e administrador. Os autores enviam vídeo, avaliação e descrição; compradores adquirem licenças de download, streaming ou uso empresarial; espectadores consultam catálogo, assistem e baixam vídeos; administradores mantêm catálogo e preços. O desenho também apresenta casos gerais de compra de licença e consulta de catálogo. Segundo a responsabilidade única, esses quatro atores representam fontes distintas de mudança e devem orientar a separação do sistema, reduzindo interferências entre suas necessidades.

---

<a id="pagina-0222"></a>

## Página 0222 — Dos atores aos componentes e abstrações de catálogo

A divisão deve evitar que alterações para um ator afetem os demais. O autor esclarece que a lista de casos de uso é propositalmente incompleta, omitindo funções como login para manter o estudo pequeno. Casos abstratos expressam políticas gerais especializadas por outros; consultar catálogo como comprador e como espectador compartilham uma base comum. A arquitetura preliminar separa visualizações, apresentadores, interactors e controladores, subdividindo cada categoria por ator. Componentes especiais de catálogo acomodam as abstrações compartilhadas. Cada unidade pode vir a ser um JAR ou DLL, preservando opções de compilação e entrega.
