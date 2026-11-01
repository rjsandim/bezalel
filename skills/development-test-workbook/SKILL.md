---
name: development-test-workbook
description: Cria e atualiza roteiros manuais de teste em Excel (.xlsx) para uma feature, correção, PR ou desenvolvimento, com casos, dados do ambiente, verificações de persistência, evidências e backlog de falhas. Use quando o pedido for "monta uma planilha de testes", "quero um roteiro de teste manual em Excel", "matriz de casos para homologação" ou "plano de testes para o QA executar". Para escolher quais provas automatizadas ou de risco são necessárias, use verification-planning; para escrever testes automatizados, use as ferramentas do projeto. Gerar o arquivo não executa os casos.
---

# Plano de testes do desenvolvimento em Excel

## Objetivo e escopo

Produzir um `.xlsx` que permita executar cada cenário, comparar o observado com o
esperado na interface/API e na persistência, e registrar incongruências com
rastreabilidade. O arquivo segue as seis abas do [contrato](references/workbook-contract.md);
a [origem e adaptação](references/origem.md) registra a portabilidade. A geração
organiza o roteiro: execução e cobertura são comprovadas por quem executa.

## Entradas e pré-requisitos

- Pedido e decisões do usuário, história/critérios, diff, commits, issue/PR e
  testes pertinentes. Simulações usam fixtures identificadas como sintéticas.
- Ambiente isolado autorizado, unidades/tenants e integrações confirmados, quando
  o pedido incluir descoberta real. O que faltar evidência fica `A confirmar` ou
  `Bloqueado`, em vez de IDs, URLs ou estados inventados.
- Python 3.9+ e `openpyxl` 3.1.x já instalados (validado com 3.1.5). O gerador
  independe de Node e da raiz do Bezalel.
- `$SKILL_DIR`: pasta desta skill na instalação carregada, copiada inteira,
  incluindo `assets/`. Destino local autorizado para o arquivo.

## Procedimento

1. **Descubra o escopo.** Confronte requisitos e fontes autorizadas: UI, APIs,
   integrações, jobs, filas, webhooks, importações e consumidores afetados.
   Leia o [contrato do workbook](references/workbook-contract.md).
2. **Derive os casos pelo risco:** fluxo principal, variações, negativas,
   autorização, isolamento, compatibilidade, persistência e regressão, quando
   pertinentes. Identifique dados e unidade por caso, separe leitura de mutação e
   defina ordem segura, baseline e pré-condições. Sem persistência envolvida,
   justifique na aba de verificações em vez de criar consultas de enfeite.
3. **Prepare o JSON e gere** com os campos do contrato. O
   [template vazio](assets/test-plan-template.xlsx) é neutro; a
   [fixture](tests/fixtures/synthetic.json) serve só para testar o gerador.

   ```sh
   python3 "$SKILL_DIR/scripts/build_test_workbook.py" /caminho/spec.json /caminho/novo-roteiro.xlsx
   # Template sem casos:
   python3 "$SKILL_DIR/scripts/build_test_workbook.py" - /caminho/novo-template.xlsx
   ```

   O destino precisa ser novo (o script recusa sobrescrever). Para atualizar um
   plano, reconcilie antes o JSON com o Excel atual, preservando IDs, resultados,
   datas, evidências e backlog: gerar de novo a partir de um JSON antigo perde
   edições manuais.
4. **Confira a planilha** (veja Validação).
5. **Registre execução somente quando pedida:** observado, status, data,
   executor e referência sanitizada de evidência; falhas e bloqueios viram itens
   de backlog com reteste e issue/PR quando existirem. Caso só é aprovado com
   execução registrada.

## Saídas

Um `.xlsx` com Resumo, Guia de execução, Casos de teste, Dados do ambiente,
Consultas SQL (verificações de dados) e Backlog, mais referência ao arquivo,
cobertura, dados/unidade recomendados e limitações. Evidências brutas ficam
fora do arquivo, apenas referenciadas. Use destino local autorizado, como
`outputs/<tarefa>/`; dados e evidências reais ficam fora do Git, salvo pedido.

## Validação

Antes de entregar, confira o arquivo gerado:

- O script terminou sem erro e o arquivo abre com as seis abas na ordem do contrato.
- Todo caso tem ID `T###` único, passos observáveis e esperado na interface/API e
  na persistência (ou justificativa de não aplicável); toda referência a
  verificação (`Q##`) e a backlog existe.
- Após recalcular em Excel ou LibreOffice, as fórmulas do Resumo e do backlog
  mostram números e não há `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?` ou `#N/A`.
  `openpyxl` grava fórmulas sem calculá-las; sem aplicativo de planilha
  disponível, declare que cálculo e aparência não foram conferidos.
- Filtros, congelamento de painéis e listas de status/prioridade funcionam.
- Nenhum caso aparece aprovado sem execução registrada.

Testes do próprio gerador: [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. Gerar a planilha não autoriza
executar casos, consultar produção, restaurar snapshots, iniciar infraestrutura,
cobrar, alterar dados ou corrigir bugs encontrados; a execução usa local,
sandbox ou homologação com isolamento comprovado. As verificações são texto para
revisão, de preferência somente leitura; mutação destrutiva só com pedido
explícito. Segredos, tokens, cartões reais e dados pessoais desnecessários ficam
fora do JSON, do Excel, de logs e do Git. Publicar a planilha ou enviar
evidências depende de autorização.
