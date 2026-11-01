# Bezalel

**Bezalel** é o plugin completo de agentes e skills.
**DreamTeam** é sua equipe de nove agentes para corrigir bugs e desenvolver melhorias e features.
O fluxo é mantido nos arquivos do pacote, sem depender de ferramenta externa de modelagem.

O plugin reúne a DreamTeam, seu fluxo de desenvolvimento e 18 skills, incluindo nove
importações com conteúdo preservado e duas auditorias adaptadas.
Há contratos portáteis, adaptadores para Codex e Claude Code, instalação por
projeto, pacote de plugin e validadores locais.
A execução depende do aplicativo e das ferramentas do projeto; não há serviço
hospedado, monitoramento ou runtime próprio que aplique autorizações.

## Inventário de skills

As **18 skills disponíveis** estão organizadas pelo uso: **11 indicadas no
fluxo da DreamTeam**, **cinco reservadas à chamada manual** e **duas operacionais
fora do fluxo**. A indicação no fluxo depende da etapa, do escopo e dos
pré-requisitos; não significa executar todas em cada demanda.

### Indicadas no fluxo da DreamTeam

| Skill | Finalidade | Implementação |
|---|---|---|
| [clean-code](skills/clean-code/SKILL.md) | Revisar e corrigir código dentro do escopo | Markdown e referências |
| [security-audit](skills/security-audit/SKILL.md) | Auditar vulnerabilidades com modelo de ameaças e evidências | Skill original de akitaonrails/my-skills, com referências e inventário Bash |
| [clean-architecture](skills/clean-architecture/SKILL.md) | Revisar responsabilidades e dependências | Markdown e referências |
| [env](skills/env/SKILL.md) | Gerenciar ambientes locais por worktree e Docker | Bash, Python auxiliar e templates |
| [implementar-snapshots](skills/implementar-snapshots/SKILL.md) | Construir snapshots full/tiny com sanitização, integridade e destino isolado | Markdown, modelo de política e fixture sintética |
| [development-test-workbook](skills/development-test-workbook/SKILL.md) | Criar roteiros manuais em Excel com casos, evidências e backlog | Python/openpyxl, template vazio e fixtures sintéticas |
| [verification-planning](skills/verification-planning/SKILL.md) | Planejar evidências proporcionais ao risco | Skill original de akitaonrails/my-skills; pesquisa via @librarian é uma dependência condicional não fornecida aqui |
| [humanizer](skills/humanizer/SKILL.md) | Revisar redação preservando fatos, critérios e referências | Pacote original completo, com licença e validador local |
| [agent-browser](skills/agent-browser/SKILL.md) | Apoiar reprodução de bugs de interface e jornadas/E2E web | Stub original; depende de CLI e guias da versão disponíveis |
| [iss-audit](skills/iss-audit/SKILL.md) | Separar qualificação PM e investigação técnica de demandas | Variante Bezalel autorizada, com referências e origem |
| [pr-audit](skills/pr-audit/SKILL.md) | Revisar candidato integrado/PR sem executar testes nem corrigir | Variante Bezalel autorizada para revisão técnica |

### Reservadas à chamada manual

Estas cinco skills ficam fora das etapas do fluxo da DreamTeam e têm metadados de
invocação explícita. Não são iniciadas ao concluir uma auditoria ou entregar uma PR.

| Skill | Finalidade | Implementação |
|---|---|---|
| [release](skills/release/SKILL.md) | Preparar e publicar versões quando solicitado | Conteúdo original; chamada manual, fora do fluxo da DreamTeam |
| [reflect](skills/reflect/SKILL.md) | Avaliar padrões recorrentes e propor melhorias | Conteúdo original; chamada manual, fora do fluxo da DreamTeam |
| [github-resolution](skills/github-resolution/SKILL.md) | Executar resoluções auditadas e autorizadas | Conteúdo original; chamada manual, fora do fluxo da DreamTeam |
| [pr-bump](skills/pr-bump/SKILL.md) | Consolidar atualizações de dependências de bots | Conteúdo original com exemplos Rails; chamada manual |
| [pr-post-audit](skills/pr-post-audit/SKILL.md) | Auditar a composição de mudanças antes de release/deploy | Conteúdo original; apoio manual de release/github-resolution |

### Operacionais fora do fluxo

Procedimentos já existentes para tarefas específicas autorizadas. A entrega de
uma PR não inicia deploy nem comprova que um ambiente pode ser removido.

| Skill | Finalidade | Implementação |
|---|---|---|
| [vps-deploy](skills/vps-deploy/SKILL.md) | Orientar operações de VPS com configuração por projeto | Markdown e validador Python |
| [limpar-orbstack](skills/limpar-orbstack/SKILL.md) | Auditar e limpar ambientes explicitamente autorizados | Markdown e roteiros de preservação |

