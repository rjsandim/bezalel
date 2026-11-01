---
name: proposta-banco
description: Prepara a proposta revisável de mudança de banco (tabela, coluna, índice, relação, migration ou transformação de dados) em HTML, com estrutura atual e proposta por entidade, riscos e reversão, e a apresenta para aprovação humana antes de qualquer implementação. Use quando o pedido for "preciso de uma migration para...", "adiciona a coluna X", "vamos mudar essa relação", "monta a proposta de banco" ou quando uma correção ou feature exigir mudar o schema ou os dados. Toda migration passa por essa aprovação. Para fronteiras e dependências no código, use clean-architecture; para snapshots de dados de desenvolvimento, use implementar-snapshots.
---

# Proposta de banco

## Objetivo e escopo

Usar o banco como guia para entender o problema e decidir antes de construir:
mostrar ao humano, com base no schema real, o que existe, o que muda, por que,
com que riscos e como voltar atrás. A proposta cobre mudança estrutural,
qualquer migration (inclusive só de dados) e relações complexas. A aprovação
humana da versão exata vem antes da migration e do código que depende dela.

## Entradas e pré-requisitos

- Necessidade e escopo da tarefa; repositório, branch e commit de base.
- Fontes reais do projeto: migrations, schema versionado, models e contratos.
  Produção fica fora da leitura.
- Template HTML do Bezalel `templates/database-review.html`: em
  `agents/templates/` nesta árvore e na integração direta
  (`.bezalel/base/agents/templates/`), em `contracts/templates/` no pacote de
  plugin. Sem o template, reproduza as mesmas seções e tabelas.
- `.bezalel/.gitignore` do projeto, para manter a cópia da tarefa fora do Git.

## Procedimento

1. **Fixe a base.** Registre repositório, branch e commit e liste os arquivos de
   schema e migrations lidos. Fonte ausente bloqueia a proposta: o estado atual
   nunca é inventado.
2. **Mapeie o impacto:** entidades afetadas, dados existentes e consumidores
   (API, web, mobile, jobs, relatórios, integrações).
3. **Monte o antes/depois por entidade**, uma linha por coluna: nome, tipo
   completo, relação (destino, cardinalidade e regra de exclusão), finalidade no
   negócio, regras (nulo, padrão, PK/FK, índices, restrições) e marcação
   **+ Adicionado**, **~ Alterado**, **− Removido** ou **= Mantido**. Em mudança
   só de dados, mostre seleção e transformação antes/depois.
4. **Escreva riscos e plano:** alternativa mais simples e motivo da escolha;
   backfill com volume estimado e origem da estimativa; compatibilidade dos
   consumidores; locks e desempenho; ordem entre banco, interface e
   consumidores; verificações antes/depois; reversão e o que ela não recupera.
5. **Gere o HTML.** Confira (ou acrescente, preservando as regras existentes)
   `/reviews/` em `.bezalel/.gitignore`. Copie o template para
   `.bezalel/reviews/database-<tarefa>-v<N>.html`, substitua todo `PREENCHER` e
troque o status "Modelo não preenchido" pela versão submetida.
   Mantenha-o autocontido, em UTF-8, sem scripts remotos, credenciais ou dados
   pessoais, e abra-o para inspecionar a renderização.
6. **Apresente para decisão:** caminho do arquivo, base, versão, resumo das
   diferenças, hash (`shasum -a 256 <arquivo>`) e os pontos que o humano precisa
   aprovar. Aguarde resposta explícita na conversa ou na issue.
7. **Ajuste pedido = nova versão.** Atualize o HTML como `v<N+1>`, recalcule o
   hash e reapresente; a aprovação vale só para a versão que ela cita.
8. **Feche após a decisão final.** Registre na issue ou conversa decisão, base,
   versão, resumo e hash; exclua as cópias da tarefa em `.bezalel/reviews/` e
   confirme a ausência. O template do pacote permanece.

## Saídas

- HTML da proposta, temporário e fora do Git, até a decisão final.
- Registro permanente na issue ou conversa: decisão humana, base, versão,
  resumo das diferenças e hash.
- Para quem implementa: a versão aprovada e as condições ligadas a ela.

## Validação

Antes de apresentar e ao fechar, confira o próprio trabalho:

- `grep -c PREENCHER <arquivo>` retorna 0.
- Toda entidade afetada tem tabela atual e proposta, e toda diferença tem cor e
  rótulo textual da legenda.
- O hash informado corresponde ao arquivo apresentado.
- A decisão registrada cita a versão e veio de uma interação real do humano.
- Depois da decisão final, `.bezalel/reviews/` não contém mais as cópias da tarefa.

## Limites operacionais

Siga as regras do projeto e os limites do papel. A proposta não implementa:
migration, código dependente e execução em qualquer banco aguardam a aprovação
da versão exata. Migration pequena, só de dados ou reversível passa pelo mesmo
caminho; sem mudança de banco, registre "não aplicável". Silêncio, hash,
exclusão do HTML ou aprovação de outra versão não contam como aprovação, e o
agente nunca decide pelo humano.
