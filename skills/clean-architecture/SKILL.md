---
name: clean-architecture
description: Revisa e corrige a arquitetura com Clean Architecture, SOLID e princípios de componentes, olhando responsabilidades, fronteiras entre módulos/camadas e direção das dependências. Use quando o pedido for "isso está no lugar certo?", "o domínio está acoplado ao framework/ORM", "revisa a arquitetura desse módulo", "como separar essa regra", "tem dependência circular" ou quando uma implementação ou refatoração mexer em fronteiras. Para legibilidade, nomes e funções dentro do trecho, use clean-code; para estrutura de banco ou migrations, prepare a proposta com proposta-banco.
---

# Clean Architecture

## Objetivo e escopo

Corrigir problemas arquiteturais concretos com os princípios de **Clean
Architecture**, de Robert C. Martin: proteger regras de negócio, conter a
propagação de mudanças e facilitar testes, implantação e manutenção. As
referências práticas e 132 resumos de apoio estão nesta pasta.

Escolha o modo de acordo com o pedido:

- **Implementação ou correção:** aplique os princípios ao fluxo alterado e aos
  consumidores afetados e entregue a mudança, não apenas recomendações.
- **Refatoração:** preserve comportamento e contratos observáveis, salvo mudança
  solicitada.
- **Revisão sem edição:** aponte violações demonstráveis, consequências e
  correções sugeridas, sem alterar o projeto.

Parta da arquitetura, linguagem e convenções existentes. Quatro camadas, nomes
de pastas, classe por caso de uso, interface por classe ou microsserviços são
opções, não metas: funções, módulos e monólitos também preservam fronteiras.

## Entradas e pré-requisitos

- Pedido e modo (revisão, implementação ou refatoração).
- Um fluxo real afetado: ponto de entrada, regra, persistência ou integração e saída.
- Contratos, composição (bootstrap, container, Main), testes e regras de
  arquitetura documentadas pelo projeto.
- Requisitos operacionais conhecidos (latência, vazão, implantação), quando a
  proposta envolver topologia.

## Procedimento

1. **Rastreie um fluxo real** do ponto de entrada à saída. Diferencie quem chama
   quem em execução de quem depende de quem no código. Inclua tipos, anotações,
   modelos de dados, configuração, carregamento dinâmico e acesso compartilhado;
   imports e pastas sozinhos escondem acoplamento.
2. **Registre cada problema com evidência, princípio e consequência.** Exemplos:
   trocar o ORM obriga a mudar um cálculo; dois atores compartilham uma regra que
   precisa divergir; um controlador contorna a autorização; um ciclo obriga a
   testar ou implantar módulos juntos. Nome, diagrama ou métrica isolados são
   sinais para investigar, não prova.
3. **Priorize** o risco ao comportamento e às regras, depois o acoplamento que
   bloqueia a mudança atual. Preserve separações que já funcionam.
4. **Defina a menor fronteira** que resolve o problema e um cenário de mudança
   para medi-la: menos módulos afetados, regra testável isoladamente, menos
   coordenação de releases ou menos passos de implantação.
5. **Consulte a referência pertinente** (tabela abaixo) para a decisão atual.
6. **Aplique em passos pequenos**, justificando a direção de cada dependência e a
   responsabilidade movida. Atualize composição e consumidores reais; deixar a
   implementação antiga como dependência oculta não resolve a fronteira.
7. **Delimite o restante.** Se a correção exigir trocar banco, framework,
   protocolo, esquema público ou modelo de implantação, descreva o diagnóstico e
   a decisão pendente em vez de executá-la.

| Questão | Referência |
|---|---|
| SOLID, propriedade de contratos, domínio, aplicação, adaptadores e composição | [Princípios e fronteiras](references/principios-e-fronteiras.md) |
| Coesão, ciclos, estabilidade, requisitos operacionais, reutilização e serviços | [Componentes e evolução](references/componentes-e-evolucao.md) |
| Correção incremental, persistência, testes e proteção de fronteiras | [Correção e verificação](references/correcao-e-verificacao.md) |
| Exemplos do livro, ressalvas e contexto adicional dos princípios | [Fontes e 132 resumos incluídos](references/fontes.md) |

Critérios de revisão:

- **Dependências para dentro:** regras centrais desconhecem web, banco,
  framework, UI e provedores. O contrato de uma operação externa pertence a quem
  expressa a necessidade; o adaptador o implementa.
- **Responsabilidades pelo propósito:** domínio protege regras gerais, casos de
  uso coordenam objetivos, adaptadores traduzem formatos. A montagem concreta
  fica em Main, bootstrap ou mecanismo equivalente.
- **Motivos de mudança:** separe atores e políticas que evoluem de forma
  independente, mesmo quando os algoritmos parecem iguais.
- **Duas dimensões:** examine níveis de política e também atores/casos de uso;
  camadas técnicas sozinhas podem manter funcionalidades acopladas.
- **Contratos pequenos e substituíveis:** preserve semântica, falhas e invariantes
  ao trocar implementações. Abstrações protegem uma variação identificável.
- **Componentes coesos e acíclicos:** agrupe o que muda junto e observe quem
  precisará recompilar, testar ou implantar. Processos separados não comprovam
  independência.
- **Fronteiras efetivas:** quando a fronteira importa, use visibilidade,
  exportações, módulos ou regras verificáveis de dependência.

## Saídas

- **Com edição:** fronteira ou responsabilidade corrigida, efeito prático no
  cenário de mudança, arquivos alterados e verificações executadas.
- **Sem edição:** achados classificados como violação confirmada, escolha
  aceitável ou questão não verificada, com evidência e correção sugerida.
- Limites da investigação; se nenhuma mudança útil for necessária, diga isso.

## Validação

Antes de entregar, confira o próprio trabalho:

- Os testes existentes do fluxo alterado passam.
- A propriedade arquitetural pretendida está verificada: a regra é testável sem a
  infraestrutura real, o adaptador cumpre o contrato e a dependência indevida é
  barrada pelo compilador, pela visibilidade ou por regra de arquitetura, quando
  o projeto oferece esse recurso.
- O cenário de mudança do passo 4 ficou mais barato; menos setas no diagrama
  com custo total maior conta como regressão.
- Substitutos em memória comprovam a regra, não o comportamento do banco ou
  serviço real; o que dependeu deles está declarado.

## Limites operacionais

Siga as regras do projeto e os limites do papel. Pedido de revisão não autoriza
editar. Corrigir estrutura não autoriza trocar banco, framework, protocolo,
esquema público ou modelo de implantação; mudanças de banco seguem a aprovação
humana prevista pelo projeto.
