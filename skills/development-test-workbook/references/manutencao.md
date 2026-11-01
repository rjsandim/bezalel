# Manutenção da skill

Leia somente ao alterar o gerador, o template ou o contrato. Gerar um roteiro em
um projeto não exige rodar estes testes.

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Os testes usam fixtures sintéticas e exigem `openpyxl` 3.1.x. Eles conferem as
seis abas do template, preservação de resultados, datas e links, expansão de
capacidade (fórmulas, filtros e validações), conteúdo parecido com fórmula
mantido como texto, rejeição de IDs, referências, status e datas inválidos e
execução da cópia isolada da skill. Eles verificam estrutura e expressões, não
o cálculo nem a aparência no aplicativo de planilhas.

Os nomes das abas e colunas são compartilhados com o checker do Bezalel
(`validate_workbook_template`); mudar um deles exige alterar template, gerador,
checker e testes juntos.
