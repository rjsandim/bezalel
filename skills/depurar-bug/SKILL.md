---
name: depurar-bug
description: Corrige um bug pelo ciclo reproduzir, isolar a causa com evidência, escrever o teste que falha, aplicar a menor correção, ver a regressão passar e registrar causa e prova. Use quando o pedido for "corrige esse bug", "esse teste está falhando, conserta", "dá erro 500 ao salvar, resolve", "voltou a quebrar depois da última versão" ou quando a investigação já apontou o defeito e falta corrigir. Para qualificar uma issue ou investigar sem corrigir, use iss-audit; para revisar a PR da correção, use pr-audit; para melhorar a legibilidade depois, use clean-code.
---

# Depurar bug

## Objetivo e escopo

Levar um defeito do sintoma à correção comprovada: a causa é demonstrada antes
de mexer no código, um teste automatizado falha pelo motivo certo, a menor
mudança o faz passar e a prova fica registrada. Serve a bugs de backend, web,
mobile, scripts e testes instáveis com causa no código.

## Entradas e pré-requisitos

- Relato do sintoma: comportamento observado e esperado, versão ou commit,
  ambiente e passos ou entrada que o provocam.
- Diagnóstico anterior, quando existir (por exemplo, o registro do iss-audit).
- Ambiente isolado para reproduzir (local, worktree ou ambiente da skill env) e
  o runner de testes do projeto.
- Escopo autorizado da correção e instruções do projeto.

## Procedimento

1. **Fixe o sintoma.** Escreva em uma frase o observado e o esperado, com versão,
   ambiente e a menor entrada conhecida. Reaproveite o diagnóstico existente.
2. **Reproduza** em ambiente isolado, com dados sintéticos, e guarde o comando e
   a saída. Se não reproduzir, volte à investigação (iss-audit, modo
   investigação) ou registre o limite; correção às cegas fica para depois da
   reprodução.
3. **Isole a causa com evidência.** Reduza a entrada, leia o caminho real do
   código, use logs ou depurador e, em regressão, `git bisect` entre a última
   versão boa e a ruim. Para cada hipótese, defina o controle que a derrubaria;
   a causa é a explicação que sobreviveu ao controle e explica o sintoma inteiro.
4. **Escreva o teste que falha** no nível mais baixo que exercita a causa
   (unitário ou de integração). Rode-o e confirme que a falha corresponde ao
   defeito, não a erro de montagem do teste.
5. **Corrija com a menor mudança na causa**, não no sintoma. Refatoração fica
   para depois (clean-code); mudança de banco ou migration segue antes a
   proposta-banco com aprovação humana; regra de negócio ambígua volta ao
   responsável pela decisão.
6. **Prove a correção.** O teste novo passa, os testes da área continuam
   passando e a reprodução do passo 2 não mostra mais o sintoma. Se a causa
   sugerir vizinhos (limites, nulos, concorrência, outros consumidores), cubra-os.
7. **Registre causa e prova:** arquivo/linha da causa, por que acontecia, o que
   mudou, o teste de regressão e os comandos com resultado. Indique o alcance:
   outras rotas, dados já afetados ou versões publicadas.

## Saídas

- Correção mínima e teste de regressão no mesmo diff.
- Registro curto na issue, PR ou conversa: sintoma, causa comprovada, correção,
  prova (teste falhando antes e passando depois) e alcance.
- Pendências explícitas: dados já corrompidos, decisão de produto, causa
  parcialmente explicada ou ambiente que impediu a reprodução.

## Validação

Antes de entregar, confira o próprio trabalho:

- O teste novo falha sem a correção (na base ou revertendo só o código
  corrigido) e passa com ela.
- A reprodução original não mostra mais o sintoma.
- A suíte da área afetada passa; falhas preexistentes estão identificadas como tais.
- O diff contém apenas a correção, o teste e o que eles exigem.
- O registro aponta a causa com evidência, não só a mudança feita.

## Limites operacionais

Siga as regras do projeto e os limites do papel. Reprodução em produção ou com
dados reais só com escopo autorizado. Teste existente que falha é investigado:
desativá-lo ou afrouxar a expectativa para obter verde fica fora da correção.
Indício de vulnerabilidade vai ao AppSec com a evidência. Push, merge e deploy
seguem o fluxo do projeto.
