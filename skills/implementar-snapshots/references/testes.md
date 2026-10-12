# Validação com fixtures e mocks

O objetivo é testar a implementação criada no projeto, não provar que palavras
ou títulos existem na skill. Use o runner já adotado e doubles para conexão,
metadata, storage, relógio e efeitos externos. Nenhum cenário padrão conecta a
banco real, usa Docker daemon, lê `.env`/dump real ou executa restore no Carisma.

## Fixture relacional

Use [tiny-relations.json](../templates/tiny-relations.json) como contrato sintético
de entrada/saída. Datas/IDs são artificiais e não vieram do projeto de origem.
Transforme-a em arrays/factories do projeto; não a aplique a uma base existente.

A política da fixture mantém contas/usuários completos, exclui dados das sessões,
recorta pedidos/itens por `updated_at` e inclui os pais necessários e todos os
itens dos pedidos retidos. O item recente 100 exige o pedido antigo 20. O pedido
recente 21 exige o item antigo 101 pelo contrato do cenário. O pedido antigo 22
e seu item 102 ficam fora do `tiny`. `full` mantém todos esses dados permitidos.
Contas completas aqui são deliberadas; esta fixture não representa um filtro
por tenant nem autorização para copiar tenants reais.

No teste da seleção, compare IDs com `expected` e comprove que nenhum vínculo
obrigatório fica sem destino. No teste do artefato, prove que `forbidden_values`
não aparecem em nenhum payload/manifesto/log capturado; os valores são somente
marcadores sintéticos. Comprove também as transformações esperadas por campo:
ausência de uma amostra não certifica toda a política de privacidade.

## Cenários mínimos observáveis

| Grupo | Entrada/falha simulada | Resultado esperado |
|---|---|---|
| Contrato | Tipo inválido, dias zero/negativos/textuais/excessivos, config ausente, tabela nova/coluna inválida | Erro antes de abrir writer, publicar ou executar SQL mutável. |
| Modos | Fixture relacional nos dois modos | `full` conserva dados permitidos; `tiny` corresponde às chaves esperadas; somente estrutura tem zero linhas. |
| Recorte | Registro exatamente no corte, antes/depois, fuso, data nula e coluna ausente | Semântica inclusiva e política explícita; nenhuma conversão silenciosa para tabela completa. |
| Relações | Pai antigo, filho antigo necessário, pivô, ciclo, FK composta, polimórfica, pai proibido e teto excedido | Fechamento termina; dependências preservadas; conflito/teto falham sem truncar arbitrariamente. |
| Tenant | Relação atravessa escopo de tenant autorizado | Erro explícito sem ampliar o conjunto permitido. |
| Sanitização | Marcadores em campos simples, JSON, texto livre, metadados e integração | Nenhum marcador original no artefato/log; preservados tipos, unicidade e vínculos; política versionada. |
| Fidelidade | NULL, string vazia, Unicode, aspas, barras, NUL, binário, newline e delimitador literal | Round-trip sintético preserva valores permitidos sem executar payload como código. |
| Limites | Linha individual enorme, lote próximo ao teto, gzip de expansão excessiva | Limite aplicado antes de crescimento/destruição; erro com recursos liberados. |
| Criação | Exceção na leitura, escrita curta, disco cheio, falha de compressão/upload | Artefato não elegível; último snapshot bom preservado; cleanup restrito à execução. |
| Concorrência | Duas criações mesma origem, dois restores mesmo destino | Lock evita concorrência indevida; nomes temporários únicos; locks liberados em erro. |
| Publicação | Falha entre payload, manifesto e ponteiro opcional | Consumidor não observa versão parcial nem mistura execuções. |
| Produção | `APP_ENV=production` com confirmação/force | Bloqueio antes de qualquer escrita. |
| Destino | `APP_ENV=local` mas identidade aponta produção, alias errado, contexto divergente, túnel, alvo ausente | Bloqueio; não usar conexão padrão nem confiar só no host. |
| Corrida | Alvo muda após preview/obtenção do lock | Revalidação bloqueia antes da mutação. |
| Arquivo | Ausente, vazio, gzip truncado, hash divergente, manifesto de outro projeto, versão incompatível, path traversal | Nenhum DDL/DML no destino, mesmo com confirmação. |
| Confiança | Payload/manifesto de produtor não autorizado com hashes coerentes | Origem rejeitada; checksum isolado não concede confiança. |
| Planejamento | `--dry-run` ou cancelamento | Zero chamadas de DDL/DML, upload, cleanup destrutivo, alteração de config ou disparo externo. |
| Restore | Erro depois de um DDL, órfão, contagem divergente, tabela extra | Erro e destino indisponível para aplicação; sem alegar rollback integral. |
| Efeitos | Import contém antigas referências de cobrança/mensagem | Zero dispatch, HTTP, e-mail, scheduler ou escrita no storage compartilhado. |
| Arquivos | Modo exclude/fixtures e referência ausente | Comportamento documentado e testado; nunca buscar o objeto real como fallback. |

Para cada bloqueio, faça uma asserção sobre o efeito perigoso: por exemplo,
`writer.calls == []` e destino/versão anterior inalterados. Não teste apenas a
mensagem de erro. Os fakes devem falhar se houver chamada fora do escopo esperado.

## Limites da evidência

Mocks não comprovam semântica real de MySQL, drivers, TLS, IAM, constraints,
transações ou S3. Não use SQLite para declarar compatibilidade MySQL comprovada.
Registre o que permanece não ensaiado. Um ensaio com engine real exige nova etapa
explicitamente autorizada, base descartável exclusiva e dados sintéticos; não
faça parte da validação segura automática desta skill.

O template PHP pode ser validado com `php -l` sem bootstrap do projeto. Confira
que o executável é um binário local, não um wrapper que inicia infraestrutura.
JSON pode ser lido por parser local. Checks de estrutura/links/frontmatter validam apenas
o pacote, não a funcionalidade que a skill ensinará a construir.
