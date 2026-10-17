# Erros e contratos

Use ao alterar resultados, entradas opcionais, exceções, integrações, estado persistido ou sequência de efeitos.

## Erros, ausência e recuperação

Classifique falhas pela resposta que o chamador precisa dar. Se vários erros externos recebem a mesma recuperação, uma tradução local pode reduzir repetição; se exigem respostas distintas, preserve a diferença e o contexto diagnóstico. Não suprima a causa útil de uma falha ao trocar seu tipo.

Uma condição esperada do negócio pode ser representada por um resultado explícito ou caso especial. Coleção vazia só substitui ausência quando significa a mesma coisa no contrato. Indisponibilidade, acesso negado e dado desconhecido não devem se transformar em lista vazia, zero ou sucesso aparente.

Mantenha contratos válidos de nulidade e o modelo de erros da linguagem ou projeto. A preferência por exceções em exemplos do livro não exige substituir resultados tipados ou APIs públicas.

Verifique a recuperação além do sucesso: que estado permanece se a execução parar entre duas etapas? Trate a falha esperada ou propague-a com contexto. Preserve a liberação de recursos e a ordem dos efeitos. Não mude precisão numérica, regras de arredondamento ou representação monetária como efeito incidental de uma limpeza.

## Torne o comportamento observável explícito

Antes da alteração, identifique os aspectos do contrato realmente envolvidos:

| Aspecto | O que conferir |
|---|---|
| Entradas | Tipos, unidades, omissão, valores vazios, nulidade e defaults. |
| Saídas | Forma, ordem, precisão, identidade, mutabilidade, cópia ou mutação do objeto recebido. |
| Falhas | Tipo ou resultado de erro, contexto útil, momento em que ocorre e quem recupera. |
| Efeitos | Escritas, eventos, chamadas externas, número de execuções e ordem necessária. |
| Compatibilidade | Nomes públicos, parâmetros nomeados, formatos serializados e usos por configuração. |
| Contexto de conversão | Localidade, fuso e convenções de representação quando influenciarem o resultado. |

Não trate essa tabela como exigência de investigar todos os contratos do sistema: examine os que a mudança pode alcançar.

Uma data civil e um instante têm significados diferentes; converter entre eles pode exigir uma convenção de horário e fuso. Preserve a convenção requerida, sem impor UTC ou a configuração da máquina por preferência. Ao testar conversões dependentes de localidade ou fuso, controle o contexto relevante para que o cenário não mude silenciosamente entre ambientes.

## Ausência não é indisponibilidade

Uma consulta de itens pode produzir situações diferentes:

- Consulta bem-sucedida sem itens: uma coleção vazia pode representar o resultado.
- Serviço indisponível: o chamador pode precisar informar falha ou tentar uma recuperação autorizada.
- Acesso negado: pode exigir uma resposta própria de autorização.
- Dado ainda desconhecido: pode ser um estado válido e diferente de vazio.

Uma captura ampla que devolve `[]` em todos os casos apaga essas diferenças. Se esse comportamento já existir, não o mude sob o rótulo de simples refatoração: verifique o requisito e o escopo da correção. Dentro de uma correção autorizada, cubra o caso que antes produzia uma resposta enganosa.

## Tradução de falhas na fronteira

Agrupe erros externos quando o consumidor tiver a mesma ação de recuperação. Preserve distinções que mudem a decisão, como entrada inválida versus falha temporária. Conserve a causa e o contexto necessários ao diagnóstico, sem espalhar tipos específicos do fornecedor por toda a aplicação.

Capturar uma falha é assumir responsabilidade por sua recuperação ou tradução. Registrar uma mensagem e seguir como se a operação tivesse sido concluída não é, por si só, recuperação.

## Ordem de efeitos e interrupções

Se uma rotina grava dados e depois emite um evento, inverter essas operações pode tornar o fluxo visualmente mais agradável e ainda assim mudar o contrato. Antes de extrair ou reordenar, determine o que consumidores podem observar e qual estado fica após uma falha intermediária.

Preserve o tratamento de recursos: mover operações para fora do escopo de finalização pode alterar seu tempo de vida. Quando a mudança ultrapassar o mecanismo atual de consistência, descreva a necessidade concreta; não introduza novas políticas de transação ou repetição como parte incidental da limpeza.

## Requisito versus aparência

Retornar zero, `false` ou um objeto nulo pode parecer menos elegante e ainda ser um contrato válido. Nomear melhor e isolar a regra são opções diferentes de alterar esse contrato. Mudanças deliberadas devem ser apoiadas pelo requisito e por uma verificação do comportamento, não apenas por uma preferência do livro.
