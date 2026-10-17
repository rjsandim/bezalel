---
name: development-test-workbook
description: Cria e atualiza roteiros manuais de teste em Excel para uma feature, correção, PR ou desenvolvimento, com casos, dados do ambiente, consultas de validação, evidências e backlog. Use quando o usuário pedir uma planilha, matriz ou roteiro em Excel; não substitui testes automatizados nem executa os casos ao gerar o arquivo.
---

# Plano de testes do desenvolvimento em Excel

## Objetivo e escopo

Produza um `.xlsx` que permita executar cada cenário, comparar o observado com o
esperado na interface/API e na persistência e registrar incongruências com
rastreabilidade. Preserve as seis abas do [contrato](references/workbook-contract.md).
A [origem e adaptação](references/origem.md) registra a portabilidade.
A geração organiza o roteiro; não testa a aplicação nem certifica cobertura.

## Entradas e pré-requisitos

- Pedido e decisões do usuário, história/critérios, diff, commits, issue/PR e
  testes pertinentes. Uma simulação usa fixtures identificadas como sintéticas.
- Ambiente isolado autorizado, unidades/tenants e integrações confirmados, quando
  o pedido incluir descoberta real. Não invente IDs, URLs, estados ou capacidades.
  Registre `A confirmar` ou `Bloqueado` quando não houver evidência.
- Python 3.9+ e `openpyxl` 3.1.x já disponíveis no ambiente escolhido; a adaptação
  foi validada com 3.1.5. O gerador não depende de Node, loader do Codex ou da raiz
  do Bezalel. Não instala dependências por conta própria.
- Destino local autorizado. Defina `SKILL_DIR` como a pasta desta skill efetivamente
  carregada; copie a pasta inteira, incluindo `assets/`, ao instalar.

## Procedimento

1. **Descubra o escopo.** Confronte requisitos e fontes autorizadas: UI, APIs,
   integrações, jobs, filas, webhooks, importações e consumidores afetados.
   Leia o [contrato do workbook](references/workbook-contract.md) antes de gerar.
2. **Derive os casos pelo risco.** Inclua fluxo principal, variações, negativas,
   autorização, isolamento, compatibilidade, persistência e regressão quando
   pertinentes. Identifique dados/unidade por caso. Separe leitura de mutações
   e defina ordem segura, baseline e pré-condições. Banco não aplicável exige
   justificativa; não invente SQL para preencher uma aba.
3. **Prepare o JSON e gere.** Use os campos do contrato. O
   [template vazio](assets/test-plan-template.xlsx) é neutro; a
   [fixture](tests/fixtures/synthetic.json) é apenas teste do gerador.

   ```sh
   python3 "$SKILL_DIR/scripts/build_test_workbook.py" /caminho/spec.json /caminho/novo-roteiro.xlsx
   # Template sem casos:
   python3 "$SKILL_DIR/scripts/build_test_workbook.py" - /caminho/novo-template.xlsx
   ```

   O destino deve ser novo: o script recusa sobrescrever. Para atualizar um plano
   existente, preserve IDs, resultados, datas, evidências e backlog. Confira a
   versão atual antes de exportar outra; gerar novamente com um JSON antigo não
   recupera edições manuais feitas no Excel.
4. **Confira a planilha.** Abra/recalcule em Excel ou LibreOffice, ou use um
   renderizador de planilhas já disponível. Inspecione as seis abas, filtros,
   painéis, validações, fórmulas e legibilidade. Se não houver aplicativo, informe
   a limitação; inspeção OOXML não comprova cálculo nem aparência renderizada.
5. **Registre execução somente quando pedida.** Atualize observado, status, data,
   executor e referência sanitizada de evidência. Relacione falhas/bloqueios a
   itens de backlog, incluindo reteste e issue/PR quando existirem. Não marque
   casos aprovados apenas porque o arquivo foi gerado.

## Saídas

Um `.xlsx` com Resumo, Guia de execução, Casos de teste, Dados do ambiente,
Consultas SQL e Backlog. Entregue referência ao arquivo, cobertura, dados/unidade
recomendados e limitações. Evidências brutas ficam fora dele, apenas referenciadas.
Use destino local autorizado, como `outputs/<tarefa>/`; mantenha dados e evidências
reais fora do Git, salvo solicitação explícita. O template vazio integra a skill.

## Validação

Execute os testes locais com fixtures sintéticas:

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Confira IDs e referências, casos em excesso à capacidade inicial, fórmulas do
Resumo e do backlog, filtros, congelamento e listas de status/prioridade. Procure
`#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` e `#N/A` após recalcular. `openpyxl` grava
fórmulas e pede recálculo ao abrir, mas não as calcula. Os testes conferem estrutura
e expressões; não substituem essa inspeção nem testes do produto.

## Limites operacionais

Gerar/importar esta skill não autoriza executar casos, consultar produção,
restaurar snapshots, iniciar infraestrutura, cobrar, alterar dados ou corrigir
bugs encontrados. Use local, sandbox ou homologação com isolamento comprovado.
Consultas são texto para revisão; o gerador não executa nem certifica SQL seguro.
Prefira somente leitura; não inclua mutações destrutivas sem pedido explícito.

Não grave segredos, tokens, cartões reais ou dados pessoais desnecessários no
JSON, Excel, logs ou Git. Mascare identificadores externos dispensáveis. Não
publique a planilha nem envie evidências sem autorização. Preserve resultados
existentes e reporte falhas; não amplie o escopo para conseguir uma execução verde.
