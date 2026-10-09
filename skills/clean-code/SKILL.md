---
name: clean-code
description: Revise e corrija o código criado ou alterado na tarefa usando os princípios de Código Limpo. Use durante implementação, correção de bugs, refatoração ou revisão de código para melhorar clareza, coesão e manutenção sem ampliar o escopo.
---

# Clean Code

## Objetivo e escopo

Aplique os princípios de **Código Limpo**, de Robert C. Martin, para tornar o código em desenvolvimento mais claro, coeso e fácil de manter. Esta skill reúne uma síntese dos resumos do livro e adaptações práticas ao trabalho em repositórios. Os exemplos internos são ilustrativos; não são transcrições nem dependem de um framework específico.

Todo o conhecimento necessário está nesta pasta. As referências abaixo usam caminhos relativos e acompanham a skill; não consulte o PDF, os resumos originais ou arquivos externos para conseguir aplicá-la.


- **Implementação ou correção:** incorpore melhorias pertinentes enquanto trabalha e revise o trecho alterado antes de concluir. Faça as correções locais autorizadas; não entregue apenas recomendações quando o pedido exige código corrigido.
- **Refatoração:** preserve o comportamento observável, salvo a mudança de requisito ou correção de bug solicitada. Considere retornos, erros, mutações, ordem de efeitos, interfaces públicas e formatos persistidos.
- **Revisão sem edição:** apresente problemas concretos, consequências e a menor correção apropriada. Um pedido de análise não autoriza alterar arquivos.
- Concentre a limpeza nos arquivos da tarefa e nos consumidores diretamente afetados. A regra do escoteiro significa melhorar o código tocado; não exige uma reescrita geral nem substituir o framework.

## Entradas e pré-requisitos

Use o pedido, os arquivos/diff relevantes, contratos, restrições e instruções do
projeto alvo. Identifique se o escopo é análise, implementação ou refatoração.
Não há runtime próprio nem dependências de execução desta skill; a validação
depende das ferramentas do projeto analisado.

## Procedimento

Entenda o propósito do trecho, os chamadores, as dependências e as verificações existentes antes de mudar a estrutura. Identifique o custo concreto: intenção ambígua, regra repetida, estado oculto, responsabilidade dispersa, recuperação inadequada de falhas ou dificuldade real de teste. Um método longo ou um nome pouco familiar, isoladamente, não demonstram um defeito.

Priorize manter o comportamento requerido, remover duplicação da mesma regra, expressar a intenção e evitar componentes desnecessários. Prefira a menor transformação que resolva o problema compreendido. Não encerre a análise apenas porque os testes passam: compreenda por que o algoritmo e seus limites estão corretos.

Faça mudanças em passos que permitam localizar regressões. Renomeações exigem conferir consumidores, inclusive reflexão, configuração, registro de eventos, serialização e API pública quando presentes. Se a limpeza revelar um bug fora da tarefa ou uma decisão de produto não resolvida, registre-o separadamente; não invente um contrato para tornar o código mais elegante.

### Referências sob demanda

Leia somente as referências necessárias ao trecho em análise. Uma alteração simples de nome não pede uma auditoria de arquitetura, concorrência ou testes do sistema inteiro.

| Situação | Referência interna |
|---|---|
| Nomes, unidades, funções, parâmetros, condicionais, comentários, duplicação e apresentação | [Legibilidade e funções](references/legibilidade-e-funcoes.md) |
| Classes, coesão, tipos, invariantes, construção e dependências implícitas ou externas | [Responsabilidades e fronteiras](references/responsabilidades-e-fronteiras.md) |
| Nulidade, valores padrão, exceções, conversões, compatibilidade e ordem de efeitos | [Erros e contratos](references/erros-e-contratos.md) |
| Código legado, transformações graduais, regressões, testes legíveis e verificações reproduzíveis | [Refatoração e testes](references/refatoracao-e-testes.md) |
| Estado compartilhado, operações atômicas, bloqueios, progresso e encerramento | [Concorrência](references/concorrencia.md) |

### Critérios de revisão

- Preserve o comportamento exigido e torne efeitos e dependências compreensíveis.
- Extraia conceitos e responsabilidades reais; não apenas distribua linhas.
- Unifique a mesma regra de negócio, sem forçar semelhanças superficiais a compartilhar uma abstração.
- Adote padrões e estruturas quando resolverem uma dificuldade observada.
- Use convenções e garantias atuais da linguagem e do projeto. Exemplos históricos de Java não impõem imports, ferramentas ou uma arquitetura universal.
- Dimensione a verificação ao risco e aos contratos afetados. Não crie testes que apenas espelhem a implementação nem uma suíte por uma mudança cosmética reversível.
- Não enfraqueça expectativas dos testes nem desative proteções para acomodar a nova implementação; investigue a divergência e diferencie falhas anteriores das introduzidas.

## Saídas

Entregue achados com localização, consequência e proposta concreta; quando
houver autorização para editar, entregue mudanças e evidências de validação.
Diferencie o que foi verificado de hipóteses e limitações.

## Validação

Pare a limpeza quando o problema concreto tiver sido resolvido e a verificação pertinente passar. Desfazer uma extração que piorou a clareza faz parte do refinamento. Se não houver melhoria útil no escopo, não produza alterações apenas para demonstrar o uso da skill.

Explique brevemente o que mudou, qual dificuldade foi removida e como o comportamento foi preservado ou deliberadamente corrigido. Informe limitações e verificações não executadas. As orientações são critérios de julgamento: não imponha cotas de linhas, uma asserção por teste, proibição absoluta de nulos, polimorfismo para toda seleção ou uma migração universal para orientação a objetos.

## Limites operacionais

Análise não autoriza alteração. Mantenha o escopo solicitado, preserve contratos
e use testes proporcionais ao risco. Não amplie a tarefa para migrações,
publicação, acesso a serviços ou mudanças destrutivas sem autorização aplicável.
