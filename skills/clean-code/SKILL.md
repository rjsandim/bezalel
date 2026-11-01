---
name: clean-code
description: Revisa e corrige o código criado ou alterado na tarefa com os princípios de Código Limpo (nomes, funções, duplicação, erros, testes legíveis e concorrência). Use quando o pedido for "limpa esse código", "melhora a legibilidade", "refatora essa função", "simplifica isso", "revisa o código que eu mudei" ou ao concluir uma implementação ou correção. Para fronteiras entre módulos, camadas ou direção de dependências, use clean-architecture; para achar a causa de um bug, use depurar-bug; para revisar uma PR inteira com evidências, use pr-audit.
---

# Clean Code

## Objetivo e escopo

Tornar o código da tarefa mais claro, coeso e fácil de manter, aplicando os
princípios de **Código Limpo**, de Robert C. Martin, adaptados ao trabalho em
repositórios. As referências desta pasta trazem a síntese e exemplos ilustrativos,
independentes de framework.

Escolha o modo de acordo com o pedido:

- **Implementação ou correção:** incorpore as melhorias pertinentes enquanto
  trabalha e revise o trecho alterado antes de concluir. Quando o pedido exige
  código corrigido, entregue o código, não apenas recomendações.
- **Refatoração:** preserve o comportamento observável, salvo a mudança de
  requisito ou a correção solicitada.
- **Revisão sem edição:** aponte problemas concretos, consequências e a menor
  correção apropriada, sem alterar arquivos.

O alcance é o código tocado e seus consumidores diretos. A regra do escoteiro
significa melhorar o que foi tocado, não reescrever o sistema ou trocar o framework.

## Entradas e pré-requisitos

- Pedido e modo (revisão, implementação ou refatoração).
- Arquivos ou diff da tarefa, chamadores, dependências e testes existentes.
- Instruções do projeto: convenções de linguagem, lint e comandos de teste.

A skill não tem runtime próprio; a verificação usa as ferramentas do projeto.

## Procedimento

1. **Delimite o trecho.** Liste os arquivos da tarefa e os consumidores
   diretamente afetados. Leia chamadores, dependências e testes antes de mudar
   a estrutura.
2. **Nomeie o custo concreto.** Para cada problema, diga qual dificuldade ele
   causa: intenção ambígua, regra repetida, estado oculto, responsabilidade
   dispersa, falha mal tratada ou dificuldade real de teste. Tamanho de método ou
   nome pouco familiar, sozinhos, não demonstram defeito.
3. **Consulte só a referência necessária** (tabela abaixo). Uma renomeação
   simples dispensa auditoria de concorrência ou de testes do sistema inteiro.
4. **Escolha a menor transformação** que resolva o custo. Liste o que precisa
   continuar igual: retornos, erros, mutações, ordem de efeitos, interfaces
   públicas e formatos persistidos.
5. **Aplique em passos pequenos** e rode os testes pertinentes entre eles. Em
   renomeações, confira consumidores por reflexão, configuração, eventos,
   serialização e API pública, quando existirem.
6. **Separe o que está fora da tarefa.** Bug alheio ou decisão de produto em
   aberto vira registro separado; o contrato atual continua valendo.
7. **Pare quando o problema estiver resolvido.** Desfaça extrações que pioraram
   a clareza. Sem melhoria útil no escopo, diga isso em vez de produzir mudanças.

| Situação | Referência |
|---|---|
| Nomes, unidades, funções, parâmetros, condicionais, comentários, duplicação e apresentação | [Legibilidade e funções](references/legibilidade-e-funcoes.md) |
| Classes, coesão, tipos, invariantes, construção e dependências implícitas ou externas | [Responsabilidades e fronteiras](references/responsabilidades-e-fronteiras.md) |
| Nulidade, valores padrão, exceções, conversões, compatibilidade e ordem de efeitos | [Erros e contratos](references/erros-e-contratos.md) |
| Código legado, transformações graduais, regressões, testes legíveis e verificações reproduzíveis | [Refatoração e testes](references/refatoracao-e-testes.md) |
| Estado compartilhado, operações atômicas, bloqueios, progresso e encerramento | [Concorrência](references/concorrencia.md) |

Critérios de julgamento:

- Extraia conceitos e responsabilidades reais, em vez de apenas distribuir linhas.
- Unifique a mesma regra de negócio; semelhança superficial não justifica abstração.
- Adote padrões quando resolverem uma dificuldade observada.
- Use as convenções atuais da linguagem e do projeto; os exemplos em Java do
  livro são ilustrativos.
- Dimensione os testes ao risco. Testes que espelham a implementação ou suítes
  para mudanças cosméticas reversíveis custam mais do que protegem.
- Diante de teste falhando, investigue a divergência e diferencie falha anterior
  de falha introduzida; a expectativa do teste só muda com motivo de requisito.
- As orientações são critérios, não cotas: linhas por função, uma asserção por
  teste ou polimorfismo para toda seleção são escolhas caso a caso.

## Saídas

- **Com edição:** código alterado, lista curta do que mudou, dificuldade removida
  e como o comportamento foi preservado ou deliberadamente corrigido.
- **Sem edição:** achados com arquivo/linha, consequência e menor correção proposta.
- Em ambos: verificações executadas, não executadas e hipóteses ainda abertas.

## Validação

Antes de entregar, confira o próprio trabalho:

- Os testes do projeto que cobrem o trecho alterado passam, e as falhas
  preexistentes estão identificadas como tais.
- Cada mudança do diff resolve um custo nomeado no passo 2; mudanças sem custo
  associado são revertidas.
- Consumidores de nomes ou assinaturas alterados foram localizados e atualizados.
- O comportamento listado no passo 4 continua igual, ou a diferença é a correção pedida.

## Limites operacionais

Siga as regras do projeto e os limites do papel. Pedido de revisão não autoriza
editar. A limpeza fica no escopo da tarefa; migrações, publicação, acesso a
serviços e mudanças destrutivas dependem de autorização própria.
