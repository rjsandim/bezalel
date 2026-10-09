# Tecnologias e proteção das fronteiras no código

[Voltar ao mapa de fontes](../fontes.md)

Cópias dos resumos selecionados de *Clean Architecture*, em português. Os números indicam a posição física das páginas no PDF de origem. Os textos abaixo estão incluídos integralmente nesta skill; não dependem do PDF nem de arquivos externos.

Leia apenas a página ou exemplo relevante. Busque pelo título ou por `Página NNNN` para localizar um trecho.

## Conteúdo

- [Página 0210 — A lentidão dos discos explica sistemas de acesso a dados](#pagina-0210)
- [Página 0211 — Persistência e representação em memória têm papéis diferentes](#pagina-0211)
- [Página 0212 — Uma exigência comercial pode existir sem necessidade técnica](#pagina-0212)
- [Página 0213 — Atender ao mercado sem entregar o núcleo ao banco](#pagina-0213)
- [Página 0216 — Casos de uso criam uma fronteira independente da interface](#pagina-0216)
- [Página 0217 — Frameworks resolvem problemas que podem coincidir com os seus](#pagina-0217)
- [Página 0218 — O compromisso com um framework é assimétrico](#pagina-0218)
- [Página 0219 — Manter frameworks fora do núcleo é uma escolha consciente](#pagina-0219)
- [Página 0225 — Organização do código precisa sustentar o desenho](#pagina-0225)
- [Página 0227 — Pacotes por funcionalidade tornam o domínio visível](#pagina-0227)
- [Página 0229 — Infraestrutura depende do domínio e usa sua linguagem](#pagina-0229)
- [Página 0230 — Portas e adaptadores no exemplo dos pedidos](#pagina-0230)
- [Página 0231 — Camadas públicas permitem contornar a lógica de negócio](#pagina-0231)
- [Página 0232 — Regras arquiteturais precisam de aplicação verificável](#pagina-0232)
- [Página 0233 — Pacotes por componente buscam fronteiras impostas pelo compilador](#pagina-0233)
- [Página 0234 — Componente encapsula funcionalidade atrás de uma interface](#pagina-0234)
- [Página 0235 — Organização de pacotes sem encapsulamento é insuficiente](#pagina-0235)
- [Página 0236 — A visibilidade muda o efeito de cada organização](#pagina-0236)
- [Página 0237 — Uma única interface pública permite impor a fronteira](#pagina-0237)
- [Página 0238 — Módulos e árvores de fontes oferecem outros controles](#pagina-0238)
- [Página 0239 — A infraestrutura pode contornar o domínio](#pagina-0239)

<a id="pagina-0210"></a>

## Página 0210 — A lentidão dos discos explica sistemas de acesso a dados

Tabelas e linhas não devem aparecer nos casos de uso nem circular como objetos por todo o sistema, pois isso acopla regras e interface à estrutura relacional. O autor relaciona a predominância dos bancos à história dos discos magnéticos: mover cabeças, esperar setores e carregar blocos custa muito mais que acessar memória. Índices, caches e consultas otimizadas mitigam essa diferença. Dessa necessidade surgiram sistemas de arquivos, adequados à recuperação de documentos por nome, e bancos, orientados à busca pelo conteúdo. A página inicia essa comparação e continua a discussão na próxima.

---

<a id="pagina-0211"></a>

## Página 0211 — Persistência e representação em memória têm papéis diferentes

Bancos associam registros por conteúdo; sistemas de arquivos organizam documentos. Ambos tornam o acesso ao disco mais eficiente e levam dados à memória para processamento. O autor imagina a substituição dos discos por memória e pergunta como os dados seriam organizados: listas, árvores, tabelas hash, pilhas e filas já são representações comuns nas aplicações. Essa reflexão sustenta a ideia de persistência como mecanismo separado, cujo formato não deve dominar a arquitetura. A página reconhece desempenho como preocupação arquitetural, mas defende que aspectos de acesso ao armazenamento podem ser encapsulados longe das regras de negócio. A previsão tecnológica pertence ao contexto do livro.

---

<a id="pagina-0212"></a>

## Página 0212 — Uma exigência comercial pode existir sem necessidade técnica

O autor relata um sistema de monitoramento de linhas T1 que usava arquivos de acesso aleatório, árvores e listas encadeadas adequados aos dados. Um gerente de marketing exigiu um banco relacional, apoiado depois por um engenheiro de hardware. O autor resistiu por não enxergar benefício técnico e pelo custo adicional de reorganizar os dados em tabelas. Mais tarde reconheceu que a exigência era real: clientes esperavam um banco relacional como item de compra, mesmo sem uma utilização prática definida. O episódio distingue proteger o núcleo arquitetural de ignorar requisitos comerciais existentes.

---

<a id="pagina-0213"></a>

## Página 0213 — Atender ao mercado sem entregar o núcleo ao banco

O relato atribui a expectativa dos clientes às campanhas dos fornecedores, que associavam bancos à proteção dos ativos de dados. A solução que o autor considera adequada retrospectivamente seria acrescentar o banco relacional por um canal estreito e seguro, mantendo a organização já apropriada ao núcleo. Na ocasião, porém, ele saiu da empresa. A conclusão reafirma a distinção: o modelo e a organização dos dados são significativos para a arquitetura; as tecnologias responsáveis por persistir e recuperar esses dados são mecanismos. O valor dos dados não exige tornar o banco o centro do sistema.

---

<a id="pagina-0216"></a>

## Página 0216 — Casos de uso criam uma fronteira independente da interface

A web é apresentada como dispositivo de entrada e saída, devendo ficar separada da lógica central. O autor reconhece que abstrair todas as interações específicas de interfaces ricas seria difícil: navegador e aplicação conversam de formas diferentes das interfaces de desktop. A separação viável ocorre nos casos de uso. Quando os dados de entrada estão completos, uma operação de negócio pode executá-los e devolver resultados em estruturas simples, retomando depois a interação visual. Essa fronteira preserva a independência do núcleo sem exigir uniformidade de toda a interface. A conclusão admite que acertá-la costuma exigir várias iterações.

---

<a id="pagina-0217"></a>

## Página 0217 — Frameworks resolvem problemas que podem coincidir com os seus

O capítulo 32 reconhece a utilidade de frameworks gratuitos, poderosos e populares, mas distingue essas ferramentas de arquitetura. Seus autores geralmente desejam ajudar e contribuir com a comunidade, porém não conhecem os problemas particulares de cada usuário. Eles partem das próprias necessidades e das pessoas próximas. Frameworks são úteis na medida em que essas necessidades coincidem com as da aplicação que os adota. Essa distinção prepara uma avaliação crítica: a disponibilidade e a qualidade da ferramenta não significam que suas escolhas devam definir todo o desenho do sistema.

---

<a id="pagina-0218"></a>

## Página 0218 — O compromisso com um framework é assimétrico

Documentação e exemplos costumam incentivar herdar classes do framework e importar seus recursos para objetos de negócio. Para o autor da ferramenta isso é controlável; para a aplicação, cria um compromisso de longo prazo sem garantia recíproca. O texto enumera riscos: violar a regra de dependência ao inserir tecnologia nas entidades; ultrapassar as capacidades da ferramenta; sofrer com evolução, remoção ou mudanças de recursos; e ter dificuldade para adotar alternativa melhor. A metáfora de um casamento assimétrico enfatiza que os custos de acoplamento recaem sobre quem constrói a aplicação. A solução é introduzida na página seguinte.

---

<a id="pagina-0219"></a>

## Página 0219 — Manter frameworks fora do núcleo é uma escolha consciente

A solução proposta é usar frameworks em componentes externos, atrás de fronteiras. Quando exigirem herança, proxies podem cumprir essa exigência e conectar-se às regras como plugins. No exemplo de Spring, a injeção pode ocorrer em Main, sem espalhar anotações pelos objetos de negócio. O autor admite compromissos difíceis de evitar, como STL em C++ e a biblioteca padrão em Java, mas pede que sejam decisões conscientes, considerando o vínculo duradouro. A conclusão recomenda manter a possibilidade de afastamento da ferramenta pelo maior tempo viável, em vez de incorporar imediatamente suas dependências ao centro da aplicação.

---

<a id="pagina-0225"></a>

## Página 0225 — Organização do código precisa sustentar o desenho

O capítulo 34, de Simon Brown, alerta que princípios e diagramas não bastam se a implementação não preservar suas fronteiras. O exemplo é uma livraria online com um caso de uso para consultar o estado dos pedidos, descrito em Java mas aplicável a outras linguagens. A primeira abordagem analisada organiza pacotes por camadas técnicas: código web, lógica de negócio e persistência. Essa divisão horizontal agrupa elementos pelo tipo de trabalho que realizam. A página prepara a comparação de diferentes formas de organizar o código e suas consequências para a arquitetura.

---

<a id="pagina-0227"></a>

## Página 0227 — Pacotes por funcionalidade tornam o domínio visível

Camadas técnicas ajudam a começar rapidamente, mas três grandes grupos tornam-se insuficientes conforme crescem tamanho e complexidade. Também pouco revelam sobre o negócio, pois sistemas diferentes acabam organizados em web, serviços e repositórios. A alternativa por funcionalidade reúne tipos relacionados a um conceito, como pedidos, em um único pacote. Isso evidencia o domínio e aproxima o código necessário para alterar um caso de uso. Embora reconheça esses benefícios, Simon Brown considera ambas as opções limitadas e prepara formas mais fortes de modularização, em vez de tratar a simples mudança de pastas como solução completa.

---

<a id="pagina-0229"></a>

## Página 0229 — Infraestrutura depende do domínio e usa sua linguagem

A figura 34.3 coloca domínio no interior e infraestrutura ao redor. A região externa contém interface, banco e integrações; a regra estabelece que ela dependa do núcleo, sem dependência inversa. No exemplo dos pedidos, o pacote domain representa o interior e recebe as dependências dos demais pacotes. O antigo OrdersRepository é renomeado para Orders para usar a linguagem do domínio, conforme a orientação de projeto dirigido pelo domínio. A escolha ressalta que os conceitos centrais devem ser expressos como as pessoas do negócio os entendem, sem acrescentar necessariamente nomes de mecanismos técnicos.

---

<a id="pagina-0230"></a>

## Página 0230 — Portas e adaptadores no exemplo dos pedidos

A figura 34.4 mostra OrdersController fora do domínio, usando OrdersService. Dentro do domínio ficam o serviço, sua implementação e a interface Orders; JdbcOrdersRepository permanece externo e implementa o contrato interno. O autor esclarece que o desenho é simplificado e omite interactors e objetos de transferência pelas fronteiras. Depois introduz sua proposta de pacotes por componente, derivada da experiência com diferentes tipos de sistemas empresariais em Java. Embora concorde com os princípios discutidos no livro, apresenta uma alternativa de organização do código e prepara a crítica aos limites práticos das camadas tradicionais.

---

<a id="pagina-0231"></a>

## Página 0231 — Camadas públicas permitem contornar a lógica de negócio

Separar Java em pacotes web, serviço e dados exige interfaces públicas para comunicação entre camadas. Isso permite dependências indesejadas mesmo sem formar ciclos. O exemplo acompanha um novo desenvolvedor que injeta OrdersRepository diretamente em OrdersController para entregar rapidamente outra página de pedidos. O resultado continua com setas descendentes, mas ignora OrdersService. Essa arquitetura de camadas relaxadas pode ser intencional em alguns cenários, como CQRS, porém pode eliminar regras importantes, inclusive autorização de acesso a registros. O caso mostra a distância entre uma intenção arquitetural e o que o código efetivamente permite.

---

<a id="pagina-0232"></a>

## Página 0232 — Regras arquiteturais precisam de aplicação verificável

A figura 34.5 evidencia a dependência direta do controlador para o repositório, além do caminho pelo serviço. Para impedir esse desvio, a equipe pode formular uma regra que proíba controladores web de acessar repositórios. Confiar apenas em disciplina e revisão é frágil sob pressão de prazo e orçamento. Algumas equipes usam ferramentas de análise estática para verificar dependências entre pacotes e falhar a construção quando houver violações. O autor reconhece que regras por padrões de nomes podem funcionar, mas começa a discutir as limitações dessas abordagens e o tempo até receber retorno sobre o erro.

---

<a id="pagina-0233"></a>

## Página 0233 — Pacotes por componente buscam fronteiras impostas pelo compilador

Revisões e verificações posteriores podem falhar e oferecem retorno mais lento do que o desejado; Simon Brown prefere aproveitar o compilador para impor a arquitetura. Sua alternativa híbrida reúne as responsabilidades relacionadas a um componente funcional amplo em um pacote, mantendo a interface de usuário separada. Nesse sentido, lógica de negócio e persistência ficam dentro da mesma unidade, com suas separações internas preservadas. O autor ressalta que usa “componente” de modo diferente do apresentado antes por Robert Martin, para quem componentes são unidades de implantação, como arquivos JAR. Sua própria definição continua na página seguinte.

---

<a id="pagina-0234"></a>

## Página 0234 — Componente encapsula funcionalidade atrás de uma interface

A figura 34.6 deixa OrdersController fora de um pacote de pedidos que expõe OrdersComponent e contém implementação, contrato de repositório e acesso JDBC. No modelo C4 de Simon Brown, componente é um grupo de funcionalidades relacionadas atrás de uma interface, inserido em um ambiente de execução. Sistemas contêm contêineres, estes contêm componentes e estes são implementados por classes ou código; separar cada componente em um JAR é outra decisão. O benefício é oferecer um único ponto para operações de pedidos. Negócio e persistência continuam separados internamente, sem exigir que os consumidores conheçam essa organização.

---

<a id="pagina-0235"></a>

## Página 0235 — Organização de pacotes sem encapsulamento é insuficiente

Componentes bem definidos em um monólito podem preparar uma evolução para serviços, mudando o modo de desacoplamento. Porém, as quatro formas de organização analisadas perdem força quando todos os tipos são públicos. Nesse caso, pacotes funcionam apenas como pastas: qualquer código pode acessar detalhes e instanciar implementações, contrariando o desenho pretendido. O autor observa que esse uso indiscriminado é comum em exemplos e projetos reais. Sem restrições de acesso, abordagens conceitualmente diferentes tornam-se sintaticamente equivalentes. Os modificadores da linguagem, embora imperfeitos, são recursos importantes para tornar fronteiras efetivas.

---

<a id="pagina-0236"></a>

## Página 0236 — A visibilidade muda o efeito de cada organização

A figura 34.7 elimina pacotes e mostra que as quatro abordagens mantêm relações equivalentes quando todos os tipos são públicos. Ao aplicar restrições, surgem diferenças. Em pacotes por camada, interfaces de serviço e repositório precisam ser públicas, mas implementações podem ficar internas ao pacote. Em pacotes por funcionalidade, apenas o controlador pode ser público, o que também obriga outros consumidores de pedidos a passar por ele. Em portas e adaptadores, OrdersService e Orders permanecem públicos para uso externo, enquanto implementações podem ser ocultadas e fornecidas por injeção em execução.

---

<a id="pagina-0237"></a>

## Página 0237 — Uma única interface pública permite impor a fronteira

A figura 34.8 destaca os tipos que podem ter acesso restrito em cada abordagem. Nos pacotes por componente, apenas OrdersComponent precisa estar disponível ao controlador; implementação, contrato de repositório e acesso concreto podem permanecer internos. Isso reduz dependências possíveis e permite ao compilador impedir acesso direto ao repositório por código externo. O texto cita internal em .NET como recurso semelhante, exigindo uma assembly por componente. A recomendação se refere ao monólito com uma única árvore de fontes: usar os mecanismos da linguagem para proteger a arquitetura, em vez de depender apenas de disciplina e ferramentas posteriores.

---

<a id="pagina-0238"></a>

## Página 0238 — Módulos e árvores de fontes oferecem outros controles

Sistemas de módulos, como OSGi e o Java 9 citado no contexto do livro, permitem distinguir tipos públicos dos efetivamente publicados para consumidores externos. Outra opção separa árvores de código de domínio, web e persistência, fazendo as duas últimas dependerem da primeira na compilação. Ferramentas de construção podem impor esses vínculos. Repetir o padrão por componente amplia o isolamento, mas aumenta complexidade, manutenção e custos de desempenho do processo de construção. Uma simplificação comum reúne apenas duas árvores, domínio interno e infraestrutura externa, preservando a dependência de fora para dentro, mas com outras concessões.

---

<a id="pagina-0239"></a>

## Página 0239 — A infraestrutura pode contornar o domínio

A figura 34.9 representa domínio e infraestrutura separados, mas essa organização admite um risco: código web pode chamar diretamente um repositório dentro da mesma infraestrutura. O autor compara esse desvio ao anel viário de Paris, que permite circular sem entrar na cidade, e o chama de antipadrão Périphérique. Restrições de acesso inadequadas facilitam o problema. A conclusão pede traduzir intenções arquiteturais em estruturas de código e mecanismos reais de separação, equilibrando equipe, habilidade, complexidade, prazo e orçamento. Recomenda usar o compilador e observar também acoplamentos em modelos de dados.
