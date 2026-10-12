# Contrato do workbook

Use este contrato como piso estrutural. Adapte nomes e cobertura ao domínio, mas preserve a relação entre casos, banco, evidências e backlog.

## Abas obrigatórias

### 1. Resumo

Inclua indicadores calculados por fórmula:

- total de casos;
- não iniciados;
- em execução;
- aprovados;
- falharam;
- bloqueados;
- progresso concluído;
- itens de backlog preenchidos e ainda abertos.

Inclua também uma matriz de cobertura que cruze as dimensões relevantes do desenvolvimento, por exemplo integração, UI/API, regra, dados, sucesso, falha/retry, migração/compatibilidade e segurança.

### 2. Guia de execução

Explique ambiente, links, ordem segura, baseline, blocos mutáveis, restauração, evidências e critérios de severidade. Use as colunas:

`Seção | Item | Orientação | Link / valor | Obrigatório? | Resultado esperado`

### 3. Casos de teste

Uma linha por comportamento verificável, com estas colunas:

`Ordem | ID | Prioridade | Área | Integração | Unidade | Canal / tela | Família / dados | Pré-condição | Passos manuais | Esperado na interface / API | Esperado no banco | SQL IDs | Evidência a anexar | Resultado da execução | Resultado observado | Data | Executor | Ação backlog | ID backlog`

Regras:

- IDs estáveis no formato `T001`, `T002` etc.;
- passos reproduzíveis e observáveis, não descrições vagas;
- esperado no banco deve citar tabelas/colunas ou invariantes quando aplicável;
- `SQL IDs` referencia a aba Consultas SQL;
- `Ação backlog` é fórmula e exibe `Criar item` para `Falhou` ou `Bloqueado`;
- resultado usa `Não iniciado`, `Em execução`, `Aprovado`, `Falhou` ou `Bloqueado`;
- prioridade usa `Crítica`, `Alta`, `Média` ou `Baixa`.

### 4. Dados do ambiente

Registre fixtures verificadas no ambiente autorizado; em simulações, identifique explicitamente dados sintéticos:

`Código | Uso principal | Unidade | Integração | Entidade principal | Entidades relacionadas | Estado inicial | Estado esperado | IDs úteis | Link de entrada | Fonte no banco | Observações`

Não copie dados pessoais além do mínimo necessário. Prefira código de caso, IDs e nomes sanitizados.

### 5. Consultas SQL

Use consultas somente leitura para confrontar antes/depois:

`SQL ID | Quando usar | Objetivo | Consulta somente leitura | Esperado antes | Esperado depois | Cuidados`

Use placeholders claros como `<USER_ID>` quando o ID depende da execução. Não coloque segredos ou valores de cartão nos resultados.

### 6. Backlog

Uma linha por incongruência independente:

`ID backlog | Teste origem | Data | Unidade | Integração | Severidade | Tipo | Resumo | Esperado | Observado | Evidência / link | SQL usado | Responsável | Status | Issue / PR | Reteste`

Status sugeridos: `Novo`, `Em análise`, `Em correção`, `Pronto para reteste`, `Fechado`, `Descartado`.

## Especificação JSON do gerador

O script aceita dois argumentos:

```text
python3 "$SKILL_DIR/scripts/build_test_workbook.py" <spec.json> <novo-output.xlsx>
```

O primeiro pode ser `-` para gerar o template neutro. Estrutura:

```json
{
  "title": "Plano manual — nome do desenvolvimento",
  "subtitle": "Escopo e ambiente avaliados.",
  "warning": "Ordem segura e restrições operacionais.",
  "generalAcceptance": "Critério de aceite transversal.",
  "guide": [
    {
      "section": "Ambiente",
      "item": "Unidade principal",
      "guidance": "Por que usar este ambiente",
      "link": "https://ambiente.local/rota",
      "required": "Sim",
      "expected": "Estado localizável"
    }
  ],
  "coverage": [
    {
      "dimension": "Integração A",
      "uiApi": "T002–T004",
      "rules": "T005",
      "dataSetup": "T006",
      "success": "T007",
      "failureRetry": "T008",
      "migrationCompatibility": "T009",
      "security": "T010"
    }
  ],
  "cases": [
    {
      "order": 1,
      "id": "T001",
      "priority": "Crítica",
      "area": "Baseline",
      "integration": "Todas",
      "unit": "Todas",
      "channel": "Banco",
      "fixture": "Snapshot ou fixture",
      "precondition": "Ambiente restaurado",
      "steps": "Executar Q01",
      "expectedSurface": "Não se aplica",
      "expectedDatabase": "Contagens e invariantes",
      "sqlIds": "Q01",
      "evidence": "Resultado sanitizado",
      "result": "Não iniciado",
      "observed": "",
      "date": null,
      "executor": "",
      "backlogId": ""
    }
  ],
  "environmentData": [
    {
      "code": "FIX-01",
      "use": "Fluxo principal",
      "unit": "tenant-a",
      "integration": "Sandbox",
      "primaryEntity": "<ID>",
      "relatedEntities": "<IDs>",
      "initialState": "Estado confirmado",
      "expectedState": "Estado após o caso",
      "ids": "IDs mínimos",
      "entryLink": "https://ambiente.local",
      "databaseSource": "tabelas/consulta",
      "notes": "Sem dados sensíveis"
    }
  ],
  "queries": [
    {
      "id": "Q01",
      "when": "Antes e depois",
      "objective": "Conferir baseline",
      "sql": "SELECT ...",
      "expectedBefore": "Estado inicial",
      "expectedAfter": "Mudança limitada",
      "care": "Somente leitura"
    }
  ],
  "backlog": []
}
```

Campos opcionais ausentes ficam vazios; casos recebem `Não iniciado` se o resultado
não for informado. IDs de casos (`T001`), consultas (`Q01`) e backlog são únicos;
os itens preenchidos exigem ID. Referências SQL usam IDs separados por espaço,
vírgula ou ponto e vírgula e precisam existir; `backlogId` e `testId`, quando
informados, também precisam existir. Datas usam `YYYY-MM-DD`. Status e prioridades
seguem as listas acima. O gerador reserva no mínimo 200 casos e 100 itens de
backlog e expande tabelas, filtros, validações e fórmulas para entradas maiores.

O destino deve ser um novo `.xlsx`; não há sobrescrita implícita. Fórmulas não são
aceitas como código nos campos de conteúdo. Somente fórmulas internas do gerador
são gravadas como fórmulas Excel. Nenhum SQL, link ou caso é executado.

Para atualizar, reconcilie primeiro JSON e Excel atual, preservando resultados e
IDs. O gerador não importa edições feitas manualmente no workbook. Salve em outro
arquivo e confronte antes de substituir a versão usada pelo executor.

## Evidências

O Excel guarda referências, não os arquivos brutos. Uma boa referência informa tipo, caso, timestamp e caminho/link sanitizado. Nunca exponha chave, token, PAN, CPF/e-mail desnecessário ou payload integral com dados pessoais.

## Critério de completude

O plano está pronto quando outra pessoa consegue:

1. escolher o ambiente correto;
2. executar o caso sem contexto oral adicional;
3. observar o resultado na superfície e no banco;
4. distinguir falha de bloqueio ambiental;
5. abrir e retestar o backlog com vínculo ao caso original.
