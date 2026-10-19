# Contrato local da entrega

O registro é um **snapshot opcional das declarações da demanda**, para conferência
local. A issue existente e suas submissões continuam sendo a fonte de requisitos,
decisões e evidências; sem issue, use a conversa e depois a PR. Não é necessário
manter um MD paralelo por demanda. O
[modelo](templates/delivery.example.json) é incompleto por intenção; não contém
aprovações ou resultados fictícios.

O registro e o catálogo usam `schema_version: 3`; a configuração do projeto
permanece em `schema_version: 2`. Esses campos identificam o formato dos dados,
não uma versão da equipe ou dos agentes.

Guarde o snapshot em `.bezalel/deliveries/<id>.local.json`; incorpore
`/deliveries/*.local.json` ao `.bezalel/.gitignore`. Referências privadas não entram
em Git. Proposta/roteiro/rascunho locais são artefatos ou exportações vinculados à
demanda, não fontes concorrentes. O validador só lê arquivos, não acessa serviços.

## Configuração do projeto

O [modelo](../.bezalel/project.example.json) declara `project`, documentos reais
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
| `plan` | Registro, cenário, issue real ou referência da demanda e papéis existentes. Pode ser intenção incompleta; não libera execução. |
| `database` | HTML temporário presente com hash, base e escopo; parecer técnico quando complexo. Conferência para apresentar ao humano, sem aprovação fabricada. |
| `investigate` | Critérios/dependências, devs e dono da integração, isolamento; feature exige escopo humano aprovado. |
| `implement` | Acrescenta investigação do escopo, UI/UX quando afetada e situação de banco resolvida. |
| `accept` | Candidato integrado, checks prévios, revisão TL, AppSec, QA e roteiro pronto para execução humana. |
| `deliver` | Candidato tecnicamente validado, roteiro e rascunho da PR. Não exige aceite humano para abrir a PR. |
| `handoff` | Acrescenta todas as PRs abertas/verificadas na base/head previstos, `draft: false`, CI observado e orientações manuais. |
| `accepted` | Aceite humano da versão/roteiro realmente executados na PR aberta. Não prova merge. |
| `merged` | Interação humana e consulta posterior ao serviço confirmando todas as PRs mergeadas na base/head previstos. |
| `finish` | Acrescenta issues existentes fechadas/verificadas e resultado completo do destroy do alvo registrado, ou ambiente comprovadamente não aplicável. |
| `close` | Confere destino sem implementação: adiamento, descarte, comportamento esperado ou transferência. Não exige testes/PR fictícios. |

Pendência em `blocker` impede avançar além de `plan`. Descreva motivo, dono e
condição de retomada, preserve histórico na issue e remova do snapshot somente
quando resolvida de fato. Para trabalho independente de parte bloqueada, delimite
a atribuição e justifique a independência conforme R6; isso não libera o conjunto.
Este CLI não intercepta ferramentas nem aplica automaticamente os gates do fluxo.

## Campos e objetos

`schema_version` é 3; `scenario` é `bug`, `improvement` ou `feature`. Campos abaixo
só precisam ser preenchidos quando exigidos pela etapa. Campos desconhecidos na
raiz são recusados; declarações de autorização não pertencem a este arquivo.

