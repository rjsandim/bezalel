# Componentes e evolução

Use para agrupamento de módulos, ciclos, estabilidade e decisões de implantação. Fontes: [mapa dos resumos](fontes.md).

## Escolher o que fica junto

Equilibre três forças, sem tentar maximizá-las simultaneamente:

- **REP, equivalência entre reutilização e release:** o que é reutilizado deve formar uma entrega coerente, com versão e mudanças compreensíveis. Não exige publicar cada módulo interno como biblioteca.
- **CCP, fechamento comum:** agrupe o que muda pelas mesmas razões e no mesmo momento, reduzindo coordenação e validação.
- **CRP, reutilização comum:** evite obrigar consumidores a depender de funcionalidades que não usam. Partes usadas juntas podem permanecer juntas; dependências excedentes espalham custos de release.

No início, manutenção pode pesar mais que reutilização externa. Dividir cada classe num pacote pode piorar o trabalho. Investigue consumidores e mudanças reais antes de recompor módulos. Fontes: 93–97, 104.

Antes de extrair uma plataforma ou framework compartilhado, exercite a abstração com consumidores reais que tenham diferenças relevantes. Um caso pode justificar uma separação local, mas não comprova generalidade. O relato das vinhetas mostra um framework que precisou ser refeito quando outras aplicações o utilizaram; a extração passou a funcionar ao evoluir junto delas. Não transforme as quatro aplicações do relato numa cota universal. Se uma exceção útil a um consumidor complica todos os demais, reavalie o limite do compartilhamento. Fontes: 272–273.

## Eliminar ciclos demonstrados

Registre o caminho concreto, como `Pedidos -> Cobrança -> Clientes -> Pedidos`, e suas arestas. O ciclo pode transformar componentes em uma única unidade de teste e release, mesmo em pastas diferentes.

Escolha conforme a responsabilidade:

1. Inverta a dependência da política para o detalhe: contrato no consumidor, implementação no provedor.
2. Extraia uma abstração coesa necessária a ambos, se houver conceito próprio.
3. Reúna partes de uma mesma responsabilidade quando a separação artificial tiver criado o ciclo.

As duas primeiras técnicas vêm das páginas 102–103; a terceira aplica o critério de coesão. Evite um `common` que receba qualquer dependência. Mover imports para dentro de funções pode adiar um erro sem remover o ciclo arquitetural. Fontes: 98–104.

## Estabilidade e abstração

Estabilidade significa dificuldade de mudança por obrigações perante consumidores; não é ausência de bugs nem frequência de commits. Oriente dependências para maior estabilidade (SDP) e preserve a extensão das políticas estáveis por abstrações adequadas (SAP). Detalhes concretos precisam continuar fáceis de mudar. Fontes: 105–110.

Métricas opcionais para investigar um grafo compreendido:

- `I = fan-out / (fan-in + fan-out)`: instabilidade estrutural. Sem relações, registre como não calculável por essa fórmula.
- `A = tipos abstratos / total de tipos`: abstração. Declare o critério de contagem e limitações da linguagem; com denominador zero, não calcule.
- `D = |A + I - 1|`: distância da sequência principal. Sinaliza investigação, não aprovação.

Não adote limites universais ou crie interfaces sem consumidores para melhorar números. Bibliotecas concretas estáveis podem ser aceitáveis. A página 112 contém uma inconsistência de notação; interprete o gráfico pelas definições de 107 e 111, sem reproduzir a menção inconsistente. Fontes: 106–115.

## Escolher a força da fronteira

Fronteiras podem existir num processo, entre bibliotecas, processos ou serviços. Chamadas remotas acrescentam latência, falhas e operação. Equilibre desenvolvimento, implantação, operação e manutenção, sem otimizar apenas a divisão da equipe. Fontes: 117–132, 144–148.

Declare qual independência é necessária e qual foi demonstrada:

| Dimensão | Evidência relevante |
|---|---|
| Código e desenvolvimento | Mudança fica concentrada; dependências de compilação, contratos e trabalho de equipes permanecem controlados |
| Implantação | Uma versão pode ser entregue sem exigir atualização simultânea de consumidores; contratos, dados e composição continuam compatíveis |
| Execução e operação | A separação atende ao requisito de vazão, latência, recursos ou distribuição e suporta o custo da comunicação |

Uma dimensão não prova as outras. Threads organizam execução, mas não estabelecem por si uma fronteira arquitetural ou uma unidade de implantação. Um componente lógico pode continuar sendo entregue junto ao restante. Fontes: 126–132, 145–148, 223–224.

Determine quais restrições operacionais já existem e como a mudança as afeta. Quando esse risco for relevante, compare medições disponíveis ou um experimento representativo antes e depois. Não invente metas, extrapole testes locais para carga de produção ou ignore desempenho em nome de pureza arquitetural. O mecanismo pode ficar isolado, mas o requisito precisa ser atendido. Fontes: 15–16, 126–127, 211.

Fronteiras completas custam contratos, modelos e manutenção. Separação parcial pode proteger a mudança atual e reservar uma opção futura. Fachada isolada não inverte dependências nem impede atalhos; registre a proteção efetiva. Antecipe eixos de mudança plausíveis e reavalie quando surgir atrito. Fontes: 171–180.

Serviços separados continuam acoplados por esquemas, mensagens, regras e releases coordenados. Examine essas relações antes de afirmar independência. Um monólito modular pode satisfazer a necessidade; fronteiras também podem existir dentro de um serviço ou atravessar vários. Decida pelos requisitos reais. Fontes: 185–191, 223–224.

Use o custo da mudança como critério de resultado: esforço para localizar e alterar uma regra, consumidores atingidos, preparação dos testes e coordenação da entrega. Mais camadas podem aumentar navegação e comunicação sem proteger outra política. O apêndice relata tanto estruturas diferentes igualmente eficazes quanto excesso de arquitetura que prejudicou o ROSE. Compare alternativas pelo problema atendido e pelas concessões reais, sem eleger um estilo universal. Fontes: 15–16, 26, 262, 271.

## Tornar o desenho executável

Use visibilidade de tipos, exportações, módulos e dependências do build. Quando necessário, análise arquitetural pode verificar a direção e bloquear atalhos. Trocar nomes de pastas não demonstra correção.

Investigue `controlador -> repositório`: esse desvio pode ignorar autorização ou regras mesmo com domínio e infraestrutura separados. Consulta direta pode ser deliberada, como num caminho de leitura separado, desde que preserve as políticas exigidas. Não condene pelo formato do diagrama apenas. Fontes: 225–239.

“Componente” tem dois sentidos: unidade de implantação nos capítulos de Martin e funcionalidades encapsuladas no capítulo de Simon Brown. Declare o nível discutido antes de sugerir pacotes, bibliotecas ou serviços. Fontes: 88, 233–234.
