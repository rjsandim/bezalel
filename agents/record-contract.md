# Contrato local da entrega — versão 1

O [modelo](templates/delivery.example.json) é um registro de declarações, não um
log confiável de execução. Guarde a cópia do projeto em
`.bezalel/deliveries/<história>.local.json`, fora do Git quando houver referências
privadas. Antes disso, acrescente `/deliveries/*.local.json` ao
`.bezalel/.gitignore` do projeto sem sobrescrever regras existentes. A história,
propostas sanitizadas e rascunhos podem ser versionados conforme o projeto.

## Dados mínimos

| Campo | Contrato |
|---|---|
| `story` | Caminho relativo, dentro do projeto, para Markdown com ID `US-`, necessidade, critérios `AC-01:` únicos e dependências/limites explícitos |
| `owner` | Identidade responsável pela integração inteira; obrigatória antes de implementar |
| `implementers` | Identidades que implementam; não apenas nomes de papéis |
| `roles` | Seleção de papéis de entrega do catálogo; não ativa nem instancia agentes |
| `isolation` | Exatamente `files`, `database`, `queues`, `ports`, `storage`; `verified` com evidência, ou `not_applicable` com razão (arquivos sempre requer verificação) |
| `database` | `change: none` com razão, ou `structural` com proposta e registro de decisão humana aplicável |
| `checks` | Verificações com nome, status e evidência, ou `not_applicable` justificado |
| `qa` | Revisor diferente dos implementadores, resultado por critério e cenários adicionais fundamentados em requisito/risco |
| `integration` | `owner` igual ao responsável, `status: passed` e evidência do fluxo completo |
| `manual_test`, `pr_draft` | Caminhos relativos para arquivos não vazios com roteiro manual e rascunho da PR |

O projeto declara arquitetura e regras de negócio em `.bezalel/project.json` a
partir do [modelo de configuração](../.bezalel/project.example.json). Os documentos
referenciados precisam existir no projeto; nenhuma fonte remota é consultada.
`checks.test/lint/build` são listas de argumentos declaradas, não comandos que o
validador executa. Listas vazias significam que o projeto ainda deve decidir seus
comandos. Configuração não concede acesso ou aprovação.

## Roteiro manual em Excel

Quando o usuário pedir Excel, `manual_test` pode referenciar o `.xlsx` produzido
pela [skill development-test-workbook](../skills/development-test-workbook/SKILL.md),
com seis abas, passos, expectativas, evidências e backlog. Use caminho relativo
dentro do projeto, por exemplo `outputs/US-001/roteiro.xlsx`, e mantenha o artefato
local fora do Git quando contiver dados de execução. O JSON privado da entrega
também permanece fora do Git. Formatos anteriores de roteiro continuam aceitos.

O CLI verifica apenas existência, contenção no projeto e tamanho não vazio;
não abre Excel, recalcula fórmulas, avalia conteúdo ou comprova execução dos casos.
Gerar um template vazio não atende semanticamente um roteiro executável, mesmo
que passe nessa verificação estrutural. QA e integração continuam exigidos.
O responsável confere o conteúdo e registra limitações antes de entregar.

## Etapas verificadas pelo CLI

- `plan`: formato básico, história, critérios, papéis e configuração. Isolamento,
  implementadores e aprovações podem continuar pendentes. Não autoriza implementar.
- `implement`: também exige responsável, implementadores, isolamento declarado e
  situação de banco resolvida. O runtime ainda precisa verificar as evidências e
  a origem humana da aprovação **antes** de permitir alteração estrutural.
- `deliver`: também exige verificações, QA de todos os critérios, ao menos um
  cenário adicional com `name`, `basis`, `expected`, `status: passed` e `evidence`,
  integração, roteiro e rascunho de PR. Critério falho/bloqueado impede conclusão.

Resultados de critério usam `id`, `status: passed` e `evidence`. Checks usam
`name`, `status: passed` e `evidence`, ou `status: not_applicable` e `reason`.
Identidades e referências não são autenticadas pelo CLI: quem o integrar precisa
assegurar independência real de QA e resultados obtidos, não apenas nomes distintos.
Ele não avalia semanticamente se o requisito foi atendido ou se a cobertura basta.

## Banco estrutural

`database.proposal` referencia o arquivo revisado. `database.approval` só pode ser
preenchido depois de uma decisão real, com:

- `decision: approved` e `actor_type: human`;
- `actor`: identidade humana e `source`: referência verificável à interação;
- `recorded_at`: data/hora com fuso;
- `proposal_sha256`: SHA-256 dos bytes da proposta efetivamente aprovada.

O digest é apenas o vínculo pontual entre decisão e proposta; não reintroduz
checksums de todo o repositório. Alterar a proposta invalida o vínculo. O CLI
recusa ausência, autoaprovação declarada por agente e divergência de versão,
mas não consegue provar que a pessoa aprovou. Não gere um registro aprovado para
fazer o check passar. A aprovação de banco não autoriza publicação/merge/deploy.

## Contrato exigido do runtime futuro

1. Identificar tarefa/projeto e autorização concreta; carregar instruções e papéis.
2. Executar ferramentas permitidas para comprovar isolamento e resultados.
3. Obter a decisão humana real, verificar sua origem e vincular a proposta.
4. Invocar as verificações antes das transições e impedir efeitos bloqueados;
   invalidar o registro quando história/proposta/contexto mudarem.
5. Garantir a separação dos executores de implementação e QA e manter evidências.
6. Publicar PR, fazer merge/deploy ou ativar coleta somente com autorização própria,
   registrando o resultado real de cada ferramenta. Nada disso está implementado
   pelo Markdown, catálogo ou validador local.

Sem runtime integrado, o operador humano precisa conduzir esse processo. Não há
execução automática, interceptação de edições, agendamento ou acesso à produção.
