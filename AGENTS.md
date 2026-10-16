# Instruções de contribuição do Bezalel

Este arquivo instrui contribuições no repositório. Papéis e contratos ficam em
`agents/`; são definições, não um runtime de delegação ou autorização.

## Escopo e estrutura

- Trabalhe nesta árvore; não edite as instalações originais fora do Bezalel.
- Cada pasta em `skills/` contém `SKILL.md` com `name`, `description` e, nesta
  ordem: Objetivo e escopo; Entradas e pré-requisitos; Procedimento; Saídas;
  Validação; Limites operacionais. Use português nas instruções e interfaces.
- Exceção: `skills/security-audit/` preserva os arquivos originais de
  `akitaonrails/my-skills`, inclusive idioma e estrutura, para facilitar
  atualizações. Registre a revisão de origem no README; não adapte seu conteúdo.
  Metadados essenciais e links locais continuam sujeitos à validação.
- Referências extensas ficam em `references/`; scripts, templates e testes são
  opcionais conforme a função. Não crie pastas vazias ou runtimes artificiais.
- Caminhos executáveis devem partir da pasta da skill carregada. Não introduza
  caminhos fixos de usuário/agente ou dependências ocultas da raiz do Bezalel.
- Metadados `agents/openai.yaml` são adaptadores opcionais. Não prometa suporte
  de um aplicativo sem validá-lo. Invocação implícita não autoriza efeitos externos.

## Papéis e contratos de entrega

- Agente define papel/processo; `.bezalel/project.json` aponta instruções de
  arquitetura/negócio do projeto; skills definem procedimentos. Não misture as três
  responsabilidades nem crie gerenciador de pacotes ou runtime implícito.
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
- Preserve os nove papéis do catálogo e o APROVADOR HUMANO externo, que não é
  agente. IDs são estáveis; `display_name` define a nomenclatura. Confiabilidade é
  responsabilidade do Engenheiro DevOps; negócio, do Analista de Produto.
- Responsabilidades de observação permanecem desativadas e somente propositivas. Não ative coleta,
  leia produção ou faça correções como teste dessa base. Calendário, janela e
  tolerância importam para métricas; ausência de dados não é zero eventos.
- PR é etapa prevista de entrega, mas publicação/merge/deploy exigem autorização
  concreta da tarefa. Quando ausente, prepare rascunho local e registre a pendência.

- Em mudanças que afetem o Company Flow, use a [correspondência](agents/company-flow.md):
  arquivos são a fonte canônica; releia a revisão visual, preserve alterações
  concorrentes e confira etapas/decisões/condições nos dois sentidos. Diferencie
  checker estrutural de revisão semântica e registre divergências preexistentes.

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
