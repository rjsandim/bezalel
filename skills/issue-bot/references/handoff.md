# Contrato de handoff

A raiz do pacote fica dois níveis acima da skill carregada. Leia
`agents/contracts/handoff.schema.json` (integração direta) ou
`contracts/contracts/handoff.schema.json` (plugin nativo). Use
`scripts/check_handoff.py --project P --issue N --round R --cycle C --role par`.
Os exemplos de cada papel estão em `agents/templates/` ou `contracts/templates/`.

Claude grava veredito, CI passed, candidato, cada critério com evidência, ajustes,
fora de escopo, skills usadas e data/fuso. Codex responde todos os bloqueantes com
IDs existentes, status, como e commit se corrigido. Arquivos por rename atômico;
não sobrescrever rodada anterior. Mais de duas rodadas exige decisão humana real.
JSON de decisão não autentica pessoa nem autoriza merge. Apenas sugestões são
compatíveis com pode_mergear; critério pendente/bloqueante não é.
