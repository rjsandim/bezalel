# Problema e comportamento resultante

## Mudança

Issue, necessidade atendida, resultado e exemplo antes/depois quando útil.

## Validação

Candidato completo, componentes/repos/base/head, checks prévios, revisão TL,
AppSec, QA independente e integração pelo dev responsável. Informe limitações
reais e tratamento dos achados. Informe que o aceite humano está pendente, ou referencie a decisão real já existente da mesma versão.

## Roteiro e aceite

Roteiro pronto para o humano executar e decidir na PR: Excel em melhoria/feature;
no bug, formato pertinente. Gerar a planilha não executa testes. Artefatos e links
não podem conter segredos/dados privados nem ser publicados sem autorização.

## Banco, contratos e próximos passos

Proposta/decisão exatas quando houve estrutura, migration ou relações complexas;
caso contrário, não aplicável com razão. Registre compatibilidade, recuperação,
dependências e riscos. Abra/verifique PRs normais, prontas para revisão e sem draft; informe CI no estado
observado e orientações manuais ao humano. Não habilite merge/deploy automático. Após aprovação ou aviso humano, consultar merge no serviço; somente com todas as PRs mergeadas, fechar/verificar issues aplicáveis e encaminhar ao DevOps o encerramento do ambiente da branch registrada.
Este rascunho não comprova abertura ou execução: siga o
[processo de PR](../dream-team.md#process-pr).