| Campo | Conteúdo |
|---|---|
| `issue` | `url` real ou `null` quando não houver issue, `scope_ref`, `dependencies`, `criteria: [{id, text}]`, `stories: []`; em feature, histórias com `url` real ou `null`, `scope_ref` distinto, `criteria` e `approval` do conjunto. IDs de critérios são únicos entre histórias e critérios globais, por exemplo `US-1:AC-01`. |
| `roles` | IDs do catálogo para a tarefa; humano nunca entra nesta lista. Aceite exige TL, QA e AppSec, além dos devs selecionados. |
| `owner`, `implementers` | Identidades reais. O dono da integração deve constar entre os devs executores; trocar somente rótulo não garante independência. |
| `isolation` | Exatamente `files`, `database`, `queues`, `ports`, `storage`: `status: verified` com `evidence`, ou `not_applicable` com `reason`; arquivos sempre precisam de prova. |
| `investigation` | `status: passed`, `evidence`, `scope` vinculado ao escopo atual. Hipótese não comprovada não vira causa por preencher o JSON. |
| `ui` | `status: not_applicable` e `reason`, ou `passed`, `evidence`, `reviewer` independente, `mock_ref` e `scope` atual. Conferir UI/UX antes da API definitiva afetada. |
| `database` | Booleanos `schema_change`, `migration`, `complex_relations` e `reason`. Se qualquer um for verdadeiro: `proposal` em `.bezalel/reviews/*.html`, `proposal_sha256`, `base_ref`, `scope`, `summary`, `proposal_ref`. Antes de implementar: `approval` real e `cleanup` confirmando exclusão. Relações complexas exigem `review` técnico identificado. |
| `candidate` | `id`, `context_ref` para componentes/builds, contratos, schema/dados/configuração; `repositories: [{name, base, head}]`, incluindo todos os repositórios envolvidos. |
| `checks` | Lista com `name`, `required` booleano e resultado passado com evidência/candidato. `not_applicable` só quando não obrigatório, com `reason`. Teste obrigatório falho/ausente bloqueia. |
| `integration` | Resultado passado com `owner` igual ao dev integrador e evidência da integração inteira. |
| `review` | Parecer TL passado, `reviewer` distinto dos autores e evidência/candidato. TL lê as provas, não executa testes. |
| `security` | Parecer AppSec passado, revisor distinto, `coverage`, `material_gap: false`, `findings` e evidência/candidato. Ver tratamento abaixo. |
| `qa` | Parecer passado, revisor distinto, `criteria: [{id, status, evidence, candidate}]`, `additional_scenarios` fundamentados; feature também exige `journeys` globais. |
| `manual_test` | `path` local e `candidate`. Melhoria/feature exigem `.xlsx`; bug segue a necessidade. Arquivo existente não comprova roteiro adequado ou executado. |
| `acceptance` | Decisão humana sobre candidato e bytes do roteiro, mais `execution_evidence` da execução humana real. |
| `pr_draft` | Caminho local para preparar a descrição; não é uma PR publicada nem autoriza entregá-la em modo draft. |
| `pull_requests` | Uma por repositório do candidato: `repository`, `url`, `base`, `head`, `state: open`, `draft: false` confirmado no serviço, `verified_at` com fuso, `ci: {status, evidence}`. |
| `handoff` | Resultado passado com candidato, `evidence` e `next_steps` manuais, incluindo CI pendente/falho. |
| `environment` | Identidade do ambiente registrada durante a tarefa; ver encerramento abaixo. |
| `completion` | Interação humana, merges, issues e resultado da limpeza, sem executar operações pelo checker. |
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
- Banco: `proposal_subject(database)` vincula `proposal_sha256` (bytes do HTML),
  `base_ref`, `scope` e as três classificações de impacto. `scope` é o vínculo
  atual de `scope_subject(issue)`. `proposal_ref` e `summary` preservam referência
  e resumo da estrutura/diferenças na issue/PR/conversa, fora do HTML temporário.
  Parecer complexo usa `status: passed`, `reviewer`, `evidence` e o mesmo `subject`,
  sem exigir ferramenta específica. Ajuste exige novo hash/parecer/decisão.
  Após decisão final real, `cleanup: {status: deleted, deleted_at, evidence}`
  registra a exclusão, posterior à decisão. `implement` exige HTML ausente e
  aprovação exata; `database` exige HTML presente e bytes correspondentes.
  O checker não exclui arquivos nem consegue reler os bytes depois da exclusão:
  a interação e a preservação da decisão/resumo precisam ser conferidas pelo executor.
- Aceite: `accept:` + SHA-256 de `{candidate, manual_sha256}`, com a referência do
  candidato e o digest dos bytes do roteiro. Alterar qualquer um invalida o vínculo.
- Risco: `risk:` + SHA-256 de `{candidate, finding}`, excluindo somente a aprovação
  do achado. Mudança do achado ou candidato exige reconferir o adiamento.

