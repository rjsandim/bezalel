# Origem e adaptação autorizada

Base: [akitaonrails/my-skills/iss-audit](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a/iss-audit), revisão `7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a`.
Cópia e adaptação autorizadas por Rafael em 16/10/2026. O original baixado não foi
alterado; esta pasta é uma variante mantida pelo Bezalel, não uma cópia idêntica.

Preservados: separação de relato/hipótese, reprodução segura, refutação da causa,
duplicação, histórico de regressão, impacto de segurança e planejamento de evidências.

Alterados: modos de qualificação PM e investigação dev respeitam responsabilidades
distintas. Retirados implementação/merge/fechamento obrigatórios, inventário indiscriminado
de alertas com acesso amplo, ampliação automática do escopo e lista fechada de bloqueios.
A decisão de produto/banco continua humana; hipótese de segurança segue ao AppSec.
Lacunas reais podem aguardar evidência com dono e retomada, sem invalidar o relato.
A orientação de branches foi preservada para interoperabilidade manual; não há
encaminhamento automático para github-resolution.

Também foram retirados da entrada da skill: a fase “Approved Implementation” da
origem (github-resolution, se explicitamente chamada, é tarefa separada e confere
autorização real, objeto e decisões vigentes) e os rótulos de relatório “Fix now”,
“Fix with design caution” e “Documentation only”. As recomendações equivalentes
são **corrigir**, **propor mudança com decisão prévia** e **ajustar documentação**;
nenhuma delas autoriza implementação, merge ou fechamento.

Na revisão de 31/10/2026, o procedimento passou a ter passos numerados separados
em modo qualificação e modo investigação, e a descrição passou a cobrir pedidos
diretos ("investiga esse bug", "analisa essa issue") além do fluxo da DreamTeam.

A entrada e a interface foram traduzidas e organizadas no formato do Bezalel.
Detalhes condicionais foram movidos para referências próprias. Nenhum programa,
serviço, runtime ou definição de agente foi criado. Caminhos desta pasta são
relativos; a skill pode ser copiada com suas referências sem depender da raiz.
