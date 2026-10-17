# Instruções de contribuição do Bezalel

Este arquivo instrui contribuições no repositório. Papéis e contratos ficam em
`agents/`; são contratos e adaptadores de agentes, sem runtime próprio de autorização.

Bezalel é o fluxo de desenvolvimento; DreamTeam é a equipe de agentes; Company
Flow é a ferramenta visual. Use esses nomes nas instruções e apresentações.
Preserve caminhos e IDs técnicos existentes para manter compatibilidade com as
instalações e a correspondência com a ferramenta.

## Escopo e estrutura

- Trabalhe nesta árvore; não edite as instalações originais fora do fluxo Bezalel.
- Cada pasta em `skills/` contém `SKILL.md` com `name`, `description` e, nesta
  ordem: Objetivo e escopo; Entradas e pré-requisitos; Procedimento; Saídas;
  Validação; Limites operacionais. Use português nas instruções e interfaces.
- Exceções: `skills/security-audit/`, `skills/humanizer/`,
  `skills/verification-planning/`, `skills/agent-browser/`, `skills/release/`,
  `skills/reflect/`, `skills/github-resolution/`, `skills/pr-bump/` e
  `skills/pr-post-audit/` preservam os arquivos originais de
  `akitaonrails/my-skills`, inclusive idioma e estrutura, para facilitar
  atualizações. A seleção inicial fica no README/inventário; a revisão vigente por
  skill fica em `.bezalel/upstream.json`. Não adapte seu conteúdo.
  Metadados essenciais, inclusive descrição YAML em bloco, e links locais
  continuam sujeitos à validação. A seleção no fluxo Bezalel não autoriza
  adaptar essas cópias nem executar ações fora do escopo de cada responsável.
  Somente os adaptadores de invocação das cinco skills manuais podem acrescentar
  `allow_implicit_invocation: false`, conforme solicitado; o conteúdo original
  permanece intacto. `pr-audit` e `iss-audit` são variantes cuja adaptação foi
  autorizada, seguem o formato comum e registram origem/motivos em suas referências.
- `release`, `reflect`, `github-resolution`, `pr-bump` e `pr-post-audit` ficam
  fora do fluxo Bezalel e são para chamada manual explícita. Relatório de auditoria
  não é aprovação humana; procedimentos importados não ampliam autorização nem
  substituem regras do projeto. Confira stack, versão final e comandos reais antes
  de usar exemplos da origem. Limpeza não pode usar força nem atingir recursos
  preexistentes por prefixo. Não publicar código com verificações obrigatórias
  falhas para depois corrigi-lo; qualquer alteração material invalida provas afetadas.
- Referências extensas ficam em `references/`; scripts, templates e testes são
  opcionais conforme a função. Não crie pastas vazias ou runtimes artificiais.
- Caminhos executáveis devem partir da pasta da skill carregada. Não introduza
  caminhos fixos de usuário/agente ou dependências ocultas da raiz do Bezalel.
- Metadados `agents/openai.yaml` são adaptadores opcionais. Não prometa suporte
  de um aplicativo sem validá-lo. Invocação implícita não autoriza efeitos externos.

## Papéis e contratos de entrega

- Agente define papel/processo; `.bezalel/project.json` aponta instruções de
  arquitetura/negócio do projeto; skills definem procedimentos. Não misture as três
  responsabilidades. A instalação e distribuição autorizadas disponibilizam
  arquivos; não criam runtime de execução ou autorização do fluxo Bezalel.
- Papéis em `agents/roles/` constam do catálogo e descrevem objetivo, entradas,
  saídas, ferramentas, limites, pronto, seleção de skills e handoff. Não alegue
  que um Markdown delega, executa ferramentas ou impõe gates.
- User story deve ser curta e compreensível, com necessidade, critérios observáveis,
  dependências e responsável pela integração inteira. Especialistas são opcionais.
- Gates exigem evidência de isolamento de arquivos/banco/filas/portas/storage;
  mudança estrutural de banco exige proposta revisável e aprovação humana anterior
  à implementação, vinculada à versão exata. Sem mudança, registre não aplicável.
