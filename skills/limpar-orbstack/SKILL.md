---
name: limpar-orbstack
description: Audita e limpa ambientes locais explicitamente selecionados no OrbStack após comprovar integração e preservar dados. Use para ambientes, worktrees e imagens exclusivas concluídas; não executa prune global nem remove infraestrutura compartilhada.
---

# Limpar OrbStack

## Objetivo e escopo

Audite e, quando autorizado, remova ambientes concluídos de projetos identificados.
Um pedido para copiar, editar ou revisar esta skill não autoriza limpeza real.
Não remova máquinas Linux, produção, branches remotas ou recursos de outros projetos.

## Entradas e pré-requisitos

Exija projeto(s) e ambiente(s), ou um critério explícito de seleção dentro de um
conjunto de projetos. Não infira o escopo pelo diretório atual. Use Git, Docker
CLI e o contexto `orbstack` confirmado com `docker context inspect orbstack`.
Se indisponível, pare; não mude para outro contexto. Se usar a skill ENV, localize
a instalação explicitamente e leia seu contrato, sem caminhos fixos de agente.
A consulta a PRs/remotes, quando necessária, exige acesso já autorizado.

## Procedimento

1. Leia o [roteiro de auditoria](references/auditoria.md). Identifique recursos
   por registros, labels, caminhos e IDs exatos. Não selecione apenas por prefixo.
2. Comprove a integração do HEAD atual e preserve arquivos locais, ignorados e
   dados de volumes. Um merge não comprova que os dados locais são descartáveis.
3. Apresente alvos, impacto, itens preservados e recuperação. Um pedido explícito
   de limpeza autoriza os candidatos comprovados dentro daquele escopo; não
   amplie a seleção nem repita confirmação já inequívoca. Sem alvo/autorização,
   limite-se à auditoria e peça somente a informação que falta.
4. Siga [preservação e remoção](references/remocao.md), revalidando imediatamente
   antes de cada operação. Use `docker --context orbstack` em todo comando Docker.
5. Verifique o resultado de cada item. Falha, conflito ou mudança concorrente
   preserva o candidato; não aumente força ou alcance para terminar a limpeza.

## Saídas

Inventário por projeto, evidências de integração, elegíveis/bloqueados, plano de
preservação e, se executada a limpeza, resultados verificados por recurso.
Registre a recuperação fora do Git, com acesso restrito. Não inclua segredos,
dumps ou conteúdo privado no chat. Distinga remoção de tag de remoção da imagem.

## Validação

Esta skill é documental: revisão de links, metadados, cenários e contrato da ENV.
Ao alterá-la, não rode Docker mutável, limpeza ou integração real como teste.
Os cenários mínimos estão em [validação](references/validacao.md). A execução
real exige inventário e verificação do ambiente autorizado, sem prometer resultado
com base apenas em um código de saída ou em exemplos.

## Limites operacionais

Nunca execute `system prune`, `volume prune`, `image prune -a` ou limpeza por
prefixos amplos. Preserve Traefik, proxy, DNS, certificados, volumes e imagens
usados por qualquer ambiente preservado, inclusive containers parados. Não
reinicie OrbStack nem pare outros serviços para viabilizar a limpeza.

Imagens exigem prova de origem exclusiva e ausência de uso, revalidada antes de
`image rm` sem força. Qualquer incerteza de propriedade, integração ou backup
bloqueia aquele item. Não copie credenciais e não faça push ou exclusão remota.
