# Concorrência

Use para estado compartilhado, tarefas concorrentes, coordenação, contenção ou encerramento.

## Concorrência, quando presente

Considere estes critérios somente quando o trecho envolver execução concorrente, estado compartilhado ou coordenação. Uma função `async` não exige, por si só, introduzir threads ou bloqueios.

Identifique quem possui e acessa o estado, quais operações precisam ser indivisíveis e onde outra execução pode interferir. Uma linha de código pode conter leitura, cálculo e escrita separados. Métodos seguros isoladamente não tornam atômica uma sequência de consulta e atualização.

- Para consultar existência e inserir, use uma operação composta com a garantia apropriada ou proteja toda a decisão e atualização.
- Se cada consumidor precisa combinar chamadas protegidas, considere uma API que represente a operação completa e concentre a coordenação.
- Restrinja pontos de acesso ao estado compartilhado. Avalie dados locais, imutabilidade ou cópias conforme os custos e contratos reais.
- Separe cálculo de negócio, agendamento e sincronização quando estiverem misturados, preservando o ciclo de vida e a ordem dos efeitos.
- Verifique o alcance do mecanismo: um bloqueio local de threads não coordena automaticamente processos, workers ou máquinas.

Mantenha a região crítica pequena sem separar etapas que precisam ser atômicas. Não use espera fixa como substituto de uma garantia de ordenação. Examine aquisição e liberação de recursos, cancelamento e encerramento; uma execução não deve aguardar indefinidamente um produtor já encerrado.

Uma ordem consistente de aquisição pode eliminar espera circular. Liberar recursos e tentar novamente pode introduzir starvation ou livelock; não adote tentativas sem limite como solução genérica.

Teste primeiro a lógica independente de concorrência. Depois, procure uma intercalação que exponha o risco e controle eventos com mecanismos apropriados quando possível. Verifique a garantia, como ausência de atualização perdida, e não apenas o término sem exceção. Varie carga ou plataforma quando a falha depender dessas condições e registre o contexto observado. Uma execução verde não prova a ausência de falhas raras.

Meça o gargalo antes de propor mais paralelismo. Espera por entrada e saída, contenção e processamento exigem decisões diferentes. Use as garantias atuais das bibliotecas do projeto; exemplos históricos de Java não determinam a tecnologia a adotar.

## Exemplo de operação composta

Considere a sequência conceitual `se a chave não existe, inserir o valor`. Duas execuções podem consultar antes de qualquer uma inserir. Mesmo que consulta e inserção sejam seguras isoladamente, a decisão conjunta pode não ser.

A correção depende da garantia desejada: uma operação atômica adequada, uma restrição da camada que possui os dados ou coordenação que cubra a decisão inteira. Não escolha um bloqueio local antes de verificar se os participantes estão na mesma instância, em processos diferentes ou em máquinas distintas.

Ao testar, procure exercer a intercalação relevante e conferir a invariante resultante. Um atraso fixo pode aumentar a chance de uma corrida, mas não prova que a sequência foi controlada nem corrige o problema.

## Estado compartilhado e responsabilidades

Separe a função que calcula um resultado da parte que escolhe quando executá-la e publica seus efeitos. Isso permite verificar a regra sem concorrência e concentrar a análise das regiões críticas. A separação só ajuda se o novo contrato continuar expondo os dados necessários e não esconder estado em um singleton ou campo mutável.

Prefira limitar quem pode modificar o recurso a depender de cada chamador lembrar a mesma disciplina. Quando uma sequência precisa ser protegida, uma operação composta na API pode ser mais confiável que repetir bloqueios nos consumidores.

## Deadlock e progresso

Deadlock pode envolver exclusão mútua, retenção de um recurso enquanto se espera por outro, ausência de preempção e espera circular. Identifique o mecanismo concreto antes de propor a solução. Uma ordem comum de aquisição pode romper a espera circular; aumentar indiscriminadamente recursos ou reiniciar tentativas pode apenas deslocar a falha.

Observe também progresso: starvation impede uma execução de conseguir os recursos; livelock mantém execuções reagindo umas às outras sem concluir. Uma política de repetição precisa de condições de término e deve pertencer ao contrato da operação, não ser acrescentada automaticamente pela refatoração.

## Encerramento e desempenho

Considere o destino de tarefas em andamento, a liberação de recursos e a notificação de quem aguarda. Uma fila vazia momentaneamente não significa necessariamente que todo trabalho terminou. Use a semântica do mecanismo presente no projeto para distinguir esses estados.

Em fluxos produtor-consumidor com fila limitada, confira a capacidade e o comportamento quando a fila fica cheia ou vazia. Preserve a política de espera, rejeição ou sinalização existente, salvo mudança requerida. Exercite os estados afetados e verifique se cancelamento e encerramento liberam quem aguarda. Uma melhoria de vazão não deve introduzir perda silenciosa de trabalho nem espera sem possibilidade de progresso.

Antes de paralelizar, examine o tempo gasto em processamento, espera e contenção. Depois de mudar a coordenação, valide o comportamento e, se desempenho for parte da justificativa, meça a condição relevante. Mais tarefas e mais bloqueios não representam, por si só, uma melhoria.