- Não fabrique aprovações ou resultados para satisfazer validadores. JSON não prova
  identidade nem autorização; um runtime deve conferir a interação humana real.
- QA independente amplia cenários e confronta comportamento, não só a suíte do dev.
  Mantenha responsabilidade pela integração de API/web/mobile e serviços envolvidos.
- Product Manager aponta desvios e alternativas; o usuário decide mudanças. Contratos,
  fachadas e reutilização devem resolver problemas concretos, sem refatorar fora
  do escopo ou concentrar regras/SQLs de todos os módulos num arquivo gigante.
- Preserve os nove agentes ativos da v2 e o APROVADOR HUMANO externo: PM, TL,
  DevOps, quatro devs, QA e AppSec. IDs são estáveis; `display_name` define a
  nomenclatura. Processos e skills atribuídos devem corresponder à fonte canônica.
- Observação de produção/negócio está fora deste pacote. Não ative coleta, leia
  produção ou faça correções como teste da base. Ausência de dados não é zero eventos.
- PR é etapa prevista de entrega, mas publicação/merge/deploy exigem autorização
  concreta da tarefa. Quando ausente, prepare rascunho local e registre a pendência.

- Em mudanças que afetem o fluxo Bezalel, use a [fonte canônica](agents/company-flow-v2.md):
  arquivos são a fonte canônica; releia a revisão visual, preserve alterações
  concorrentes e confira etapas/decisões/condições nos dois sentidos. Diferencie
  checker estrutural de revisão semântica e registre divergências preexistentes.

## Manutenção das instruções e da adoção

- Ao alterar estrutura, instalação, comandos, configuração, responsabilidades,
  processo ou seleção de skills, confira e atualize o README e este `AGENTS.md`
  na mesma tarefa, conforme o impacto. Não é necessário reescrever instruções
  que continuam válidas; não deixe mudança de comportamento sem documentação.
- Use `AGENTS.md` como instrução curta de contribuição, README como guia de adoção,
  [Bezalel v2](agents/company-flow-v2.md) como processo vigente e a
  [relação por etapa](agents/company-flow-v2-skills.md) para selecionar skills.
  Referencie essas fontes; não copie seus procedimentos completos aqui.
- Contratos, catálogo, templates, adaptadores e validadores seguem a v2. Atualize
  o conjunto quando uma responsabilidade mudar; não reintroduza percursos antigos,
  observadores ou instruções duplicadas. Piloto real e descoberta no aplicativo
  são verificações próprias; testes locais não certificam execução de agentes.
- `agents/codex/` e `agents/claude/` contêm nove adaptadores por plataforma, com
  referências aos contratos, sem modelo fixo, credenciais ou override de permissões.
  Não crie um adaptador humano. Catálogo e checker devem conferir os dois formatos.
- A integração direta (`scripts/project.py`) gerencia somente seus links,
  adaptadores, hooks e blocos de instrução por projeto. Preserve conteúdo próprio,
  contexto e estado operacional. Customizações e colisões interrompem a atualização;
  não as adote silenciosamente. Use clone estável para ENV e não siga links externos.
  Operações Git da distribuição não devem iniciar manutenção automática que possa
  continuar escrevendo após o retorno; aplique a restrição por comando, sem alterar
  a configuração persistente do usuário ou do projeto.
- `scripts/plugin.py` gera o pacote nativo: contratos em `contracts/`, adaptadores
  Claude explicitamente listados e TOMLs Codex conectados ao projeto. Não coloque
  contratos/humano numa pasta descoberta como agentes. Skills originais permanecem
  idênticas; comandos Claude de invocação manual só referenciam seus originais.
- Os workflows consultam o Akita e **abrem PR para revisão humana**; somente a
  publicação na `master` distribui o pacote para `bezalel-plugins`. Nunca integre
  automaticamente a PR do Akita. `pr-audit`/`iss-audit` ficam excluídas; mudança
  local protege a skill inteira. Não execute scripts do upstream para validá-lo.
- Os registros de integridade em `.bezalel/upstream.json` e no projeto consumidor
  existem para detectar alterações antes de atualizar, limitados a arquivos
  gerenciados. Não regenere hashes de toda a árvore a cada contribuição.
