# Bezalel

Coleção de cinco skills pessoais: instruções, referências e automações locais.
Não há runtime de agentes, serviço hospedado ou instalador automático.

| Skill | Finalidade | Implementação |
|---|---|---|
| [clean-code](skills/clean-code/SKILL.md) | Revisar e corrigir código dentro do escopo | Markdown e referências |
| [clean-architecture](skills/clean-architecture/SKILL.md) | Revisar responsabilidades e dependências | Markdown e referências |
| [env](skills/env/SKILL.md) | Gerenciar ambientes locais por worktree e Docker | Bash, Python auxiliar e templates |
| [vps-deploy](skills/vps-deploy/SKILL.md) | Orientar operações de VPS com configuração por projeto | Markdown e validador Python |
| [limpar-orbstack](skills/limpar-orbstack/SKILL.md) | Auditar e limpar ambientes explicitamente autorizados | Markdown e roteiros de preservação |

## Estrutura comum

Cada `SKILL.md` declara `name` e `description` e contém objetivo/escopo,
entradas/pré-requisitos, procedimento, saídas, validação e limites operacionais.
`references/`, `scripts/`, `templates/` e `tests/` aparecem quando necessários.
`agents/openai.yaml` é um adaptador opcional de interface, não um agente em
execução. As skills operacionais usam invocação explícita nesse metadado; as duas
Clean podem ser usadas implicitamente em tarefas compatíveis. A interpretação
pelo aplicativo deve ser conferida nele; este repositório não certifica loaders.

## Instalação e uso

Leia a skill e copie sua pasta **inteira** para o diretório de skills que a sua
ferramenta suporta. Não sobrescreva uma instalação divergente: faça backup ou
compare antes. A cópia não ativa nem executa nada por si só. Também é possível
ler os arquivos e chamar os scripts diretamente desta árvore.

Nos exemplos, defina `SKILL_DIR` como o caminho absoluto da pasta efetivamente
copiada, por exemplo `<Bezalel>/skills/env`. Isso evita executar uma instalação
antiga em outro diretório. Configure a descoberta/invocação na ferramenta usada.
Os arquivos originais fora deste repositório foram preservados.

Para comandos da ENV, entre no repositório **alvo**, com ao menos um commit:

```sh
bash "$SKILL_DIR/scripts/detect.sh"
# Revise .envstack/stack.yaml antes de continuar.
bash "$SKILL_DIR/scripts/init.sh"
ENV_DRY_RUN=1 bash "$SKILL_DIR/scripts/new.sh" exemplo
```

Detect/init geram arquivos locais. O dry run também cria worktree e resolve
arquivos de ambiente; não é uma operação somente leitura. Esses comandos não
constituem autorização para criar infraestrutura ou descartar dados.

## Configuração

### ENV

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
python3 "$SKILL_DIR/scripts/check_config.py" --project <caminho-do-projeto>
```

A validação não conecta, autentica ou confirma permissões. Veja
[configuração](skills/vps-deploy/references/configuracao.md).

### Limpar OrbStack

É um roteiro operacional, sem comando automático de limpeza. Exige projeto e
ambiente/critério delimitado, contexto `orbstack` validado, prova de integração,
preservação de dados e propriedade exclusiva dos recursos. Não faz prune global,
não reinicia OrbStack e não remove infraestrutura compartilhada. Um pedido de
instalar, copiar ou editar a skill não autoriza executá-la.

## Verificação local segura

Requisitos: Python 3.9+ e Bash; para os testes de ciclo de vida da ENV, Git,
`yq` de Mike Farah v4, `jq`, `envsubst` e Docker CLI com Compose. Para operação
real, a ENV é orientada a macOS/Homebrew e Compose com `--wait --wait-timeout`.
Nenhuma dependência é instalada automaticamente pelos testes.

Execute a partir da raiz do Bezalel:

```sh
python3 -B scripts/check_repository.py
python3 -B -m unittest discover -s skills/env/tests -v
python3 -B -m unittest discover -s skills/vps-deploy/tests -v
```

O checker verifica estrutura, links locais e metadados essenciais, sem alterar
arquivos ou exigir atualização de hashes a cada edição.
Os testes usam repositórios temporários e simulam operações Docker, brew, sudo
e mkcert; o CLI real só valida Compose estaticamente, sem acessar o daemon.
Os testes Python de VPS usam entradas sintéticas, sem rede. As skills documentais
não precisam de uma suíte de runtime artificial. Os cenários de limpeza estão
em [validação](skills/limpar-orbstack/references/validacao.md).

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

Para contribuir, siga [AGENTS.md](AGENTS.md). Não há publicação automática.
