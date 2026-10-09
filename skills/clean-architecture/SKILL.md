---
name: clean-architecture
description: Revise e corrija a arquitetura de software usando Clean Architecture, SOLID e princípios de componentes. Use em revisões arquiteturais e em implementações ou refatorações que afetem responsabilidades, fronteiras ou dependências. Não se aplica a ajustes apenas cosméticos.
---

# Clean Architecture

## Objetivo e escopo

Corrija problemas arquiteturais concretos a partir dos princípios sintetizados de **Clean Architecture**, de Robert C. Martin. Proteja regras de negócio, contenha a propagação de mudanças e facilite desenvolvimento, testes, implantação e manutenção. Esta skill é autocontida: as referências práticas e 132 resumos de apoio estão incluídos na própria pasta, com links relativos. Use esse material local sem precisar de arquivos do projeto que originou a skill.


- **Implementação ou correção:** aplique os princípios ao fluxo alterado e aos consumidores afetados. Execute as correções autorizadas; não substitua um pedido de implementação por recomendações.
- **Revisão sem edição:** apresente violações demonstráveis, consequências e correções sugeridas. A revisão não autoriza alterar o projeto.
- **Refatoração:** preserve comportamento e contratos observáveis, salvo mudanças solicitadas. Considere retornos, erros, autorização, transações, formatos persistidos, eventos e ordem dos efeitos externos.

Parta da arquitetura, linguagem e convenções existentes. Reduza o custo de mudança dentro do escopo, sem converter todo projeto para um modelo predeterminado. Não imponha quatro camadas, nomes de pastas, classes de caso de uso, uma interface por classe ou microsserviços. Funções, módulos e monólitos também podem preservar fronteiras.

## Entradas e pré-requisitos

Use o pedido, os arquivos/diff relevantes, contratos, restrições e instruções do
projeto alvo. Identifique se o escopo é análise, implementação ou refatoração.
Não há runtime próprio nem dependências de execução desta skill; a validação
depende das ferramentas do projeto analisado.

## Procedimento

Rastreie um fluxo real: entrada, aplicação, regra de negócio, persistência ou integração e saída. Examine contratos, composição e testes. Diferencie **quem chama quem em execução** de **quem depende de quem no código**. Inclua tipos, anotações, modelos de dados, configuração, carregamento dinâmico e acesso compartilhado quando relevantes; olhar somente imports ou pastas pode esconder acoplamento.

Para cada problema, relacione evidência no código, princípio e consequência concreta. Exemplos: mudar o ORM exige alterar um cálculo; atores compartilham uma regra que precisa divergir; um controlador contorna autorização; um ciclo obriga testar ou implantar módulos em conjunto. Um nome, um diagrama ou uma métrica isolada não demonstra uma violação.

Priorize o risco ao comportamento e às regras, depois o acoplamento que bloqueia a mudança atual. Defina a menor fronteira que resolve o problema e confira seu custo. Preserve separações que já funcionam. Quando a investigação for parcial, declare os limites em vez de certificar a arquitetura inteira.

Escolha um cenário representativo de mudança e o ganho esperado: menos módulos afetados, regras testáveis isoladamente, menos coordenação de releases ou menos passos de implantação. Considere requisitos reais de latência, vazão, recursos e operação antes de propor outra topologia. Avalie o resultado contra esse cenário; reduzir dependências no diagrama não basta se o custo total aumentar.

### Referências sob demanda

Leia somente o material pertinente à decisão atual:

| Questão | Referência |
|---|---|
| SOLID, propriedade de contratos, domínio, aplicação, adaptadores e composição | [Princípios e fronteiras](references/principios-e-fronteiras.md) |
| Coesão, ciclos, estabilidade, requisitos operacionais, reutilização e serviços | [Componentes e evolução](references/componentes-e-evolucao.md) |
| Correção incremental, persistência, testes e proteção de fronteiras | [Correção e verificação](references/correcao-e-verificacao.md) |
| Exemplos do livro, ressalvas e contexto adicional dos princípios | [Fontes e 132 resumos incluídos](references/fontes.md) |

### Critérios de revisão

- **Dependências para dentro:** regras centrais não conhecem detalhes voláteis de web, banco, framework, UI ou provedores. O contrato de uma operação externa pertence ao lado que expressa a necessidade; o adaptador externo o implementa. O fluxo de controle pode seguir o sentido contrário.
- **Responsabilidades pelo propósito:** domínio protege regras gerais; casos de uso coordenam objetivos específicos; adaptadores traduzem formatos externos. A montagem concreta fica em Main, bootstrap ou no mecanismo de composição equivalente do framework.
- **Motivos de mudança:** separe atores e políticas que evoluem independentemente. Não unifique regras apenas porque os algoritmos parecem iguais.
- **Duas dimensões de separação:** examine tanto níveis de política quanto atores e casos de uso. Camadas técnicas sozinhas podem continuar obrigando funcionalidades independentes a mudar juntas.
- **Contratos substituíveis e pequenos:** preserve semântica, falhas e invariantes ao trocar implementações. Evite impor operações e dependências que um consumidor não utiliza. Abstrações devem proteger uma variação ou fronteira identificável.
- **Componentes coesos e sem ciclos:** agrupe o que muda junto e observe quem precisará recompilar, testar, versionar ou implantar. Processos separados não comprovam independência.
- **Fronteiras efetivas:** diretórios não impedem atalhos. Quando a fronteira for importante, use visibilidade, exportações, módulos ou regras verificáveis de dependência compatíveis com a linguagem e o projeto.

## Saídas

Entregue achados com localização, consequência e proposta concreta; quando
houver autorização para editar, entregue mudanças e evidências de validação.
Diferencie o que foi verificado de hipóteses e limitações.

## Validação

Faça transformações pequenas, justificando a direção das dependências e a responsabilidade movida. Atualize composição e consumidores reais: deixar a implementação antiga como dependência oculta ou criar outro caminho de negócio não resolve a fronteira.

Verifique comportamento e propriedade arquitetural alterada. Use testes existentes e verificações proporcionais ao risco. Pode ser apropriado testar a regra sem infraestrutura real, validar o contrato do adaptador e impedir a dependência indevida pelo compilador ou por análise arquitetural. Um substituto em memória não prova o comportamento do banco ou serviço real.

Não enfraqueça testes para acomodar a refatoração nem espelhe métodos privados em novas verificações. Corrigir estrutura não autoriza trocar banco, framework, protocolo, esquema público ou modelo de implantação. Se uma mudança mais ampla for indispensável, concretize o diagnóstico e delimite a decisão restante.

Na entrega, explique a fronteira ou responsabilidade corrigida, o efeito prático, as verificações e os limites. Diferencie violação confirmada, escolha aceitável e questão não verificada. Se nenhuma mudança útil for necessária, diga isso.

## Limites operacionais

Análise não autoriza alteração. Mantenha o escopo solicitado, preserve contratos
e use testes proporcionais ao risco. Não amplie a tarefa para migrações,
publicação, acesso a serviços ou mudanças destrutivas sem autorização aplicável.
