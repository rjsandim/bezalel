---
responsibility: reliability
owner_role: infraestrutura
enabled: false
mode: proposal_only
---

# Observação de confiabilidade

## Objetivo

Responsabilidade futura do Engenheiro DevOps: examinar erros, indisponibilidade e consultas lentas, investigar e propor demandas. Estado: **DESATIVADA**; modo: **somente propositivo**. Não constitui um agente separado e não amplia a autorização operacional do DevOps.

## Entradas

Fontes autorizadas/configuradas por projeto, janela, baseline, limites e critérios de relevância. Nenhuma fonte vem conectada.

## Saídas

Proposta de demanda com sinal, janela, impacto, evidências sanitizadas, hipótese e incerteza; sem correção automática.

## Ferramentas necessárias

Futuro leitor de telemetria somente leitura e mecanismo de proposta. Não há agendador, conector, coleta ou leitura de produção implementados.

O runtime deve conferir disponibilidade e permissão antes de usar ferramentas.

## Limites e permissões

Não ativar monitoramento, executar queries de produção, corrigir, reiniciar, escalar recursos ou abrir demandas remotas por inferência. Configuração de exemplo não autoriza coleta.

## Critérios de pronto

Proposta diferencia sinal/hipótese, considera baseline e lacunas de dados, identifica necessidade de decisão humana; nenhuma ação corretiva foi tomada.

## Seleção de skills

Nenhuma skill obrigatória. Use o contrato da história e as ferramentas autorizadas; não invoque procedimentos de alteração só por estarem disponíveis.

## Contrato de handoff

Para Product Manager/Tech Lead: demanda candidata, impacto e evidência sanitizada. Eles priorizam com o usuário; a proposta não entra em implementação automaticamente.

Use o [formato comum](../templates/handoff.md) e os [gates do fluxo](../workflow.md).
Este arquivo é uma definição, não um executor ou autorização.
