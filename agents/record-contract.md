# Contrato local da entrega v2

O registro é um **snapshot opcional das declarações da issue**, para conferência
local. A issue e suas submissões continuam sendo a fonte de requisitos, decisões
e evidências. Não é necessário manter um MD paralelo por demanda. O
[modelo](templates/delivery.example.json) é incompleto por intenção; não contém
aprovações ou resultados fictícios.

Guarde o snapshot em `.bezalel/deliveries/<id>.local.json`; incorpore
`/deliveries/*.local.json` ao `.bezalel/.gitignore`. Referências privadas não entram
em Git. Proposta/roteiro/rascunho locais são artefatos ou exportações vinculados à
issue, não fontes concorrentes. O validador só lê arquivos, não acessa serviços.

## Configuração do projeto

O [modelo v2](../.bezalel/project.example.json) declara `project`, documentos reais
em `context.architecture/business`, interfaces, `checks.test/lint/build` como
listas de argumentos e `production_branches` como mapa repositório → branch real.
Não presuma main/master. Os nomes de repositórios precisam coincidir com os do
candidato. Configuração não contém permissões ou segredos e não executa comandos.

## Etapas conferidas

```sh
python3 .bezalel/base/scripts/check_delivery.py --project . --record .bezalel/deliveries/tarefa.local.json --stage plan
```

| Etapa | Declarações exigidas |
|---|---|
| `plan` | Registro v2, cenário, URL de issue e papéis existentes. Pode ser intenção incompleta; não libera execução. |
| `investigate` | Critérios/dependências, devs e dono da integração, isolamento; feature exige escopo humano aprovado. |
| `implement` | Acrescenta investigação do escopo, UI/UX quando afetada e situação de banco resolvida. |
| `accept` | Candidato integrado, checks prévios, revisão TL, AppSec, QA e roteiro pronto para execução humana. |
| `deliver` | Acrescenta aceite humano sobre candidato/roteiro executados e rascunho da PR. Ainda não comprova abertura. |
| `handoff` | Acrescenta todas as PRs abertas/verificadas na base/head previstos, CI observado e orientações manuais. |
| `close` | Confere destino sem implementação: adiamento, descarte, comportamento esperado ou transferência. Não exige testes/PR fictícios. |

Pendência em `blocker` impede avançar além de `plan`. Descreva motivo, dono e
condição de retomada, preserve histórico na issue e remova do snapshot somente
quando resolvida de fato. Para trabalho independente de parte bloqueada, delimite
a atribuição e justifique a independência conforme R6; isso não libera o conjunto.
Este CLI não intercepta ferramentas nem aplica automaticamente os gates do fluxo.

## Campos e objetos

`schema_version` é 2; `scenario` é `bug`, `improvement` ou `feature`. Campos abaixo
só precisam ser preenchidos quando exigidos pela etapa. Campos desconhecidos na
raiz são recusados; declarações de autorização não pertencem a este arquivo.

| Campo | Conteúdo |
|---|---|
| `issue` | `url`, `scope_ref`, `dependencies`, `criteria: [{id, text}]`, `stories: []`; em feature, histórias com `url`, `scope_ref`, `criteria` e `approval` do conjunto. IDs de critérios são únicos entre histórias e critérios globais, por exemplo `US-1:AC-01`. |
| `roles` | IDs do catálogo para a tarefa; humano nunca entra nesta lista. Aceite exige TL, QA e AppSec, além dos devs selecionados. |
| `owner`, `implementers` | Identidades reais. O dono da integração deve constar entre os devs executores; trocar somente rótulo não garante independência. |
| `isolation` | Exatamente `files`, `database`, `queues`, `ports`, `storage`: `status: verified` com `evidence`, ou `not_applicable` com `reason`; arquivos sempre precisam de prova. |
| `investigation` | `status: passed`, `evidence`, `scope` vinculado ao escopo atual. Hipótese não comprovada não vira causa por preencher o JSON. |
| `ui` | `status: not_applicable` e `reason`, ou `passed`, `evidence`, `reviewer` independente, `mock_ref` e `scope` atual. Conferir UI/UX antes da API definitiva afetada. |
| `database` | Booleanos `schema_change`, `migration`, `complex_relations` e `reason`. Se qualquer um for verdadeiro: `proposal`, `proposal_ref`, `approval`; relações complexas também exigem `review` do DB Reviewer. |
| `candidate` | `id`, `context_ref` para componentes/builds, contratos, schema/dados/configuração; `repositories: [{name, base, head}]`, incluindo todos os repositórios envolvidos. |
| `checks` | Lista com `name`, `required` booleano e resultado passado com evidência/candidato. `not_applicable` só quando não obrigatório, com `reason`. Teste obrigatório falho/ausente bloqueia. |
| `integration` | Resultado passado com `owner` igual ao dev integrador e evidência da integração inteira. |
| `review` | Parecer TL passado, `reviewer` distinto dos autores e evidência/candidato. TL lê as provas, não executa testes. |
| `security` | Parecer AppSec passado, revisor distinto, `coverage`, `material_gap: false`, `findings` e evidência/candidato. Ver tratamento abaixo. |
| `qa` | Parecer passado, revisor distinto, `criteria: [{id, status, evidence, candidate}]`, `additional_scenarios` fundamentados; feature também exige `journeys` globais. |
| `manual_test` | `path` local e `candidate`. Melhoria/feature exigem `.xlsx`; bug segue a necessidade. Arquivo existente não comprova roteiro adequado ou executado. |
| `acceptance` | Decisão humana sobre candidato e bytes do roteiro, mais `execution_evidence` da execução humana real. |
| `pr_draft` | Caminho local para rascunho não vazio; não é uma PR publicada. |
| `pull_requests` | Uma por repositório do candidato: `repository`, `url`, `base`, `head`, `state: open`, `verified_at` com fuso, `ci: {status, evidence}`. |
| `handoff` | Resultado passado com candidato, `evidence` e `next_steps` manuais, incluindo CI pendente/falho. |
| `disposition` | Destino sem implementação, conforme seção própria. |