- O registro v2 é um snapshot opcional da issue. Não exija Markdown paralelo por
  demanda nem preencha decisões/resultados para satisfazer o checker. Migração
  de v1 é explícita, com provas reais; comandos declarados nunca são executados
  pelo validador. Arquivos removidos não podem permanecer referenciados nos guias.
- Em projetos consumidores, preserve o `AGENTS.md` e as configurações existentes;
  incorpore referências à versão adotada. Não substitua suas instruções pelo
  arquivo de contribuição do Bezalel. Instalação não ativa agentes ou infraestrutura.
- Na entrega, informe quais instruções foram atualizadas e as limitações verificadas.
  Diferencie automação preparada, instalada e executada. Hooks precisam da confiança
  do aplicativo; não a conceda via edição de configuração. A distribuição de arquivos
  não sincroniza o MCP. Mudanças do fluxo seguem a conferência nos dois sentidos.

## Configuração e segurança

- Segredos nunca entram em Git, exemplos, relatórios, chat ou saída de comandos.
  VPS usa `.bezalel/vps-deploy.local.json` por projeto, ignorado, e referência a
  `COOLIFY_API_TOKEN` no ambiente. Não leia/preencha credenciais reais para testar.
- ENV usa `.envstack/stack.yaml`, contexto Docker explícito e base local verificável.
  Não acrescente fallback para contexto ativo, remoção por prefixo ou força.
- Não altere DNS, CA, proxy, containers, volumes, imagens, cofres ou credenciais
  para validar mudanças. Não rode limpeza real, deploy ou integração real sem
  autorização específica. Use fixtures, temporários e mocks de comandos mutáveis.
- Preserve arquivos e configurações preexistentes. Falhas devem resultar em erro
  e estado diagnóstico; nunca as oculte para mostrar sucesso. Relate parcialidade.
- Não faça push, publicação, merge remoto ou exclusão remota por inferência.

## Validação proporcional

- Para toda mudança, execute `python3 -B scripts/check_repository.py` e confira
  `git diff --check`. O checker é somente leitura e valida estrutura, metadados
  essenciais e links locais; não exige regenerar inventários ou hashes.
- Mudanças em agentes/contratos/checkers: `python3 -B -m unittest discover -s tests -v`.
  Use fixtures sintéticas; não execute comandos declarados na configuração para
  testar sua leitura.
- Mudanças em instalação/atualização/plugins usam a mesma suíte em `tests/`, com
  remotos e projetos temporários. Teste falha, customizações e entrada de skill nova.
  Gere o pacote em destino novo e valide manifestos no Claude quando disponível;
  não instale plugins globalmente nem ligue projetos reais para testar o instalador.
  Workflows preparados não são execuções remotas comprovadas.
- Mudanças em ENV: `python3 -B -m unittest discover -s skills/env/tests -v` e
  `bash -n` nos scripts shell alterados. Os testes usam Docker simulado; o CLI
  real só pode ser usado por eles para `compose config`, sem daemon.
- Mudanças em VPS: `python3 -B -m unittest discover -s skills/vps-deploy/tests -v`.
- Mudanças documentais: confira links e comandos descritos; não execute comandos
  destrutivos apenas porque aparecem nos exemplos. Para limpar-orbstack, revise
  também seus cenários em `references/validacao.md` e o contrato atual de ENV.
- Não rode `integration_lifecycle.py` como parte da suíte padrão. Não instale
  ferramentas por conta própria para contornar pré-requisitos ausentes; reporte-os.
- Antes do commit, revise arquivos rastreados, diferenças, credenciais e alvos
  internos; adicione somente arquivos da tarefa. Não enfraqueça testes para obter verde.

## Histórico e entrega

Registre adições e motivos nos commits, sem valores privados. Os registros
da migração inicial permanecem no histórico Git; não crie um inventário mutável
ou checksums de toda a árvore para cada edição cotidiana.
Informe o que mudou, testes executados, limites, commit e eventual bloqueio.
Não descreva presença de token como autenticação ou testes locais como deploy.
