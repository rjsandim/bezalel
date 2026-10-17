# Evolução, composição e serviços

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill; não dependem do PDF nem de arquivos externos.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0171 — Fronteiras parciais reservam uma opção futura](#pagina-0171)
- [Página 0172 — Economia administrativa e risco de erosão da separação](#pagina-0172)
- [Página 0173 — Fachadas oferecem uma separação mais fraca](#pagina-0173)
- [Página 0180 — Decidir sobre fronteiras exige acompanhamento contínuo](#pagina-0180)
- [Página 0181 — Main monta o sistema e entrega o controle](#pagina-0181)
- [Página 0184 — Main como plugin para configurações diferentes](#pagina-0184)
- [Página 0185 — Serviços, por si sós, não definem arquitetura](#pagina-0185)
- [Página 0186 — Dados compartilhados mantêm serviços acoplados](#pagina-0186)
- [Página 0187 — O agregador de táxis expõe limites da independência](#pagina-0187)
- [Página 0188 — A entrega de gatos atravessa todos os serviços](#pagina-0188)
- [Página 0189 — Extensões polimórficas isolam funcionalidades transversais](#pagina-0189)
- [Página 0190 — Fronteiras podem atravessar serviços](#pagina-0190)
- [Página 0191 — Arquitetura é definida pelas fronteiras e dependências](#pagina-0191)
- [Página 0223 — Separação lógica preserva opções de implantação](#pagina-0223)
- [Página 0224 — Atores e níveis de política definem duas separações](#pagina-0224)
- [Página 0256 — Uma adaptação de modems e grandes reescritas fracassadas](#pagina-0256)
- [Página 0257 — Divergência entre versões e dificuldade de reescrever](#pagina-0257)
- [Página 0262 — Arquiteturas diferentes com resultados igualmente bons](#pagina-0262)
- [Página 0271 — Dependências mal orientadas e arquitetura excessiva no ROSE](#pagina-0271)
- [Página 0272 — A promessa prematura de um framework reutilizável](#pagina-0272)
- [Página 0273 — Reutilização comprovada por múltiplas aplicações](#pagina-0273)

<a id="pagina-0171"></a>

## Página 0171 — Fronteiras parciais reservam uma opção futura

O capítulo 24 reconhece que fronteiras completas têm custo de construção e manutenção: exigem interfaces polimórficas, estruturas de entrada e saída e controle das dependências para permitir compilar e implantar cada lado separadamente. Em alguns casos, esse investimento parece excessivo, mas a separação pode vir a ser necessária. Uma fronteira parcial preserva essa possibilidade, apesar da tensão com a ideia de não implementar algo antes de precisar. A primeira técnica faz toda a preparação de interfaces e dados, mas mantém ambos os lados compilados e implantados juntos em um único componente.

---

<a id="pagina-0172"></a>

## Página 0172 — Economia administrativa e risco de erosão da separação

Manter componentes preparados para separação, mas entregues juntos, não reduz o trabalho de desenho e código; reduz versionamento e gestão de lançamentos. O FitNesse usou essa estratégia para o servidor web, preservando o download de um único JAR. Como a separação definitiva nunca foi necessária, dependências inadequadas apareceram e tornaram sua extração futura mais trabalhosa. Outra opção é a fronteira unidimensional do padrão Strategy: o cliente usa ServiceBoundary e ServiceImpl a implementa. Isso prepara uma inversão de dependência, mas o diagrama alerta que canais de retorno diretos podem enfraquecer o isolamento.

---

<a id="pagina-0173"></a>

## Página 0173 — Fachadas oferecem uma separação mais fraca

Sem interfaces recíprocas, evitar acessos indevidos exige disciplina. A fachada representa uma fronteira ainda mais simples: uma classe expõe operações e encaminha chamadas aos serviços que o cliente não deveria acessar diretamente. Como não há inversão de dependência, o cliente continua dependendo transitivamente desses serviços e pode precisar ser recompilado quando eles mudam. Também é fácil criar acessos que contornem a fachada. A conclusão apresenta as três técnicas como exemplos com custos e benefícios distintos, adequados a determinados contextos. Cabe ao arquiteto decidir onde reservar fronteiras futuras e quanto implementá-las desde já.

---

<a id="pagina-0180"></a>

## Página 0180 — Decidir sobre fronteiras exige acompanhamento contínuo

O jogo simples foi usado como representação de sistemas maiores, não como recomendação para aplicar toda essa estrutura a poucas centenas de linhas. Fronteiras completas custam caro; acrescentá-las depois também pode ser caro e arriscado. O autor reconhece a prudência do YAGNI e os riscos do excesso de engenharia, mas exige julgamento sobre separações completas, parciais ou dispensáveis. Essa decisão não ocorre apenas no início: o arquiteto observa a evolução, identifica sinais de atrito e reavalia custos. O momento desejado é aquele em que implementar a fronteira passa a custar menos que continuar ignorando-a.

---

<a id="pagina-0181"></a>

## Página 0181 — Main monta o sistema e entrega o controle

O capítulo 26 chama de Main o componente que cria, coordena e supervisiona os demais. Apesar de iniciar o sistema, ele representa a política de nível mais baixo, dependente dos detalhes de montagem e conhecido essencialmente pelo sistema operacional. Sua função é construir fábricas, estratégias e recursos globais e transferir o controle às partes abstratas de alto nível. Frameworks de injeção de dependência devem atuar nessa montagem; depois, as dependências são distribuídas normalmente. A página prepara um exemplo de Hunt the Wumpus em que Main concentra textos que o núcleo do jogo não precisa conhecer.

---

<a id="pagina-0184"></a>

## Página 0184 — Main como plugin para configurações diferentes

O restante de createMap estabelece conexões nas quatro direções, posiciona jogador, Wumpus, morcegos e poços e define cinco flechas iniciais. O exemplo mostra Main preparando condições concretas antes de entregar o controle às políticas do jogo. A conclusão o trata como plugin externo da aplicação: reúne recursos e configurações, sem ocupar o núcleo. Essa perspectiva permite diferentes componentes Main para desenvolvimento, testes, produção, países, jurisdições ou clientes. Manter a montagem atrás de uma fronteira arquitetural simplifica a administração dessas variações sem misturá-las às regras gerais.

---

<a id="pagina-0185"></a>

## Página 0185 — Serviços, por si sós, não definem arquitetura

O capítulo 27 questiona duas promessas atribuídas a serviços e microsserviços: desacoplamento forte e independência de desenvolvimento e implantação. Ambas são apresentadas como verdades apenas parciais. Arquitetura é definida por fronteiras entre políticas de alto nível e detalhes, obedecendo à regra de dependência. Um serviço que apenas separa comportamentos pode ser comparável a uma chamada de função cara, sem relevância arquitetural própria. Isso não elimina possíveis benefícios de distribuir funcionalidades entre processos e plataformas; apenas esclarece que a escolha por serviços não estabelece automaticamente uma boa estrutura arquitetural.

---

<a id="pagina-0186"></a>

## Página 0186 — Dados compartilhados mantêm serviços acoplados

Assim como nem toda chamada de função atravessa uma fronteira arquitetural, nem toda interação entre serviços o faz. Processos separados impedem acesso direto às variáveis, mas podem compartilhar recursos e permanecer fortemente ligados aos dados trocados. Acrescentar um campo exige modificar os serviços que o usam e preservar acordo sobre seu significado. Contratos de serviço também não são necessariamente mais rigorosos que interfaces de função. A página começa a examinar outra promessa: equipes dedicadas poderiam desenvolver, implantar e operar muitos serviços independentemente. O autor reconhece algum valor nessa ideia, mas prepara uma análise de seus limites.

---

<a id="pagina-0187"></a>

## Página 0187 — O agregador de táxis expõe limites da independência

Sistemas de grande porte também podem ser construídos com monólitos e componentes; serviços não são a única forma de crescer. Quando compartilham dados ou comportamentos, suas equipes precisam coordenar desenvolvimento, implantação e operação. O exemplo apresenta um agregador de táxis distribuído em serviços: TaxiUI recebe pedidos; TaxiFinder consulta fornecedores e guarda candidatos; TaxiSelector aplica critérios de preço, tempo, luxo e experiência; TaxiDispatcher solicita o carro escolhido. Cada grupo de serviços pertence a uma equipe. A estrutura parece funcionar bem durante mais de um ano, preparando o contraste com uma futura mudança transversal.

---

<a id="pagina-0188"></a>

## Página 0188 — A entrega de gatos atravessa todos os serviços

Uma nova oferta de entrega de gatos exige localizar pontos de coleta, selecionar fornecedores participantes e excluir motoristas alérgicos. Também impede destinar a clientes alérgicos veículos usados para esse transporte nos três dias anteriores. Essas exigências atingem todos os serviços do agregador e obrigam coordenação entre equipes e implantações. O problema decorre de uma funcionalidade transversal, comum a qualquer sistema. Como alternativa, o autor propõe aplicar SOLID e extensão polimórfica: preservar lógica genérica nas classes-base e separar comportamentos de corridas e de entregas de gatos em componentes Rides e Kittens, seguindo a regra de dependência.

---

<a id="pagina-0189"></a>

## Página 0189 — Extensões polimórficas isolam funcionalidades transversais

Na solução da figura 27.2, componentes Rides e Kittens implementam variações das abstrações de busca, seleção, despacho e fornecimento. Fábricas controladas pela interface criam essas implementações. A inclusão da entrega de gatos exige modificar TaxiUI e acrescentar uma unidade carregável, como JAR, Gem ou DLL, sem alterar os demais componentes existentes. A funcionalidade pode assim ser desenvolvida e implantada separadamente. A página pergunta se o mesmo desenho vale para serviços e responde que sim: eles também podem conter componentes orientados por SOLID, em vez de funcionar como pequenos monólitos indivisíveis.

---

<a id="pagina-0190"></a>

## Página 0190 — Fronteiras podem atravessar serviços

Um serviço Java pode reunir classes abstratas em arquivos JAR e receber novas funcionalidades em outros JARs que as estendem. A implantação dessas extensões consiste em acrescentar unidades ao caminho de carregamento, preservando os componentes existentes e aplicando o princípio aberto-fechado. A figura 27.3 mantém os serviços do agregador, mas mostra variantes de corridas e de gatos dentro das funções de busca, seleção, despacho e fornecimento. A lição é que as fronteiras arquiteturais podem atravessar os serviços e dividi-los internamente, em vez de coincidir com as suas separações físicas.

---

<a id="pagina-0191"></a>

## Página 0191 — Arquitetura é definida pelas fronteiras e dependências

A figura 27.4 exemplifica TaxiSelector como abstração comum a RideSelector e KittenSelector, organizados em componentes separados. Esse desenho interno permite lidar com funcionalidades transversais seguindo a regra de dependência. A conclusão diferencia arquitetura de mecanismos de execução e comunicação: serviços podem ajudar na escalabilidade e no desenvolvimento, mas não determinam por si a estrutura arquitetural. Um serviço pode corresponder a um componente cercado por uma fronteira, conter vários componentes separados ou estar tão acoplado aos clientes que sua divisão não tenha significado arquitetural relevante.

---

<a id="pagina-0223"></a>

## Página 0223 — Separação lógica preserva opções de implantação

A figura 33.2 organiza quatro grupos de atores em visualizações, apresentadores, interactors e controladores, acrescentando abstrações de catálogo, gateways e banco. O autor manteria essa divisão no ambiente de compilação para possibilitar entregáveis independentes, mas não exige implantar um arquivo por componente. Propõe agrupamentos alternativos: cinco unidades por categoria técnica, uma combinação de visualizações e apresentadores, ou apenas duas unidades separando apresentação do restante. Preservar essas opções permite ajustar a implantação aos padrões reais de mudança do sistema, sem perder a organização arquitetural mais detalhada do código.

---

<a id="pagina-0224"></a>

## Página 0224 — Atores e níveis de política definem duas separações

No diagrama anterior, o fluxo de controle segue dos controladores para interactors, apresentadores e visualizações. As dependências não seguem sempre esse sentido: relações de uso acompanham o fluxo, enquanto herança o inverte para manter as setas voltadas às políticas superiores. Isso impede que detalhes inferiores propaguem alterações para o núcleo. A conclusão identifica duas dimensões: separar atores pela responsabilidade única e separar níveis pela regra de dependência. As primeiras correspondem a motivos de mudança; os segundos, a ritmos distintos. Depois de estruturar o código, a composição dos entregáveis pode variar conforme as condições de implantação.

---

<a id="pagina-0256"></a>

## Página 0256 — Uma adaptação de modems e grandes reescritas fracassadas

Os novos modems chegaram com comandos totalmente diferentes, mas o sistema precisava operar simultaneamente com os antigos. Para evitar modificar centenas de trechos, a equipe alterou uma rotina comum de comunicação para reconhecer sequências destinadas ao modem anterior e traduzi-las para novos endereços, tempos e bits. Embora funcionasse, o improviso evidenciou a necessidade de abstrair interfaces e isolar hardware das regras de negócio. A narrativa segue para a tentativa de reescrever o SAC em C e UNIX. Uma primeira equipe consumiu anos-pessoa sem entregar resultado; outra, usando hardware 80286 próprio, prolongou-se por anos. O autor não afirma ter confirmado a implantação final desse redesenho.

---

<a id="pagina-0257"></a>

## Página 0257 — Divergência entre versões e dificuldade de reescrever

A manutenção contínua do sistema antigo dificultava que a equipe de reescrita o alcançasse. A expansão para a Europa agravou a situação: diferenças nas redes telefônicas e na organização do trabalho levaram uma equipe britânica a criar uma versão própria do SAC. Sem integração sistemática, correções de um lado do Atlântico tornaram-se difíceis de transferir ao outro. Mesmo após melhorar a conexão entre escritórios, três tentativas de reunificar as versões falharam diante das diferenças acumuladas e do mercado em mudança. O redesenho em C passou a ter de contemplar também essa duplicidade. Ao final, começa o relato da procura por uma linguagem mais conveniente para a plataforma 8085.

---

<a id="pagina-0262"></a>

## Página 0262 — Arquiteturas diferentes com resultados igualmente bons

Embora DLU e DRU usassem o mesmo processador, linguagem e sistema de tarefas, seus autores escolheram estruturas opostas. Na DLU, pequenas tarefas especializadas transferiam dados por filas, compondo um fluxo semelhante a uma linha de montagem, com ramificações e junções. Na DRU, cada terminal tinha uma tarefa maior que executava todo o trabalho, como um profissional responsável por construir um produto completo. Ambas as soluções funcionaram bem, levando o autor a reconhecer que arquiteturas muito diferentes podem ser igualmente eficazes. A equipe também precisou criar seu próprio protocolo de comunicação. Ao final, inicia-se o relato do VRS e do processo usado para localizar defeitos em cabos telefônicos.

---

<a id="pagina-0271"></a>

## Página 0271 — Dependências mal orientadas e arquitetura excessiva no ROSE

Apesar de disciplinadas, as dependências do ROSE seguiam o fluxo de controle: interface gráfica, representação, regras de manipulação e banco. Elas não apontavam para as políticas de alto nível defendidas no livro. O banco orientado a objetos prometia persistência quase invisível, mas trouxe lentidão, invasividade e custos, prejudicando o trabalho. O autor considera ainda mais grave o excesso de camadas, cujo esforço de comunicação reduzia a produtividade. Após grande investimento e duas versões pouco expressivas, o produto foi substituído por uma aplicação menor. A lição é adequar a arquitetura ao tamanho do problema. A página introduz então o trabalho de consultoria para informatizar exames de habilitação de arquitetos.

---

<a id="pagina-0272"></a>

## Página 0272 — A promessa prematura de um framework reutilizável

O exame de habilitação de arquitetos exigia soluções gráficas para problemas de projeto, avaliadas posteriormente por especialistas em encontros caros e demorados. A proposta de automação incluía 18 aplicações gráficas e 18 avaliadores. O autor e Jim Newkirk identificaram semelhanças e prometeram que um framework inicial tornaria as demais entregas rápidas. Começaram pela aplicação mais complexa, Vignette Grande. Após um ano, tinham cerca de 45 mil linhas de framework e seis mil de aplicação. Porém, quando outros desenvolvedores iniciaram novas vinhetas, surgiram incompatibilidades sutis. A página mostra que a expectativa de reutilização baseada em um único caso ainda não havia sido comprovada por aplicações diferentes.

---

<a id="pagina-0273"></a>

## Página 0273 — Reutilização comprovada por múltiplas aplicações

A equipe renegociou o prazo e refez o framework desenvolvendo quatro vinhetas simultaneamente, aproveitando ideias anteriores apenas quando serviam a todas. Nas interfaces gráficas, as aplicações dependiam das políticas do framework; na avaliação, o framework dependia das políticas específicas das vinhetas. Embora os executáveis fossem ligados estaticamente, essas direções correspondiam à Regra da Dependência. Depois dessa experiência conjunta, as aplicações seguintes realmente passaram a sair em poucas semanas, e a equipe cumpriu os compromissos ajustados. A lição é que um framework reutilizável precisa primeiro ser utilizável e evoluir com vários consumidores reais. A página encerra o apêndice autobiográfico, limitado propositalmente ao início dos anos 1990.
