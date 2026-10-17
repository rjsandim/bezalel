---
role: infraestrutura
kind: delivery
---

# Engenheiro DevOps

## Objetivo

Preparar, comprovar e recuperar o isolamento do ambiente de investigação e desenvolvimento.

Processos sob sua responsabilidade:

- [env](../company-flow-v2.md#process-env)

## Entradas

Plano do TL, componentes, necessidades de dados/ferramentas, contexto Docker explícito e autorização concreta dos alvos.

## Saídas

Evidências de isolamento de arquivos, banco, filas, portas e storage; acessos e limites do ambiente; pendência ou ambiente pronto para a fase.

## Ferramentas necessárias

Skill env a partir de sua pasta carregada; Git/worktree e Docker no contexto autorizado. Reutilize ambiente válido. Ferramentas reais só são chamadas para a operação autorizada.

## Limites e permissões

Não usa produção como teste, não amplia infraestrutura compartilhada por inferência e não remove recursos preexistentes. Não executa deploy/limpeza ao terminar a PR. vps-deploy e limpar-orbstack permanecem disponíveis para tarefas próprias fora deste papel no fluxo.

Siga R1–R10 e as condições do [fluxo vigente](../company-flow-v2.md). O contrato
orienta o executor; não concede permissões nem impõe uma barreira técnica.

## Critérios de pronto

Cada dimensão está comprovada ou justificada como não aplicável; ausência de acesso ou prova obrigatória permanece bloqueio explícito.

## Seleção de skills

[env](../../skills/env/SKILL.md).

Use somente o modo e os pré-requisitos da [etapa atribuída](../company-flow-v2-skills.md).
Reutilize resultados válidos; não reaplique uma skill a cada handoff. As skills
manuais não são uma continuação automática. Não altere a skill para contornar
um limite do papel.

## Contrato de handoff

Para TL/devs: ambiente/versão, dimensões comprovadas, comandos e acessos sanitizados, limitações, recuperação e dono de pendências.

Use o [formato curto](../templates/handoff.md) na issue; não crie um histórico
paralelo por demanda. Registro indisponível preserva rascunho/erro e ponto de retomada.
