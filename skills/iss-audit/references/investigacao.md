# Investigação técnica e classificação

Esta referência apoia o modo dev. No modo PM, use somente fatos e decisões já
disponíveis para qualificar; encaminhe as perguntas técnicas ao responsável.

## Evidências distintas

| Estado | Significado | Limite |
|---|---|---|
| Reproduzido | O caso falhou pelo comportamento alegado em execução identificada. | Delimitar versão, ambiente e entradas. |
| Confirmado por inspeção | O caminho e defeito são inequívocos no código examinado. | Não alegar execução ou equivalência de ambientes. |
| Plausível | O mecanismo faz sentido, mas faltam provas relevantes. | A hipótese não autoriza afirmar causa ou severidade. |
| Não reproduzido | Uma tentativa responsável não apresentou a falha. | Não invalida relatos de outra versão/configuração. |
| Informação insuficiente | Falta um fato necessário para discriminar alternativas. | Nomear fato, tentativa de obtê-lo, dono e retomada. |

Na qualificação sem investigação, registre “causa não investigada nesta fase”.
Não confunda esse estado com “informação insuficiente” da demanda inteira.

## Duplicação, versão e recorrência

Busque issues, PRs e histórico pertinentes quando houver indício de trabalho
anterior. “Já corrigido” exige indicar a correção e sua versão; quando não houver
prova de implantação, diga que a correção existe no código e o ambiente permanece
não verificado. Não abra outra implementação antes de entender a existente.

Se uma correção anterior existe mas o defeito voltou, diferencie reversão,
caminho paralelo sem proteção e correção incompleta. Procure entradas/consumidores
que realmente compartilhem a regra. Corrigir a classe significa tratar esse
alcance comprovado, não ampliar a tarefa para todas as plataformas por hipótese.

## Refutação da causa

Uma fila com contagem mudando pode indicar atraso transitório, não travamento
permanente. Compare observações dentro de janela adequada; não dispare processos
de produção para testar a tese. Se a causa proposta depende de registros órfãos,
confira se eles existem nos dados autorizados antes de propor uma correção.

Reprodução emulada deve explicitar qual semântica reproduz e o que não confirma
sobre a plataforma real. Reproduções negativas precisam de controles: ausência
de dados, permissão ou configuração pode impedir o próprio caminho sob análise.

## Segurança

Verifique versão, fronteira, pré-condições, exposição real e impacto alegado.
Scanner, CVE citado ou rótulo de urgência não bastam; consulte fonte primária
quando a alegação depender de versão ou comportamento externo.

PoCs recebidos permanecem não confiáveis. Reconstrua caso inerte em ambiente
autorizado; limite recursos/tempo para hipóteses de exaustão. Não exponha serviços,
credenciais, sessões pessoais ou dados de produção. Encaminhe o indício ao AppSec
com o que foi demonstrado e o que falta; abertura/publicação/encerramento de advisory
não faz parte desta auditoria.

## Plano de correção e prova

Informe o dono real da regra, comportamento antes/depois, consumidores afetados
e critérios observáveis. Proponha teste de regressão que falhe pelo defeito,
com controles negativos/legítimos e recuperação conforme o risco. Erro de import
ou compilação na base não prova a regressão; o executor deverá isolar o efeito
da correção ou escolher outra evidência.

Não converta planejamento em implementação. Experimentos de investigação ficam
identificados e separados do candidato. Resultado final de implementação e QA
será produzido depois, na fase e por responsáveis próprios. Questão de produto,
contrato ou banco ainda pendente bloqueia somente o trabalho dependente, conforme
a decisão do coordenador e as regras do projeto.
