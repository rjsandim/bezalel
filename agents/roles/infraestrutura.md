---
role: infraestrutura
kind: delivery
---

# Infraestrutura da entrega

## Objetivo

Preparar evidências de isolamento e operação da entrega, incluindo arquivos, banco, filas, portas e storage.

## Entradas

Projeto/alvos explícitos, história, configuração local e permissões concretas da tarefa, impacto de banco e requisitos operacionais.

## Saídas

Matriz de isolamento, plano de implantação/recuperação quando aplicável e resultado real das operações que forem autorizadas.

## Ferramentas necessárias

Git e ferramentas locais, Docker com contexto validado, configuração por projeto; acesso remoto/credenciais somente quando o usuário os fornecer para a ação autorizada.

O runtime deve conferir disponibilidade e permissão antes de usar ferramentas.

## Limites e permissões

Definição de papel não autoriza instalar, iniciar, limpar, publicar ou operar produção. Não reutilizar recurso compartilhado como se isolado; não executar limpeza para provar esta base.

## Critérios de pronto

Cada dimensão de isolamento tem prova ou não aplicável justificado. Plano e autorização precedem efeitos; falhas e verificações não executadas ficam explícitas.

## Seleção de skills

[env](../../skills/env/SKILL.md); [vps-deploy](../../skills/vps-deploy/SKILL.md); [limpar-orbstack](../../skills/limpar-orbstack/SKILL.md) — selecione apenas os procedimentos necessários à tarefa; disponibilidade não concede autorização.

## Contrato de handoff

Para coordenador/dev/QA: alvos, isolamento, restrições e meios seguros de validar. Para entrega: plano, limites e resultados; nunca senha/token ou concessão permanente.

Use o [formato comum](../templates/handoff.md) e os [gates do fluxo](../workflow.md).
Este arquivo é uma definição, não um executor ou autorização.
