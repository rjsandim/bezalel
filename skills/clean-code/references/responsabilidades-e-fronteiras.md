# Responsabilidades e fronteiras

Use quando uma mudança se espalha entre componentes, a representação interna vaza ou dependências impedem teste e evolução.

## Responsabilidade, coesão e dados

Uma responsabilidade é um motivo para mudar, não uma contagem de métodos. Procure grupos que usam conjuntos distintos de estado ou respondem a mudanças independentes. Extraia uma unidade quando ela representar um conceito coeso; não divida uma classe estável apenas para atingir um tamanho ideal.

Mover comportamento para perto dos dados pode reduzir consultas aos detalhes de outro objeto. Porém, não faça uma entidade absorver regras de relatório ou apresentação apenas por essa proximidade. Considere quais mudanças cada componente deve acompanhar.

Se a extração de funções transformou variáveis locais em campos compartilhados, examine a perda de coesão e o ciclo de vida desse estado. Prefira dados explícitos ou um componente coeso a dependências temporais invisíveis.

| Mudança predominante | Organização a considerar |
|---|---|
| Novos tipos com operações conhecidas | Comportamento polimórfico que localize cada variante. |
| Novas operações sobre estruturas estáveis | Dados simples com operações externas. |
| Transporte entre fronteiras | Estruturas de transferência explícitas, sem hierarquia desnecessária. |
| Proteção de invariantes e representação | Operações que expressem a intenção sem expor cada campo. |

Encapsulamento não é criar getters e setters mecanicamente: é proteger invariantes e permitir que a representação mude sem afetar consumidores. Cadeias que percorrem estruturas internas podem pedir uma operação no colaborador apropriado. Avalie a dependência real, não o número de pontos na sintaxe; APIs fluentes e estruturas de transporte têm outros propósitos.

## Regras sustentadas pela representação

Quando vários consumidores repetem validações ou precisam lembrar combinações permitidas, considere um tipo de domínio, uma enumeração ou uma operação de construção que represente apenas estados válidos. Faça isso para uma invariante concreta. Um inteiro isolado não exige automaticamente uma classe própria.

Converta e valide dados externos na fronteira adequada. Só remova uma verificação interna quando o mecanismo escolhido realmente garantir a condição; uma anotação de tipo sem validação em execução pode não restringir dados recebidos de JSON ou do banco. Preserve códigos serializados, valores aceitos e respostas a entradas inválidas quando fizerem parte do contrato existente.

Verifique o alcance da garantia: um mês válido não assegura que a combinação de dia, mês e ano forme uma data válida. Preserve as invariantes que envolvem vários campos.

Por exemplo, um intervalo pode distinguir explicitamente extremidades abertas e fechadas em vez de depender de dois booleanos posicionais. Isso ajuda quando evita inversões e concentra a regra de inclusão. Não exige substituir uma API pública compatível nem criar polimorfismo para cada variante.

## Dependências e integrações

Separe a criação e conexão dos colaboradores de seu uso quando a mistura introduzir acoplamento ou impedir testes controláveis. Injete a dependência efetivamente utilizada, aproveitando mecanismos existentes. Não acrescente um contêiner ou uma interface para cada classe.

Separar construção de uso não exige antecipar toda criação para a inicialização. Se o fluxo decide quando criar algo ou precisa de dados disponíveis somente naquele momento, uma função de criação ou fábrica pode preservar essa decisão. Verifique o momento da criação, o número de instâncias e seu ciclo de vida; instanciar tudo antecipadamente pode mudar custos, efeitos e falhas observáveis.

Mantenha conceitos gerais independentes de detalhes concretos. Não imponha a uma abstração capacidades sem sentido para algumas variantes, preenchendo-as com respostas fictícias. Centralize a escolha dos valores de configuração e passe os dados necessários aos níveis inferiores, evitando defaults divergentes e estado global criado para economizar parâmetros.

Procure dependências lógicas escondidas: dois módulos podem estar acoplados mesmo sem compartilhar código, por presumirem o mesmo limite, unidade, origem de índice ou formato. Faça o consumidor obter essa informação de quem a define ou receba-a explicitamente. Se um exportador admite uma capacidade variável de registros por lote, o chamador deve conhecer essa capacidade pelo contrato; copiar um número para uma constante local apenas dá nome à suposição.

Coloque regras e constantes junto do conceito responsável por elas. Um módulo genérico não deve depender de uma implementação especializada só porque ela guarda uma constante conveniente. Diferencie essa dependência indevida de valores que coincidem por acaso e pertencem a regras independentes.

Uma camada de adaptação pode limitar uma API externa ao que a aplicação usa, traduzir falhas e fornecer um ponto substituível para testes. Faça isso quando houver uma dependência relevante a controlar, sem encapsular indiscriminadamente toda biblioteca ou coleção.

Aumente a estrutura conforme necessidades concretas surgirem. Um padrão deve reduzir um custo identificável; prestígio, uniformidade abstrata ou possibilidades futuras indefinidas não bastam para adotá-lo.

## Da suspeita à correção

| Evidência no código | Transformação possível | Quando evitar |
|---|---|---|
| Métodos distintos usam grupos de campos sem relação | Extrair um componente coeso com ciclo de vida claro. | Quando os dados precisam preservar uma mesma invariante e a divisão a enfraquece. |
| Uma mudança de fornecedor exige editar muitos consumidores | Concentrar a tradução numa fronteira definida pela necessidade da aplicação. | Quando uma camada adicional só renomeia uma API pequena e estável sem reduzir acoplamento. |
| Regras por tipo são repetidas em operações que crescem juntas | Localizar as variantes em estratégias ou implementações de um contrato. | Quando um despacho único e fechado já comunica bem a decisão. |
| Um objeto precisa conhecer diretórios, formatos e detalhes de outro | Oferecer a operação de que ele realmente precisa. | Quando o acesso é a uma estrutura de transporte deliberadamente simples. |
| Código de domínio resolve dependências e monta infraestrutura | Separar composição de uso, usando o mecanismo existente. | Quando isso exigiria implantar um framework sem necessidade da tarefa. |

## Exemplo: emissão de um documento

Considere uma operação que calcula valores, grava o resultado e renderiza um comprovante. Essas atividades podem mudar por razões diferentes: regra comercial, esquema de persistência e apresentação. Um primeiro passo útil pode ser isolar o cálculo puro e manter a coordenação existente, verificando os mesmos valores e a mesma ordem dos efeitos.

Esse diagnóstico não exige criar imediatamente várias camadas, repositórios e interfaces. Escolha a separação que resolve a dificuldade observada. Se o problema é testar o cálculo sem acessar o banco, uma função ou componente focado pode bastar. Se a troca de fornecedor se espalha pelo sistema, uma fronteira de integração ganha justificativa concreta.

Mover toda a renderização para a entidade só porque ela possui os dados também pode piorar o projeto: a entidade passaria a acompanhar mudanças de apresentação. A proximidade dos dados deve ser equilibrada com a razão de mudança.

## Contratos ao mover responsabilidades

Verifique propriedade e tempo de vida do estado, visibilidade de operações e direção das dependências. Uma classe base não deve depender de uma variante concreta para definir conceitos gerais. Uma nova abstração não deve exigir que algumas implementações retornem respostas fictícias para operações sem sentido.

Ao reduzir uma interface, preserve os consumidores exigidos pela tarefa. Diferencie o que está disponível publicamente do que foi observado apenas no repositório local; busca sem resultados não comprova ausência de usuários externos.