O [inventário de todas as skills analisadas](agents/skills-inventario.md)
e a [relação por processo e etapa](agents/dream-team-skills.md) registram a
seleção de 11 skills em 24 etapas do fluxo da DreamTeam. As cópias ficam somente nesta árvore;
os agentes referenciam os métodos pertinentes sem instalar ferramentas ou alterar
as instalações globais.
As cinco novas skills manuais têm [condições de uso próprias](agents/skills-uso-manual.md)
e metadado de invocação explícita; não são chamadas pelas etapas do fluxo.

## DreamTeam e seu fluxo de desenvolvimento

A [DreamTeam](agents/README.md) contém contratos e adaptadores para Product
Manager, Tech Lead, DevOps, desenvolvedores fullstack/backend/web/mobile, QA e
AppSec. O aprovador humano é externo. Os [21 processos do fluxo](agents/dream-team.md#processos)
são distribuídos por responsabilidade no [catálogo](agents/catalog.json); não há
um agente para cada etapa. O TL coordena e revisa; um dev assume a integração
inteira. QA e AppSec verificam independentemente dos autores.

Cada agente lê o próprio contrato, as regras comuns de `agents/dream-team.md` e
somente os arquivos dos seus processos em `agents/processes/`. Os 18 adaptadores
Codex/Claude e o índice de processos do fluxo são gerados por `scripts/dream_team.py`
a partir do catálogo, dos contratos, dos processos e do template
`scripts/dream-team-adapter.txt`; não os edite à mão. Depois de mudar essas fontes,
rode `python3 -B scripts/dream_team.py generate`. O checker falha quando um arquivo
gerado diverge.

O percurso é intenção/qualificação → planejamento e isolamento → investigação →
interface/banco quando aplicáveis → implementação e integração → revisão TL,
AppSec e QA → roteiro → PR aberta → aceite humano na PR. Ao receber aprovação ou
aviso de merge, TL verifica o merge no serviço, fecha/verifica issues concluídas
quando existirem e encaminha o encerramento do ambiente ao DevOps. Abertura de PR
faz parte do desenvolvimento solicitado: PR normal, pronta para revisão, sem draft. Não exige nova pergunta após validação,
salvo restrição expressa. Aprovação não prova merge. Merge e deploy continuam manuais.

Estrutura, qualquer migration ou relações complexas exigem uma proposta baseada
no schema/migrations e commit reais do projeto. O [template HTML](agents/templates/database-review.html)
mostra estrutura atual e proposta em tabelas com nome da coluna, tipo, relação e
finalidade de uso, além de regras, diferenças, impactos, alternativas e recuperação.
Destaques visuais e legenda com cores e rótulos distinguem adições, alterações,
remoções e itens mantidos; blocos monocromáticos de texto/SQL não substituem as tabelas.
A cópia da tarefa fica em `.bezalel/reviews/`, ignorada no Git; confira a regra
`/reviews/` no `.bezalel/.gitignore` antes de gerar. Ajustes são reapresentados.
Após decisão final, registre resumo, base, versão, hash e decisão na issue/conversa
antes de excluir/verificar o HTML temporário. O template do pacote permanece.

Novas branches, worktrees e ambientes ENV usam o mesmo nome: uma descrição curta
em minúsculas, sem acentos, com palavras separadas por hífens, como `corrigir-login`
ou `ajustar-cadastro-empresa`. Números cabem quando têm significado, como em
`migrar-php-84`; não há sufixo aleatório obrigatório nem prefixos como `codex/`,
`feat/` ou identificadores do agente. A pasta é `.worktrees/<nome>`.

O pedido `env destroy {{current-worktree-branch}}` é resolvido pelo registro da
branch/worktree da tarefa: em ambientes preexistentes, o nome pode diferir da branch. DevOps
confere o vínculo e executa o destroy da skill com confirmação exata de projeto e
ambiente, após preservar dados/arquivos necessários fora da worktree. Sem ambiente
registrado, informe não aplicável. Falhas, arquivos locais ou commits que impeçam
remoção mantêm pendência; squash/rebase não autoriza força. Não há limpeza geral,
remoção de pools/imagens compartilhados ou destruição pelo simples aceite da PR.

A issue existente é a fonte da demanda; sem issue, use a conversa e a PR. Os [modelos](agents/templates/user-story.md) ajudam
na redação de requisitos, proposta e handoff, sem exigir MD paralelo por tarefa.
O [registro](agents/record-contract.md) é um snapshot local opcional para
conferência: investigação, UI/banco, candidato, revisões, risco, aceite e PRs.
O CLI só valida declarações; não autentica decisões, executa comandos ou consulta
o GitHub. Passar no checker não prova a veracidade das evidências.

A [economia de contexto e coordenação](agents/dream-team.md#economia-de-contexto-e-coordenação)
orienta os agentes a comunicar mudanças relevantes, delegar entregas completas por
fase, fornecer contexto delimitado com fontes acessíveis e reutilizar evidências
cuja versão e cobertura continuem válidas. Preserva revisões independentes, testes
obrigatórios e aprovações. Projetos consumidores recebem essas instruções ao
atualizar o pacote/vínculos pelo procedimento abaixo; arquivos não impõem limites
nem comprovam economia de tokens, que precisa ser medida no uso real.

Quem inicia a conversa indica o modelo mais apropriado para a demanda e para cada
atribuição. A [política de modelos](agents/dream-team.md#seleção-proporcional-de-modelos)
prioriza o menor modelo suficiente, preferindo opções menores que o modelo inicial.
A delegação explicita a escolha quando suportada; manter ou aumentar a capacidade
exige justificativa. O handoff registra recomendação e, quando confirmado, modelo
usado. Não há modelo fixo por papel nem troca automática da conversa. Sem suporte
na aplicação, o agente informa a limitação; instalar arquivos não comprova redução
de uso. Projetos existentes recebem a regra ao atualizar seus vínculos gerenciados
pelo procedimento de atualização abaixo, respeitando customizações e colisões.

Os contratos e adaptadores estão preparados. Descoberta no aplicativo, ferramentas
reais e piloto no projeto consumidor precisam ser verificados antes de alegar
operação validada. Os testes locais usam fixtures sintéticas, sem decisões reais.

## Estrutura comum

As skills mantidas no Bezalel declaram `name` e `description` e contêm objetivo/escopo,
entradas/pré-requisitos, procedimento, saídas, validação e limites operacionais.
`references/`, `scripts/`, `templates/` e `tests/` aparecem quando necessários.
`agents/openai.yaml` é um adaptador opcional de interface, não um agente em
execução. As cinco novas skills manuais, ENV, VPS e limpar-orbstack usam invocação
explícita nesse metadado. As demais podem ser selecionadas em tarefas compatíveis,
conforme os metadados preservados e as ferramentas disponíveis. A interpretação
pelo aplicativo deve ser conferida nele; este repositório não certifica loaders.

`security-audit`, `humanizer`, `verification-planning`, `agent-browser`, `release`,
`reflect`, `github-resolution`, `pr-bump` e `pr-post-audit` são exceções de importação:
seu conteúdo é mantido sem alterações, inclusive idioma e estrutura, conforme
a [origem fixada](https://github.com/akitaonrails/my-skills/tree/7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a).
Revisão inicial: `7b8a5e5e0259da8cabcdaf806cca9d1d55abf20a`. As revisões adotadas
por skill constam de [.bezalel/upstream.json](.bezalel/upstream.json). Em 16/10/2026,
humanizer, verification-planning e agent-browser foram copiadas integralmente;
a security-audit existente foi preservada. Nas cinco manuais, somente os adaptadores
de invocação foram acrescentados ou receberam a política explícita; seus SKILL.md
permanecem idênticos. pr-audit e iss-audit foram copiadas e adaptadas com autorização,
com motivos e origem nas próprias referências. O inventário registra limitações e
diferenças locais preexistentes. Instalação não autoriza executar comandos, adaptar conteúdo
ou realizar alterações externas. A indicação de uma skill não substitui os
limites do responsável nem a decisão humana.

## Como adotar o Bezalel em um projeto

A integração direta é a opção recomendada para o fluxo da DreamTeam e para projetos
que usam ENV: mantém a base em um caminho estável e preserva seu estado operacional.
Requer Git, Python 3.11+, macOS/Linux e os aplicativos já instalados. Não instala
CLIs, Docker, credenciais ou serviços. Use uma única modalidade por projeto.

### Ligar no projeto

Na raiz de um projeto Git, depois que esta versão estiver publicada no Bezalel:

```sh
git clone --branch master --single-branch https://github.com/rjsandim/bezalel.git .bezalel/base
python3 -B .bezalel/base/scripts/project.py enable --project . --platform both
```

Use `--platform codex` ou `--platform claude` se utilizar apenas um aplicativo.
O clone recusa destino ocupado. Uma instalação manual anterior precisa ser
comparada e reconciliada: o instalador não adota arquivos ou links desconhecidos.
Cada publicação aprovada na `master` valida o pacote e atualiza o canal de plugins.

O instalador disponibiliza as skills e os nove agentes, acrescenta blocos curtos
em `AGENTS.md`, `CLAUDE.md` e README, preserva o restante desses arquivos e prepara
o hook de atualização. Ele não substitui as regras do projeto pelo `AGENTS.md`
de contribuição do Bezalel. Configurações e hooks de terceiros são preservados.

Preencha `.bezalel/project.json` com o nome do projeto, documentos reais de
arquitetura e negócio, interfaces, comandos de teste/lint/build e branches de
produção. O exemplo só é copiado se o arquivo não existir; preencher contexto é
necessário antes de executar o fluxo. Comandos declarados não são executados na
instalação. Configure MCPs e pré-requisitos das skills conforme a tarefa.

No Codex, as skills ficam em `.agents/skills` e os agentes em `.codex/agents`.
No Claude Code, as skills automáticas ficam em `.claude/skills`, os agentes em
`.claude/agents` e as skills de invocação explícita viram comandos de referência,
como `/bezalel-release`, em `.claude/commands`. Esses comandos carregam o original;
não reescrevem o `SKILL.md`. ENV, VPS e limpar-orbstack também preservam sua política
explícita existente, além das cinco skills manuais fora do fluxo.

### Grok Build e modelos GLM

A integração direta aceita `--platform grok` e o iniciador aceita `--app grok`.
O alvo é o **Grok Build oficial da xAI** (`grok`), não CLIs comunitários com nomes
parecidos nem o chat web. Segundo a [documentação oficial de compatibilidade](https://docs.x.ai/build/features/skills-plugins-marketplaces),
o Grok Build descobre agentes, skills, comandos e instruções Claude Code.
Reutilizamos os nove adaptadores do catálogo em `.claude/agents` e as skills/comandos
em `.claude`, sem manter cópias duplicadas em `.grok`. `both` continua significando
Codex e Claude; instalações Claude existentes também podem ser descobertas pelo Grok.

Com Grok Build previamente instalado, use na base publicada:

```sh
python3 -B .bezalel/base/scripts/project.py enable --project . --platform grok --no-auto-update
python3 -B .bezalel/base/scripts/project.py run --project . --app grok
```

O iniciador atualiza a base antes de abrir o aplicativo; `--no-auto-update` evita
preparar hooks de sessão. Se habilitados sem essa opção, os hooks usam a camada
compatível Claude e dependem de confiança e validação no aplicativo; a instalação
não concede confiança. `update`, `status` e `disable` usam o mesmo registro de
integridade e preservam customizações. Ao trocar `--platform` em uma instalação
gerenciada, o conjunto selecionado substitui o anterior; arquivos personalizados
bloqueiam a reconciliação. Não habilite duas modalidades de distribuição no projeto.

O suporte foi preparado com testes sintéticos de instalação, atualização e remoção.
Isso não comprova descoberta ou execução no Grok: confira `grok inspect` e `/agents`
na versão instalada e faça um piloto antes de depender da equipe. Não há pacote
nativo, atualização de marketplace ou `plugin.py --client grok` nesta integração.
Nenhum CLI, credencial, modelo, endpoint ou permissão é configurado pelo Bezalel.

Para **GLM da Z.ai**, o caminho documentado aqui é **Claude Code com GLM**,
conforme a [integração oficial da Z.ai](https://docs.z.ai/devpack/tool/claude).
GLM é o provedor/modelo dessa sessão, não um novo formato de agente ou um comando
`glm`. Configure o provedor no aplicativo seguindo a documentação da Z.ai, fora do
Bezalel, e confira o modelo efetivo antes de iniciar. Não coloque chaves em arquivos
versionados, comandos compartilhados ou conversas.

```sh
python3 -B .bezalel/base/scripts/project.py enable --project . --platform claude
python3 -B .bezalel/base/scripts/project.py run --project . --app claude
```

Os nove adaptadores continuam sem modelo fixo. A política proporcional usa os
modelos realmente disponíveis: nomes de categorias do Claude não comprovam modelos
GLM distintos ou menores, pois o provedor pode mapear várias categorias ao mesmo
modelo. Confira a execução dos subagentes e registre limitações, sem simular QA ou
AppSec independentes. Instalação em fixtures e validação do manifesto Claude não
comprovam autenticação, seleção de modelo ou funcionamento com a API da Z.ai.
OpenCode com GLM é outra integração e não está implementada nesta versão.

### Atualizar e iniciar uma sessão

**Instalações anteriores ao catálogo local e ao novo encerramento:** o validador
antigo espera o contrato anterior e recusa essa atualização. Use o atualizador de uma cópia nova
do Bezalel uma vez, sem trocar manualmente a base instalada:

```sh
git clone --branch master --single-branch https://github.com/rjsandim/bezalel.git /caminho/bezalel-atualizador
python3 -B /caminho/bezalel-atualizador/scripts/project.py update --project /caminho/do/projeto
```

Escolha uma pasta nova para o clone, fora da base do projeto. Esse comando mantém
as verificações de customizações, valida a nova árvore e atualiza o registro e as
referências juntos. O catálogo passa a usar `workflow` e IDs locais; os arquivos antigos gerenciados
são removidos somente se não houver customizações. O registro opcional de entrega
usa formato 3, com HTML temporário e encerramento pós-merge; configurações de
projeto continuam no formato 2. Não converta aprovações antigas inventando provas. Depois dessa
migração, use os comandos abaixo normalmente.
Plugins nativos recebem os arquivos renomeados pela atualização do plugin.

**Processos em arquivos próprios:** a versão que separou os processos em
`agents/processes/` mantém em `agents/dream-team.md` o índice que o checker anterior
confere; por isso a atualização normal funciona sem passo manual. Ela reescreve os
adaptadores gerenciados e o bloco de instruções, salvo customização ou colisão, que
interrompe a atualização como nos demais casos. Os links antigos
`dream-team.md#process-<referência>` continuam resolvendo pelas âncoras do índice.

Para receber a versão publicada **antes** de abrir o aplicativo:

```sh
python3 -B .bezalel/base/scripts/project.py run --project . --app codex
# Ou use --app claude.
```

Para atualizar separadamente ou consultar a instalação:

```sh
python3 -B .bezalel/base/scripts/project.py update --project .
python3 -B .bezalel/base/scripts/project.py status --project .
```

A atualização busca `master` do `origin` da base, aceita apenas avanço de histórico,
valida a árvore com o checker já adotado e reconcilia skills novas/removidas,
adaptadores e instruções. A revisão efetiva fica em `.bezalel/install.local.json`.
Não usa reset, força, limpeza de estado ou execução de scripts recém-baixados para
validá-los. Base modificada, conflito de arquivo ou falha de rede deixam um erro
visível e preservam a revisão anterior. Uma skill removida sai da descoberta;
nenhum recurso Docker, volume ou ambiente é removido.

O hook `SessionStart` em `.codex/hooks.json` / `.claude/settings.local.json`
também consulta atualizações em sessões novas. Como o aplicativo pode já ter
carregado agentes quando o hook roda, uma atualização pede reabertura da sessão;
o comando `run` evita essa defasagem. No Codex, o usuário precisa revisar/confiar
no hook pelo mecanismo do aplicativo. Instalar arquivos não contorna essa confiança.

A base fica só no checkout principal (`.bezalel/base` é ignorada no Git). Em uma
worktree, links de skills apontariam para uma base inexistente; por isso o hook
localiza o checkout principal, atualiza aquela base e cria `.bezalel/base` na
worktree como link para ela. Sem hook, ligue a worktree uma vez a partir da base
do checkout principal:

```sh
python3 -B /caminho/do/projeto/.bezalel/base/scripts/project.py link-worktree --project .
```

O link exige a regra `/base` em `.bezalel/.gitignore` (`/base/` não ignora links);
`enable` a acrescenta em instalações novas ou repetidas. Uma pasta `.bezalel/base`
própria na worktree não é substituída. Sem base no checkout principal, o hook não
faz nada.

Para fixar a versão e desligar a consulta automática, repita `enable` com
`--no-auto-update`; o comando `update` continua disponível quando solicitado.
`--branch` seleciona outra branch publicada. Para desligar a integração:

```sh
python3 -B .bezalel/base/scripts/project.py disable --project .
```

São removidos apenas links, agentes, hooks e blocos ainda iguais aos gerenciados.
A base, o contexto próprio e as demais instruções permanecem. Customização detectada
interrompe a operação para reconciliação, sem apagar o trabalho do projeto.
Arquivo gerenciado ausente, por exemplo após trocar para uma branch anterior à
instalação, não é customização: `update`/`enable` o recriam e `disable` apenas o
retira do registro. Um hook Bezalel sem registro ou alterado bloqueia a operação.

### Instalar como plugin nativo

A publicação na `master` aciona o
[workflow de distribuição](.github/workflows/publish-plugin.yml). Após validação,
ele gera a branch **`bezalel-plugins`**, com manifestos e marketplaces dos dois
aplicativos. Não edite essa branch: a fonte continua na `master`. O pacote recebe
uma versão derivada do conteúdo; uma skill nova ou mudança de workflow gera outra
versão sem editar listas de instalação manualmente.

Depois da primeira execução bem-sucedida desse workflow:

```sh
# Codex: cadastro e instalação nativos (o CLI mantém o cache/configuração do usuário).
codex plugin marketplace add rjsandim/bezalel --ref bezalel-plugins
codex plugin add bezalel@bezalel

# Claude Code: cadastro e instalação com escopo do projeto.
claude plugin marketplace add https://github.com/rjsandim/bezalel.git#bezalel-plugins --scope project
claude plugin install bezalel@bezalel --scope project
```

No diretório do projeto, use o **caminho do plugin realmente instalado**, mostrado
pelo aplicativo, para conectar o contexto e disponibilizar os agentes do Codex:

```sh
python3 -B "/caminho/do/plugin/scripts/plugin.py" enable --project . --client both
```

Escolha `--client codex` ou `--client claude` quando apropriado. A conexão registra
`.bezalel/plugin.local.json`, referencia a base carregada e preserva o contexto
próprio. No pacote gerado, contratos ficam em `contracts/`; somente os nove
adaptadores são declarados como agentes Claude. O Codex usa TOMLs no projeto,
pois a presença de agentes dentro de um plugin não é tratada como descoberta
nativa garantida. Ambos referenciam os mesmos contratos e skills.

Depois da conexão, o hook usa apenas os comandos nativos de atualização do
marketplace/plugin `bezalel`, sem mexer nos demais plugins. O aplicativo carrega a
nova versão na próxima sessão; então o hook reconcilia os contratos e TOMLs do
projeto. O cache nativo não é uma pasta de customização: altere a fonte no Bezalel.
Use `--no-auto-update` no `enable` para desativar a consulta. O mecanismo nativo do
Claude também possui uma opção de auto-update; deixe-a desligada ao usar este hook,
para evitar dois atualizadores concorrentes.

Se uma skill gravou `state/` ou `backups/` no cache, o hook recusa a atualização até
preservação/migração desse estado. Para ENV, use a integração direta, com caminho
estável: caches de plugins podem ser removidos pelo aplicativo. Essa limitação não
é autorização para limpar ambientes. Não alteramos o contrato de estado da ENV.

Para desligar a conexão, execute `plugin.py disable --project .` da base instalada.
Para retirar também suas skills do aplicativo, desabilite o plugin no próprio
aplicativo. A integração direta e a nativa não devem ficar ativas juntas no projeto.

Para preparar um pacote local revisável sem instalar ou publicar:

```sh
python3 -B scripts/plugin.py build --output .local-review/bezalel-plugin
claude plugin validate --strict .local-review/bezalel-plugin/.claude-plugin/plugin.json
claude plugin validate --strict .local-review/bezalel-plugin/.claude-plugin/marketplace.json
```

O destino precisa ser novo. O gerador preserva as 18 pastas de skills, inclui
adaptadores/manuais, não inclui estado operacional e não instala o resultado.

### Atualizar as importações do Akita

O [workflow de sincronização](.github/workflows/sync-akita.yml) consulta a origem
diariamente às 11:00 UTC (08:00 de Brasília) ou por disparo manual. Ele abre uma
**PR**, conforme a política escolhida, e não faz merge. Depois da sua revisão e
integração/publicação na `master`, a distribuição atualiza o canal de plugins e os
projetos podem receber a versão.

A seleção contém as **nove importações preservadas**. `pr-audit` e `iss-audit`
nunca são atualizadas por esse caminho. A origem registra revisão, arquivos/modos
e os overlays de metadados permitidos. Qualquer mudança local, remoção ou arquivo
adicional protege a skill inteira; as outras elegíveis podem gerar a proposta.
Links e submódulos no upstream ou remoção de uma skill selecionada causam erro.
Novas skills do Akita não são incorporadas automaticamente sem seleção humana.

O verificador não executa procedimentos ou scripts baixados. Mantém os metadados
locais de invocação manual e a exceção de modo já existente de security-audit.
Conteúdo de código/instruções novo precisa da sua revisão semântica na PR, mesmo
com os testes estruturais verdes. O inventário histórico registra a seleção inicial;
a revisão atual por skill fica no [registro de origem](.bezalel/upstream.json).

Para inspecionar ou preparar a proposta local:

```sh
python3 -B scripts/sync_upstream.py
python3 -B scripts/sync_upstream.py --apply
```

Sem `--apply`, só informa o resultado. `--upstream /caminho/do/clone --revision SHA`
permite verificar uma cópia local sem fetch. `--apply` grava arquivos/registro locais,
sem commit, push ou PR. O workflow precisa de Actions habilitado, escrita de conteúdo
e permissão para criar PRs; proteções da organização/branch continuam valendo.
PRs criadas com `GITHUB_TOKEN` não disparam `pull_request`; por isso o workflow
aciona a [validação](.github/workflows/validate.yml) na branch da proposta.
Uma falha de autenticação, permissão ou publicação é falha, não atualização concluída.
As operações Git dos scripts de distribuição desativam a manutenção automática
somente durante cada comando, evitando gravações posteriores em diretórios
temporários; a configuração persistente do Git é preservada.

### Suporte e validação

Foram implementados os formatos documentados de
[skills Codex](https://learn.chatgpt.com/docs/build-skills),
[agentes Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[hooks Codex](https://learn.chatgpt.com/docs/hooks),
[plugins OpenAI](https://developers.openai.com/plugins/build/plugins),
[agentes Claude](https://code.claude.com/docs/en/sub-agents) e
[plugins Claude](https://code.claude.com/docs/en/plugins-reference).
Os testes locais usam projetos e remotos Git sintéticos. A validação nativa de
manifestos foi feita com Claude Code 2.1.245; os comandos do Codex foram conferidos
no CLI 0.163.0. Isso não certifica descoberta/execução no aplicativo nem aprovação
dos hooks. Reabra a sessão, confira os nove agentes e faça o piloto no projeto.
A adoção em um projeto consumidor e a confiança nos hooks são etapas próprias;
os testes locais não instalam plugins globalmente nem ativam infraestrutura.

### Uso operacional das skills

Para executar scripts, defina `SKILL_DIR` como o caminho absoluto da pasta carregada,
por exemplo `<projeto>/.bezalel/base/skills/env`. Para comandos da ENV, entre no
repositório **alvo**, com ao menos um commit. Os comandos abaixo são uso posterior,
quando solicitado, e não etapas de instalação:

```sh
bash "$SKILL_DIR/scripts/detect.sh"
# Revise .envstack/stack.yaml antes de continuar.
bash "$SKILL_DIR/scripts/init.sh"
ENV_DRY_RUN=1 bash "$SKILL_DIR/scripts/new.sh" corrigir-login
```

Detect/init geram arquivos locais. O dry run também cria worktree e resolve
arquivos de ambiente; não é uma operação somente leitura. Esses comandos não
constituem autorização para criar infraestrutura ou descartar dados.

## Configuração

### ENV

MySQL e PostgreSQL podem usar pools locais compartilhados com database e usuário
por ambiente/serviço. Redis 7 também pode compartilhar o servidor, com pares de
bancos lógicos e usuários restritos por serviço. Os modos são opcionais e ambientes
existentes exigem migração explícita. Veja [configuração e limites](skills/env/references/bancos-compartilhados.md).

O manifesto por projeto continua em `.envstack/stack.yaml`; não foi migrado para
`.bezalel` porque cumpre um contrato existente de geração de ambientes.

- `base_ref`: referência local usada para criar branches. Sem ela, usa-se o
  `origin/HEAD` já disponível, ou a única branch existente entre `main` e `master`.
  Ambiguidade ou ausência falha; nenhum fetch é feito automaticamente.
- `engine`: `orbstack`, `docker-desktop` ou `auto`. Para `auto`, `docker_context`
  é obrigatório. O contexto configurado precisa existir; não há fallback.
- Estado em `state/` na instalação da skill registra projeto e contexto. Copiar
  a skill não migra estados antigos. Registros sem esses vínculos precisam de
  auditoria manual; o programa não adota ambientes por semelhança de nomes.

Operações que podem iniciar/reconfigurar proxy, DNS ou certificados exigem
`ENV_ALLOW_SHARED_INFRA=1` apenas na execução explicitamente autorizada. Não
configure essa variável permanentemente. `destroy` exige
`--confirm <projeto>/<ambiente>`, recusa volumes compartilhados e não usa força.
`--keep-worktree` mantém branch/arquivos, **mas permite remover os volumes do
ambiente confirmado**. Dados devem ser preservados antes. Imagens não são
removidas pelo destroy. Consulte o [guia](skills/env/references/operacao.md).

### VPS Deploy

Copie [o modelo da própria skill](skills/vps-deploy/templates/vps-deploy.example.json)
para `<projeto>/.bezalel/vps-deploy.local.json`, somente se ainda não existir.
Incorpore a regra de [ignore](skills/vps-deploy/templates/project.gitignore) ao
`.bezalel/.gitignore` daquele projeto, preservando regras existentes, antes de
preencher valores locais. A pasta da skill pode ser copiada sem a raiz do Bezalel.

O usuário configura localmente a URL e, se necessário, o alvo SSH. O token é
referenciado somente por `COOLIFY_API_TOKEN`, fornecido ao processo pelo próprio
usuário/gerenciador de segredos. Não envie valores pelo chat, não os coloque no
JSON nem reutilize uma credencial em outro projeto sem conferir a associação.
Nenhum arquivo local real ou credencial acompanha este repositório.

```sh
python3 "$SKILL_DIR/scripts/check_config.py" --project "/caminho/do/projeto"
```

A validação não conecta, autentica ou confirma permissões. Veja
[configuração](skills/vps-deploy/references/configuracao.md).

### Limpar OrbStack

É um roteiro operacional, sem comando automático de limpeza. Exige projeto e
ambiente/critério delimitado, contexto `orbstack` validado, prova de integração,
preservação de dados e propriedade exclusiva dos recursos. Não faz prune global,
não reinicia OrbStack e não remove infraestrutura compartilhada. Um pedido de
instalar, copiar ou editar a skill não autoriza executá-la.

### Implementar snapshots

Use [a skill](skills/implementar-snapshots/SKILL.md) para construir a funcionalidade
na linguagem e no framework do projeto alvo, com política própria de dados,
relações e destinos. Ela inclui um [modelo de política independente de stack](skills/implementar-snapshots/templates/snapshot-policy.example.json),
[fixture relacional sintética](skills/implementar-snapshots/templates/tiny-relations.json)
e [cenários de validação](skills/implementar-snapshots/references/testes.md).
Laravel aparece apenas em um [exemplo opcional](skills/implementar-snapshots/references/exemplo-laravel.md).

A referência veio da leitura dos comandos full/tiny de uma aplicação real;
[origem e diferenças](skills/implementar-snapshots/references/origem.md) separam o
comportamento observado das melhorias propostas. A skill não contém um motor de
backup nem executa snapshots ao ser instalada. Implementação não autoriza ler
produção, sobrescrever destinos, habilitar agenda ou alterar infraestrutura ENV.

### Roteiro manual em Excel

Use [development-test-workbook](skills/development-test-workbook/SKILL.md) quando o
roteiro pedido for Excel. A pasta é portátil e contém o template vazio, contrato
JSON e gerador Python; requer `openpyxl` 3.1.x já disponível. Não depende do loader
Codex, não consulta banco nem executa os casos. Fórmulas exigem recálculo em um
aplicativo de planilhas. O gerador recusa sobrescrever arquivos existentes.

O campo `manual_test.path` da entrega aponta para o roteiro local, conforme o
[contrato](agents/record-contract.md). Excel é obrigatório em melhoria/feature;
no bug, o formato depende da necessidade. A skill produz o artefato; QA, revisão
e decisão humana continuam no fluxo.

## Verificação local segura

Requisitos: Python 3.11+ e Bash; para os testes de ciclo de vida da ENV, Git,
`yq` de Mike Farah v4, `jq`, `envsubst` e Docker CLI com Compose. Para operação
real, a ENV é orientada a macOS/Homebrew e Compose com `--wait --wait-timeout`.
Nenhuma dependência é instalada automaticamente pelos testes.

Execute a partir da raiz do Bezalel:

```sh
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s skills/env/tests -v
python3 -B -m unittest discover -s skills/vps-deploy/tests -v
# Requer openpyxl 3.1.x; não instala dependências:
python3 -B -m unittest discover -s skills/development-test-workbook/tests -v
```

O checker verifica estrutura, catálogo de papéis, configuração de exemplo, links
locais, metadados essenciais e integridade/abas/vínculos do template Excel, sem
alterar arquivos ou exigir atualização de hashes a cada edição. Os testes de entrega
usam registros e decisões inteiramente sintéticos, sem autorização real.
Eles cobrem falha/retomada nos três cenários, provas desatualizadas, separação de
revisores, UI/banco, risco, aceite e PRs. Contratos, catálogo e TOMLs são conferidos
contra os processos/skills da fonte canônica; não se certifica o loader.
Os testes usam repositórios temporários e simulam operações Docker, brew, sudo
e mkcert; o CLI real só valida Compose estaticamente, sem acessar o daemon.
Os testes Python de VPS usam entradas sintéticas, sem rede. As skills documentais
não precisam de uma suíte de runtime artificial. Os cenários de limpeza estão
em [validação](skills/limpar-orbstack/references/validacao.md).

A [validação no GitHub Actions](.github/workflows/validate.yml) executa as mesmas
suítes em PRs e na `master`: checker e `tests/`, VPS, workbook (openpyxl fixado por
hash em ambiente virtual, [lista](.github/requirements-workbook.txt)) e ENV. O job
da ENV confere `git`, `jq`, `yq`, `envsubst` e `docker` já presentes no runner, sem
instalá-los, roda `bash -n` nos scripts e a suíte. Como o contexto Docker dos
fixtures só existe no simulador, o `compose config` real roda sem esse contexto,
apontado para um socket inexistente: o Compose v2 do Linux recusa contexto ausente.

`skills/env/tests/integration_lifecycle.py` é separado: usa containers reais,
imagens e um módulo Playwright fornecidos pelo operador. Não execute como teste
padrão. Exige autorização e infraestrutura descartável próprias.

## Limitações e preservação

Não foi validada operação real de DNS, certificados, proxy, deploy, autenticação
ou limpeza nesta padronização. Não há transação entre Git e Docker: uma falha
pode deixar etapas parcialmente concluídas. O estado é preservado para diagnóstico;
não repita a ação ampliando força ou alcance. Mudanças concorrentes ainda exigem
revalidação humana. Outras plataformas não estão certificadas.

A proveniência detalhada da migração e seus hashes estão preservados no histórico
Git, até o commit `cf94dec22f628a26d337fe22076fabffe973eed6`. Esses registros não
fazem parte da manutenção diária; mudanças atuais são acompanhadas pelo Git.
A antiga variante Claude de ENV é recuperável no commit
`75e65c4be946a3ae8d6ea003db0bcc6000e3ecde`.
Arquivos locais, estado de execução, backups e rascunhos não integram o Git.
Referências bibliográficas foram mantidas; nenhuma nova licença foi atribuída.

Para contribuir, siga [AGENTS.md](AGENTS.md). A única publicação automática é a
da branch `bezalel-plugins` após integração na `master`; merge e deploy são manuais.
