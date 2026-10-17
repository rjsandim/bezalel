# Origem e adaptação

Importada da skill pessoal Codex `development-test-workbook`, preservando a
instalação original. A origem continha instruções, contrato, adaptador de interface,
template vazio e gerador JavaScript baseado em `@oai/artifact-tool`.

A cópia Bezalel conserva as seis abas, colunas, listas de validação e fórmulas.
O gerador foi adaptado para Python/openpyxl, usando o template incluído, para
eliminar dependência do loader e do pacote específico do aplicativo. Não exige
acesso a outros projetos nem instalação global. O template foi corrigido para
preservar congelamento de painéis e remover uma referência Q01 sem consulta.

Diferenças: saída explícita sem sobrescrita, validação de IDs/referências/status,
texto de entrada mantido como texto (inclusive quando começa com `=`), expansão
conjunta de tabelas/filtros/fórmulas/validações. As fórmulas são recalculadas pelo
aplicativo de planilhas ao abrir; não há cálculo ou renderização pelo gerador.

A importação foi validada com fixtures sintéticas e leitura OOXML/openpyxl.
Nenhum dado de produto, ambiente real, SQL de domínio ou segredo foi importado.
A disponibilidade de Excel/LibreOffice ou renderizador precisa ser conferida no
ambiente que produzir o roteiro final.
