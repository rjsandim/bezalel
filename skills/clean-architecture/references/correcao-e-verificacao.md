# Correção incremental e verificação

Use ao mudar uma fronteira ou definir como demonstrar sua correção. Os procedimentos aplicam os princípios dos [resumos](fontes.md) ao trabalho em repositórios.

## Delimitar o efeito

Identifique o contrato observado pelos consumidores e os cenários que devem continuar funcionando. Preserve falhas e efeitos relevantes: autorização, isolamento entre clientes, ordem de escrita e notificação, rollback, idempotência, eventos e limites de transação. São exemplos para fluxos em que já existem, não requisitos novos para qualquer aplicação.

Extrair código pode mudar quando uma transação começa, quando um erro é convertido, quantas vezes um provedor é chamado ou se carregamento tardio ainda funciona. Identifique esses pontos antes de movê-lo. Se faltar cobertura num caminho arriscado, registre o comportamento observável com uma verificação útil; não espelhe a estrutura atual em testes.

## Transformações típicas

| Problema demonstrado | Transformação | Evidência |
|---|---|---|
| Regra chama SDK ou banco diretamente | Contrato interno da operação; tradução no adaptador; ligação na composição | Regra sem serviço real e contrato do adaptador verificado |
| Modelo do ORM atravessa o núcleo | Mapeamento na borda para dados adequados à aplicação | Resultados, precisão, nulidade, identidade e carregamento preservados |
| Controlador contém política usada por outros canais | Caso de uso ao qual os canais delegam | Mesmas regras e restrições nos canais afetados |
| Atores compartilham regra que precisa divergir | Políticas distintas; compartilhamento só da semântica comum | Resultado de cada ator, inclusive o que não devia mudar |
| Consumidor contorna política obrigatória | Fluxo pela fronteira correta e acesso restrito quando viável | Cenário antes vulnerável e impedimento do desvio |
| Ciclo obriga vários módulos a mudar juntos | Inversão da aresta inadequada ou contrato coeso | Grafo corrigido e cenários dos consumidores |

Prefira uma fatia completa de ponta a ponta à reorganização horizontal do repositório inteiro. Atualize consumidores e composição, faça a nova ligação funcionar e remova o caminho substituído quando sua ausência de uso estiver demonstrada. Evite duas implementações da mesma regra evoluindo por acidente.

Quando uma migração exigir convivência entre caminhos antigos e novos, explicite quais chamadas passam por cada um, onde são feitas as traduções e qual evidência permitirá retirar o caminho antigo. Uma reescrita paralela precisa acompanhar mudanças que continuam chegando ao sistema existente; cópias por cliente ou região podem divergir e dificultar a transferência de correções. Use etapas verificáveis e evite vender o redesenho completo como solução inevitável. O caso SAC ilustra esse risco; o procedimento de migração aqui descrito é uma aplicação prática da lição. Fontes: 256–257.

## Isolar detalhes preservando requisitos

Banco ser detalhe tecnológico não torna esquema, integridade, consistência, consultas ou transações irrelevantes. Preserve as garantias no contrato e na implementação. Isolar persistência não obriga trocar a tecnologia. O livro distingue modelo de dados e exigência comercial de mecanismo de armazenamento. Fontes: 137–139, 210–213.

Web ser entrega não elimina autenticação, autorização, semântica HTTP ou interação rica. Isole a operação de negócio numa fronteira adequada, sem uniformizar toda interação entre console, navegador e outros canais. Fontes: 214–216.

Separar cálculo de mutação favorece regras determinísticas e testes. Isso não impõe programação funcional, event sourcing ou remoção de todo estado. Conserve as operações e garantias do produto. Fontes: 58–60.

## Demonstrar a correção

Combine as evidências necessárias ao problema, sem exigir uma nova suíte universal:

- **Comportamento:** resultados, erros e efeitos do fluxo; invariantes e autorização quando afetadas.
- **Núcleo isolado:** regra exercitada sem web, banco ou provedor real quando essa independência for o objetivo.
- **Integração:** implementação real respeita o contrato, inclusive falhas e transações pertinentes. Fake testa a política, não substitui essa evidência.
- **Estrutura:** compilação, visibilidade, tipos ou análise de dependências comprovam a fronteira. Uma regra arquitetural adicionada precisa aceitar o desenho válido e detectar o acesso proibido.
- **Composição:** a entrada real resolve a implementação correta; injeção manual em testes não prova a atualização do bootstrap.
- **Objetivo da mudança:** o cenário que motivou a fronteira ficou mais simples ou passou a atender a restrição operacional identificada, sem transferir um custo maior para testes, integração ou entrega.

Teste negócio por contratos estáveis, sem acoplá-lo à sequência de telas ou a métodos privados. Uma classe de produção não obriga uma classe de testes espelhada. Recursos exclusivos de teste que contornam controles não devem estar expostos na operação normal. Fontes: 160, 167–170, 192–194, 232–239.

Informe verificações não executadas e diferencie falhas anteriores das introduzidas. Testes locais aprovados não certificam uma integração não exercitada. Limite a conclusão aos fluxos e dependências examinados.