O JSON ordenado usa UTF-8, `ensure_ascii=False`, `sort_keys=True` e separadores
`,`/`:` sem espaços, conforme `digest()`. Esses são vínculos pontuais, não um
inventário de hashes da árvore. A mesma versão pode reaproveitar provas válidas;
prova afetada por mudança deve ser refeita pelo responsável. O CLI não verifica
se o HTML/resumo confere com a fonte real ou se a decisão precedeu uma ação já executada.

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
e `target_started_evidence` do destino iniciado na mesma issue.
Sem issue real, `issue_state` é `not_applicable`; registro e decisão permanecem na conversa.
`disposition_subject(record)` vincula a decisão à issue, tipo, motivo, destino,
dono e retomada, sem confundir observação técnica de estado com decisão humana.

O CI que só inicia após abrir a PR pode ser `pending` ou `failed` no handoff,
com evidência e próximos passos reais. Isso não dispensa checks prévios obrigatórios
nem autoriza esperar/corrigir, merge ou deploy automaticamente.

## Conferência de merge e encerramento

`completion.trigger` contém `kind: approved` ou `merge_reported`, `actor_type: human`,
`actor`, `source`, `recorded_at` e `candidate`. É a interação real que solicita a
retomada, não uma permissão criada pelo JSON. Aprovação não significa merge.

Em `merged`/`finish`, cada item de `pull_requests` preserva URL, repository,
base/head da entrega e acrescenta `state: merged`, `merged_at`, `merge_commit`,
`evidence` da consulta ao serviço e `verified_at` posterior à interação e ao merge.
Todas as PRs necessárias devem estar presentes. PR fechada sem merge, mudança de
head, falta de acesso ou consulta antiga mantém pendência. A comparação considera
head da PR e merge commit separadamente, inclusive squash/rebase.

Para `finish`, registrar `completion.scope_complete: true` e `scope_evidence`
somente após conferir ausência de trabalho restante. `completion.issues` lista
exatamente a issue principal e histórias com URL: `url`, `state: closed`,
`verified_at` posterior à conferência dos merges e `evidence`. Sem issue, lista
vazia; não criar uma só para fechar. Se o serviço já fechou a issue, verificar em
vez de repetir. Limpeza falha não desfaz o fechamento correto da issue.

`environment` identifica `project`, `repository`, `branch`, `worktree`, `name`,
`docker_context` e `ownership_evidence`, capturados na tarefa. `branch` é a da
worktree da entrega; `name` é o ambiente efetivamente associado no estado da skill,
que pode ser diferente. Nunca substituir pela branch atual após mudar diretório.
Sem ambiente gerenciado, usar `status: not_applicable`, `reason` e `evidence` reais.

`completion.environment` registra `target: environment_subject(environment)`,
`status: destroyed`, `preservation_evidence`, `command_evidence`, `evidence`,
`worktree_removed: true` e `verified_at` após conferir merges/issues. O executor
confere projeto/contexto/alvos e usa a skill env carregada com a confirmação exata.
Backups e arquivos necessários ficam fora da worktree antes da remoção. Não usar
força nem remover recursos por prefixo. Bloqueio de ancestralidade após squash ou
rebase não autoriza apagar commits; usar preservação e reportar parcialidade.
`--keep-worktree` não satisfaz encerramento completo; `finish` continua pendente.
Quando não aplicável, o resultado também declara `status: not_applicable` e evidência.

Conserve o registro, referências e configuração necessários fora da worktree antes
da limpeza. `merged`/`finish` não exigem reler roteiro ou outros artefatos já removidos:
conferem a declaração de conclusão e a versão identificada. Não provam consulta ao
GitHub, fechamento de issue, backup ou destruição. Essas ações são do executor real;
o checker nunca as executa, nem inicia acompanhamento em segundo plano.

## Migração e limites

Registros antigos são recusados: migre conscientemente para o formato 3, mantendo
provas reais. Para banco, não troque um MD antigo por aprovação de HTML inventada;
se ainda houver implementação dependente, prepare/apresente a proposta adequada.
Confirme referências, base/hash, decisão e exclusão. Aceite funcional fica separado
da abertura de PR; não preencha aceites, merges ou limpeza para satisfazer o checker.
A configuração de projeto permanece no formato 2. Atualizadores anteriores ao
catálogo local precisam da migração pelo atualizador novo descrita no README.

Os checks são estruturais. Autenticação humana, independência real, veracidade da
evidência, cobertura, HTML e Excel dependem dos executores. O fluxo completo está
em [DreamTeam](dream-team.md); este esquema não é um runtime ou autorização.
