# Princípios e fronteiras

Use para decidir onde uma regra vive, quem possui um contrato e como orientar dependências. As páginas citadas são posições físicas dos resumos; veja [Fontes](fontes.md).

## SOLID como critério de mudança

| Princípio | Evidência | Correção proporcional |
|---|---|---|
| SRP: responsabilidade perante um ator | Financeiro, operação ou persistência exigem mudanças independentes no mesmo módulo | Separe políticas por motivo de mudança; coordene por composição ou fachada quando útil |
| OCP: proteger contra mudanças relevantes | Uma variante conhecida obriga modificar repetidamente políticas estáveis | Isole esse eixo por função, estratégia ou contrato, sem prever toda extensão possível |
| LSP: substituição preserva o contrato | Adaptadores mudam significado, pré-condições, resultados ou falhas e exigem exceções no consumidor | Alinhe os contratos ou traduza na borda; assinaturas iguais não bastam |
| ISP: consumidores dependem do necessário | Uma operação exige cliente gigante e funcionalidades alheias | Exponha o contrato mínimo para a necessidade; avalie dependências transitivas |
| DIP: políticas protegidas de detalhes voláteis | Regra importa ou instancia ORM, SDK, controlador ou implementação mutável | Contrato do lado da política; implementação externa conectada na composição |

SRP não significa um método por classe. Pagamento e relatório de horas podem ter cálculos parecidos e motivos de mudança diferentes; compartilhá-los pode introduzir regressão. OCP escolhe mudanças das quais vale proteger o sistema, sem proibir toda edição futura. LSP também se aplica a serviços e protocolos. Fontes: 64–86.

Tipos primitivos, biblioteca padrão e implementações estáveis não exigem wrappers por princípio. Funções recebidas como parâmetro, composição e contratos estruturais podem inverter dependências sem hierarquia de interfaces. Uma interface que devolve modelos do ORM ou importa o SDK continua acoplada ao detalhe. Fontes: 83–85, 110.

## Atribuir responsabilidades

- **Domínio:** regras, invariantes e dados essenciais ao negócio, independentes da entrega. Pode usar objetos ou funções com dados; não exige orientação a objetos.
- **Aplicação:** coordena objetivo do usuário, sequência das operações e regras do caso de uso. Depende do domínio; domínio não conhece esse fluxo.
- **Adaptadores:** convertem HTTP, SQL, mensagens externas e apresentação em contratos convenientes ao núcleo e vice-versa. Validação de formato pode ficar aqui; invariantes de negócio precisam existir no núcleo.
- **Composição:** escolhe implementações, configuração e recursos concretos. Entrega dependências às políticas; não força o domínio a consultar um container global de serviços.

Níveis dependem da política e da distância dos mecanismos de entrada e saída. O nome `domain` não torna um módulo independente: examine seu conteúdo. Fontes: 149–166, 181–184.

Examine duas dimensões: os níveis técnicos de política e os motivos de mudança por ator ou caso de uso. Uma pasta de serviços que reúne todas as operações pode manter funcionalidades independentes acopladas. Identifique o fluxo vertical afetado e suas responsabilidades, sem impor um pacote ou classe para cada operação. Ator é uma fonte de necessidades, não automaticamente um papel de acesso ou um serviço separado. Fontes: 128–129, 220–224.

Também pode haver eixos independentes dentro de uma camada: idioma e canal de entrega, por exemplo, não precisam variar juntos. O próprio domínio pode conter políticas de níveis distintos. Separe quando isso protege uma mudança concreta; não reproduza toda a decomposição do exemplo do jogo num sistema pequeno. Fontes: 174–180.

## Cruzar fronteiras

Exemplo de dependências de código:

```text
Controlador HTTP -> Caso de uso -> Regra de domínio
                       |
                       v
               Contrato de armazenamento
                       ^
                       |
               Adaptador SQL

Bootstrap -> Caso de uso + Adaptador SQL
```

O caso de uso chama o adaptador em execução, mas conhece apenas o contrato necessário. O adaptador conhece esse contrato e SQL. A composição pode conhecer ambos. Defina contrato e dados no lado da política que os utiliza, sem importar a implementação para especificá-los.

Expresse o contrato na linguagem da aplicação. Uma porta que recebe URLs, nomes de tabelas, registradores ou comandos do fornecedor pode continuar expondo a tecnologia, mesmo com imports apontando para dentro. No exemplo embarcado, indicar bateria fraca exprime melhor a intenção do produto que escrever num bit GPIO. Traduza operações, resultados e diferenças semânticas no adaptador quando esse for o limite pretendido; não crie uma API genérica para toda a capacidade do fornecedor. Fontes: 74, 201–202, 205–207.

Use dados simples adequados ao caso de uso. Evite transportar requests/responses HTTP, modelos do ORM, proxies de carregamento ou tipos do SDK para o núcleo. Não reutilize automaticamente entidade como entrada ou saída pública: exposição e domínio têm motivos de mudança diferentes. Preserve formatos públicos por tradução nos adaptadores. Fontes: 137–146, 155–166.

O desenho admite mais ou menos fronteiras que o diagrama do livro. Um apresentador dedicado é útil para decisões relevantes de apresentação; um retorno simples pode bastar em outro contexto. Um módulo que somente repassa parâmetros, sem traduzir contrato ou proteger política, precisa justificar seu custo.

Isolamento torna substituições viáveis, não gratuitas. Trocar banco, interface ou modelo de execução ainda pode exigir migração de dados, adaptação de semântica e trabalho operacional. Não prometa uma troca por configuração apenas porque existe uma interface. Fontes: 132, 141.

## Frameworks e objetos humildes

Use o framework onde ele ajuda. Concentre nas bordas a herança, anotações e chamadas que amarram regras à ferramenta quando houver valor nessa separação. Não substitua todo o framework para obter isolamento local. Dependências aceitas conscientemente são compromissos, não independência já alcançada. Fontes: 158–166, 217–219.

Quando a integração for difícil de testar, reduza sua parte inevitável e extraia a lógica verificável: Presenter prepara o modelo de exibição; View apresenta. Gateway traduz persistência; caso de uso decide a operação. A parte externa continua precisando de verificação de integração. Fontes: 167–170.