Resultado passado usa `status: passed`, `evidence` e, nas provas da entrega,
`candidate` vinculado à versão. Cenários adicionais/jornadas usam também `name`,
`basis` e `expected`. Datas exigem fuso. URLs de issues/PRs precisam de HTTPS sem
credenciais embutidas; existência, acesso e estado são verificados pelo executor,
não pelo CLI.

## Vínculos de versão e decisões humanas

Uma decisão tem `decision: approved`, `actor_type: human`, `actor`, `source`,
`recorded_at` e `subject`. Só preencher a partir da interação real. Os vínculos
abaixo são produzidos pelas funções de leitura em `scripts/check_delivery.py`;
não criam autorização, identidade ou aprovação.

- `scope_subject(issue)`: `scope:` + SHA-256 do JSON ordenado do escopo, excluindo
  apenas `approval`. Vincula escopo de feature, investigação e UI/UX.
- `candidate_subject(candidate, config)`: `candidate:` + SHA-256 do JSON ordenado
  do candidato; valida bases contra o projeto. Identifica pareceres/provas.
- Banco: `proposal:` + SHA-256 dos bytes do arquivo em `database.proposal`, uma
  exportação da proposta exata indicada por `proposal_ref`. A decisão vale antes
  da implementação dependente. DB Reviewer usa `status`, `evidence`,
  `tool: DB Reviewer` e o mesmo `subject`.
- Aceite: `accept:` + SHA-256 de `{candidate, manual_sha256}`, com a referência do
  candidato e o digest dos bytes do roteiro. Alterar qualquer um invalida o vínculo.
- Risco: `risk:` + SHA-256 de `{candidate, finding}`, excluindo somente a aprovação
  do achado. Mudança do achado ou candidato exige reconferir o adiamento.

O JSON ordenado usa UTF-8, `ensure_ascii=False`, `sort_keys=True` e separadores
`,`/`:` sem espaços, conforme `digest()`. Esses são vínculos pontuais, não um
inventário de hashes da árvore. A mesma versão pode reaproveitar provas válidas;
prova afetada por mudança deve ser refeita pelo responsável. O CLI não verifica
se o export confere com a issue ou se a decisão precedeu uma ação já executada.

## Segurança e retomada

Cada achado identifica `id`, `summary`, `severity` (`critical/high/medium/low`),
`classification`, `confidence`, `evidence` e `disposition`:

- `fixed`: confirmação e evidência da correção revalidada no candidato;
- `false_positive`: classificação de falso positivo e prova;
- `deferred`: apenas médio/baixo confirmado, com `reason`, `owner`,
  `deadline_or_condition` e decisão humana exata em `approval`.

Hipótese ainda investigável, falta material de cobertura e crítico/alto não
resolvido impedem concluir. `confidence` é `high`, `medium` ou `low` e
`classification` é `confirmed` ou `false_positive` nos achados concluídos;
hipóteses não concluídas seguem interrupção/investigação, nunca aprovação fictícia.
Correção retorna ao TL/dev, depois integração e verificações afetadas.

## Destinos sem implementação e CI

`disposition.kind`: `deferred`, `discarded`, `expected_behavior` ou `transferred`.
Todos exigem `reason`, `evidence` do estado real e decisão humana. Descarte ou
comportamento esperado exigem `issue_state: closed`; adiamento/transferência,
`open`, `owner` e `resume_condition`. Transferência usa `target` de outro cenário
v2 e `target_started_evidence` do destino iniciado na mesma issue.
`disposition_subject(record)` vincula a decisão à issue, tipo, motivo, destino,
dono e retomada, sem confundir observação técnica de estado com decisão humana.

O CI que só inicia após abrir a PR pode ser `pending` ou `failed` no handoff,
com evidência e próximos passos reais. Isso não dispensa checks prévios obrigatórios
nem autoriza esperar/corrigir, merge ou deploy automaticamente.

## Migração e limites

Registros/configurações v1 são recusados com erro. Preserve-os fora do pacote e
migre conscientemente: remova observadores da configuração, informe branches
reais e substitua o caminho de história por referência à issue e escopo. Obtenha
as provas ausentes de investigação, UI/banco, TL/AppSec/QA, candidato, aceite e PRs;
não preencha sucesso para converter registros antigos.

Os checks são estruturais. A autenticação humana, independência real, veracidade
da evidência, adequação da cobertura e conteúdo do Excel dependem do executor e
do operador. O fluxo completo está em [Bezalel v2](company-flow-v2.md);
este esquema não é um runtime, agendador, autorização ou substituto do fluxo.
