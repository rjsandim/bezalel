# Refatoração e testes

Use em transformação de código legado, correção de comportamento e escolha das verificações necessárias.

## Refatoração e testes

Diferencie comportamento existente, requisito pretendido e melhoria ainda não solicitada. Retornos pouco elegantes podem ser contratos públicos. Testes de aceitação e de integração podem proteger garantias ausentes da suíte de unidade; consulte os consumidores relevantes.

Se o comportamento for pouco conhecido e a transformação tiver risco real, registre-o antes com uma verificação de caracterização útil. Para um bug solicitado, procure um caso que exponha a falha e comprove o resultado corrigido. Não cristalize um defeito conhecido como requisito sem distinguir essas situações.

Se um teste antes verde falhar, investigue antes de acumular mudanças. Não altere a expectativa para acomodar a nova estrutura. Diferencie falhas anteriores das introduzidas pela refatoração.

| Alteração | Evidência proporcional |
|---|---|
| Renomeação interna ou formatação | Usos resolvidos, análise estática e verificações existentes pertinentes. |
| Extração ou mudança de representação | Resultados, erros e efeitos preservados nos caminhos afetados. |
| API ou adaptador | Chamadores e contrato de integração, incluindo entradas e falhas externas. |
| Algoritmo ou regra corrigida | Caso que reproduz o defeito e fronteiras próximas relevantes. |
| Estado ou sequência de operações | Estado final e efeitos observáveis, incluindo interrupções e recuperação. |

Não crie testes que apenas espelhem a implementação nem uma suíte nova por uma alteração cosmética reversível. Cobertura localiza caminhos não exercitados, mas não demonstra sozinha que o requisito foi atendido. Não persiga uma porcentagem sem benefício concreto.

Se um teste parecer exigir acesso a detalhes privados, procure primeiro verificar o contrato existente ou separar uma responsabilidade real. Quando ampliar a visibilidade for necessário, use o menor alcance compatível com o projeto. Facilitar um teste, por si só, não justifica transformar estado interno em API pública.

Organize os cenários em preparação, ação e verificação, usando a linguagem do comportamento. Prefira um conceito por teste. Várias asserções podem comprovar um resultado coerente; separá-las não deve duplicar toda a preparação sem melhorar o diagnóstico.

Extraia detalhes repetidos de infraestrutura para auxiliares que expressem ações do domínio. Mantenha visíveis os dados que determinam o cenário e o resultado esperado: esconder uma condição decisiva em uma preparação global torna o teste difícil de interpretar. Prefira uma comparação que mostre qual propriedade divergiu a uma sequência compacta de símbolos que exija decodificação. A linguagem dos testes deve surgir de necessidades reais, sem criar um framework próprio para economizar poucas linhas.

Busque as qualidades F.I.R.S.T.: rapidez, independência, repetibilidade, autovalidação e criação no momento oportuno. Aproveite o ciclo de teste que falha, correção mínima e refatoração quando couber à tarefa, sem exigir reconstruir o processo da equipe.

Controle tempo, aleatoriedade e serviços externos quando necessário ao cenário. Uma implementação falsa, isoladamente, não comprova que a integração funciona.

Escolha limites próprios do algoritmo: vazio, um elemento, fim do intervalo, igualdade, inclusão ou exclusão, mudança de mês ou ano e entrada inválida quando relevantes. Bugs encontrados justificam examinar fronteiras próximas que compartilham a mesma regra. Preserve as garantias dos testes quando métodos internos mudarem; não elimine uma garantia apenas porque sua implementação foi movida.

## Aprendizagem e mudanças de dependência

Quando uma API externa for pouco conhecida, pequenos testes com seu uso real permitem separar uma hipótese errada sobre a biblioteca de um defeito da aplicação. Exercite apenas o contrato utilizado, incluindo a configuração necessária e as falhas relevantes. Preserve esses testes junto do projeto quando registrarem conhecimento útil; eles podem revelar incompatibilidades numa atualização da dependência.

