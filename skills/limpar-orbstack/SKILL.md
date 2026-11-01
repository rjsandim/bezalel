---
name: limpar-orbstack
description: Audita e limpa, no OrbStack, ambientes locais de projetos identificados cujas branches já foram integradas, preservando antes arquivos locais e dados; remove worktrees, branches locais, volumes e imagens exclusivas comprovadas. Use quando o pedido for "limpa os ambientes que já foram mergeados", "libera espaço no OrbStack", "quais worktrees posso apagar?" ou "remove as imagens das features concluídas", com projeto(s) e ambiente(s) ou um critério delimitado. Para encerrar um único ambiente da tarefa atual, use o destroy da skill env; para servidores remotos, use vps-deploy. Prune global e remoção de infraestrutura compartilhada ficam fora do escopo.
---

# Limpar OrbStack

## Objetivo e escopo

Auditar e, quando autorizado, remover ambientes concluídos de projetos
identificados, em lote, com backup do que não pode ser recriado. Máquinas Linux
do OrbStack, produção, branches remotas e recursos de outros projetos ficam fora.

Fronteira com a skill env: `env destroy` encerra **um** ambiente pelo nome, com
`--confirm`, e é o passo usado no fim de uma tarefa. Esta skill parte de um
conjunto de projetos, comprova a integração de cada ambiente, guarda a
recuperação, chama o `destroy` da env para cada candidato e trata também
worktrees, branches locais e imagens que o `destroy` não remove.

## Entradas e pré-requisitos

- Projeto(s) e ambiente(s), ou um critério explícito dentro de um conjunto de
  projetos. O escopo vem do pedido, independente do diretório atual.
- Git, Docker CLI e o contexto `orbstack`, confirmado com
  `docker context inspect orbstack`. Se faltar, pare e mantenha o contexto atual.
- `$ENV_SKILL_DIR`: pasta da skill env na instalação que criou os ambientes
  (por exemplo `.bezalel/base/skills/env` na integração direta). Confirme que
  `$ENV_SKILL_DIR/scripts/destroy.sh` existe e leia o contrato dessa versão.
- Acesso já autorizado a PRs e remotes, quando a prova de integração depender deles.

Um pedido para copiar, editar ou revisar esta skill não autoriza limpeza real.

## Procedimento

1. **Audite.** Siga o [roteiro de auditoria](references/auditoria.md):
   identifique recursos por registros, labels, caminhos e IDs exatos, nunca por
   prefixo.
2. **Comprove integração e preservação.** Para cada candidato, verifique que o
   HEAD atual está integrado e liste arquivos locais, ignorados e dados de
   volumes. Merge do código não torna esses dados descartáveis.
3. **Apresente o plano:** alvos, impacto, itens preservados e recuperação. Um
   pedido explícito de limpeza autoriza os candidatos comprovados dentro daquele
   escopo, dispensando nova confirmação. Sem alvo ou autorização, entregue só a auditoria
   e peça a informação que falta.
4. **Preserve e remova.** Siga [preservação e remoção](references/remocao.md),
   revalidando cada candidato imediatamente antes da operação e usando
   `docker --context orbstack` em todo comando Docker.
5. **Confira cada item.** Falha, conflito ou mudança concorrente mantém o
   candidato preservado e registrado.

## Saídas

Inventário por projeto, evidências de integração, candidatos elegíveis e
bloqueados, plano de preservação e, se houve limpeza, resultado verificado por
recurso. A recuperação fica fora do Git, com acesso restrito; segredos, dumps e
conteúdo privado ficam fora do chat. Remoção de tag e remoção de imagem são
relatadas separadamente.

## Validação

Antes de relatar, confira o resultado de cada candidato, como em
[verificação posterior](references/remocao.md#verificação-posterior):

- `git worktree list` e `git branch --list <branch>` deixaram de listar o que foi removido.
- `docker --context orbstack ps -a`, `volume ls` e `image ls` deixaram de listar os
  recursos exclusivos removidos, e mostram os preservados e a infraestrutura
  compartilhada (Traefik, rede proxy).
- O diretório de recuperação existe e contém os arquivos inventariados.

Código de saída zero, sozinho, não comprova a limpeza. Os cenários de revisão da
própria skill ficam em [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. `system prune`, `volume prune`,
`image prune -a` e limpeza por prefixo amplo ficam fora de qualquer pedido.
Traefik, proxy, DNS, certificados e volumes ou imagens usados por ambientes
preservados, inclusive containers parados, permanecem. Reiniciar o OrbStack ou
parar serviços de outros ambientes para viabilizar a limpeza também fica fora.

Imagem só é removida com prova de origem exclusiva e ausência de uso,
revalidada antes de `image rm` sem força. Incerteza de propriedade, integração ou
backup bloqueia aquele item. Credenciais não são copiadas; push e exclusão remota
ficam fora desta skill.
