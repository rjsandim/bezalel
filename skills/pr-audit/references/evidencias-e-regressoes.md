# Evidências e regressões na revisão técnica

Consulte somente as partes pertinentes ao diff. São critérios para o revisor
conferir e solicitar provas; não atribuem execução de testes ao TL.

## O teste demonstra a afirmação?

- Para correção comportamental, busque reprodução anterior ou evidência equivalente,
  teste relevante e resultado do candidato. Falha na base por import ausente,
  API nova ou erro de compilação não demonstra o bug. Quando o teste não roda
  na base, o executor pode isolar a alteração corretiva no candidato e mostrar
  falha pela asserção do comportamento, sem tocar a árvore compartilhada.
- Confirme que o teste percorre o código real: mocks, fixtures, helpers, defaults
  e condições não podem tornar a asserção vazia ou esconder a integração.
- Negativas, defaults, erro, falha parcial, recuperação e concorrência entram
  conforme o risco. Não exigir suíte nova para ajuste cosmético.
- Se só houve inspeção, declarar “confirmado por inspeção”; reprodução,
  ambiente emulado e execução nativa são tipos de prova distintos.

## O defeito reaparece por outro caminho?

Quando houver indício de recorrência, procure a correção anterior e seus limites.
Verifique chamadas irmãs, adapters e entradas existentes que compartilham a regra.
Uma nova rota não herda automaticamente a proteção de outra. Se o mesmo defeito
persiste, registre alcance e menor correção no ponto que realmente possui a regra;
não imponha reescrita de todas as superfícies sem demonstração.

Mudanças de estrutura de dados exigem localizar consumidores reais: API, web,
mobile, parsers gerados e espelhos mantidos à mão, conforme existam. Uma resposta
nova que só o produtor e um consumidor entendem não comprova integração do conjunto.

Alteração em caminhos, normalização, lock de arquivos ou finais de linha pede
evidências nas plataformas suportadas afetadas. Verde no Linux não prova Windows;
simulação não prova execução nativa. Registrar cobertura ausente sem inventar
labels, jobs ou uma nova matriz para projetos que não os possuem.

## Dependências e execução indireta

Inspecione dependências novas/alteradas e transitivas relevantes, origem/registro,
nome, checksums, lockfile, hooks de instalação, plugins de build e permissões de CI.
Observe execução de contribuição não confiável em workflows com segredos,
interpolação em shell, substituição de artefatos e ampliação de release/deploy.
Uma dependência de origem privada prevista pelo projeto não é, sozinha, maliciosa.

Cobertura do CI precisa corresponder aos arquivos/linguagens alterados, não só
ao framework predominante. Uma mudança no próprio workflow exige revisão do que
passou a ser executado; resultado verde por teste removido não satisfaz o requisito.

## Segurança e correções sensíveis

Relato, scanner e etiqueta “security” são pistas, não prova. Confira fronteira,
pré-condições, ativo exposto e versão real com AppSec. O revisor não executa PoCs.
Exija evidência apropriada do responsável: caso adversarial e controle legítimo
evitam confundir bloqueio de todos os usuários com correção. Não publique dados
sensíveis ou passos exploráveis; encaminhe pelo canal autorizado do projeto.

## Validade e retomada

Vincule resultado a commit ou artefato verificável, executor, ambiente e comando
ou método observado. Para reutilizar resultado, confira os insumos pertinentes:
fonte, dependências, toolchain, configuração, fixtures, schemas e workflows.
Mudança fora desse alcance pode preservar uma prova; mudança que o afeta pede
nova evidência do executor. Nunca renomeie um job pendente/cancelado como aprovado.

Mudanças de regra/contrato ou escopo voltam à decisão competente. Falha ordinária
de implementação pode ser corrigida pelo dev dentro da autorização vigente.
O TL acompanha o encaminhamento e revisa o resultado; não executa as correções.