Uma implementação falsa ajuda a desenvolver o consumidor enquanto uma integração não está disponível. Ela não confirma as hipóteses feitas sobre o fornecedor. Quando essa fronteira estiver no escopo da tarefa, verifique o adaptador contra o comportamento real disponível ou declare a lacuna de validação.

## Execução reproduzível e proteções

Use os pontos de entrada existentes para construir o projeto e executar as verificações pertinentes. Se a tarefa alterar essa infraestrutura, mantenha uma execução clara e reproduzível, sem passos manuais dependentes de conhecimento não registrado. Uma falha na preparação não equivale a um teste executado. Corrija o impedimento dentro do escopo ou informe o que não foi possível verificar; não reforme todo o ambiente por causa de uma limpeza local.

Não desative testes, verificações de tipo, avisos pertinentes ou controles de compatibilidade apenas para obter sucesso. Investigue o diagnóstico. Se uma supressão for tecnicamente justificada, limite-a ao caso necessário e registre por que o diagnóstico não se aplica. Testes ignorados podem representar requisitos sem resposta; não os apague nem os reative indiscriminadamente sem compreender o motivo.

## Sequência prática de refinamento

Para uma transformação relevante, estabeleça o comportamento necessário, escolha uma mudança pequena e execute a verificação que pode revelar sua regressão. Revise o resultado antes de acumular outras transformações. Se a decomposição criou mais estado, parâmetros artificiais ou navegação, considere desfazê-la.

Essa sequência não exige um teste novo para cada edição. Uma renomeação interna pode ser bem sustentada pelos usos resolvidos e pela suíte existente. Uma alteração numa regra de datas precisa de casos que exerçam a fronteira envolvida, não de um teste que apenas confira o nome do novo método.

Se substituir uma representação de uma vez impedir verificações intermediárias, migre seus usos em etapas. A coexistência temporária deve manter uma fonte consistente dos dados e evitar efeitos repetidos. Retire os caminhos e adaptações antigos quando seus consumidores forem migrados. Esse apoio à refatoração local não exige introduzir um mecanismo permanente de sincronização ou uma migração de produção.

## Exemplo: unificar armazenamento

Suponha que valores antes guardados em mapas separados por tipo passem a um mapa único. A busca pode continuar funcionando nos casos habituais e passar a falhar quando a chave existe com outro tipo. Antes, a separação das estruturas podia garantir implicitamente um valor padrão para essa consulta.

Ao refatorar, descubra qual garantia os chamadores precisam: ausência, erro ou valor padrão. Verifique essa situação junto dos casos usuais. Não troque a expectativa de um teste de aceitação apenas porque a representação nova tornou a antiga resposta menos conveniente.

## Exemplo: cálculo em um limite

Num algoritmo de intervalo, identifique se as extremidades são abertas ou fechadas. Um teste apenas com um valor no meio não distingue essas regras. Para uma alteração nessa decisão, teste os limites pertinentes e um valor imediatamente fora quando isso for expressável no domínio.

O mesmo raciocínio vale para calendário: fim de mês e transição de ano podem exercitar regras que um dia comum não alcança. Escolha casos a partir da operação modificada; não crie uma matriz exaustiva sem relação com o risco.

Confira também a composição das operações. Somar um mês duas vezes pode diferir de somar dois meses de uma vez quando cada etapa ajusta o dia ao último dia do mês. Arredondamento e saturação em limites também podem invalidar um reagrupamento aparentemente equivalente. Se a transformação acumular ou reordenar cálculos, verifique o efeito dos ajustes intermediários.

## Leia falhas como evidência

Uma regressão localizada após uma pequena alteração ajuda a encontrar a hipótese quebrada. Compare os casos que passam e falham, confira a representação dos dados e a ordem das chamadas. Cobertura pode indicar um ramo nunca exercitado, mas a explicação do resultado ainda depende do contrato e do algoritmo.

Ao relatar a validação, diferencie teste executado, resultado observado e limite da conclusão. Uma implementação falsa verifica o consumidor em condições controladas; a integração real exige sua própria evidência quando estiver no escopo.
