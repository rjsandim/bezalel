# Origem e diferenças

Leitura estática de uma implementação Laravel/MySQL de um projeto privado, em 2026-10-12, no código baseado
na revisão `90fda6f6121ab427eb3aa561e12b0dc68c78ab27`. Foram examinados os comandos
`CreateSnapshotCommand`, `RestoreSnapshotCommand`, o concern
`InteractsWithDatabaseSnapshots`, `config/snapshot.php`, o disco pertinente em
`config/filesystems.php`, o scheduler e as dependências declaradas na API.
Não foram lidos dumps, `.env`, conteúdo de banco ou credenciais, nem executados
comandos de criação/restauração. Valores padrão de acesso não são reproduzidos.

Os caminhos acima são referências históricas relativas à API de origem, não
dependências da skill. O pacote pode ser usado sem esse repositório.

## Comportamento observado

| Parte | Comportamento do código lido |
|---|---|
| Interface | `snapshot:create {full|tiny}` aceita `--days` e `--force`; `snapshot:restore {full|tiny}` aceita `--force`. |
| `full` | Estrutura de todas as tabelas físicas; dados completos, exceto as tabelas configuradas como somente estrutura. Não significa cópia integral de tudo. |
| `tiny` | Mesmo schema; só as tabelas configuradas como recentes são filtradas. As demais mantêm todos os dados permitidos. |
| Recorte | Padrão de 30 dias; primeira coluna existente entre as preferidas, inicialmente `updated_at` e `created_at`; comparação inclusiva `>= cutoff`. Sem coluna elegível, exporta a tabela inteira com aviso. |
| Relações | Não há seleção por tenant, travessia de relacionamentos ou fechamento de dependências. A escolha é feita tabela por tabela. |
| Dados descartados | Categorias configuradas incluem logs, filas, cache, sessões, tokens e tabelas legadas. A lista é específica da aplicação, não uma política universal. |
| Extração | Laravel/PHP com MySQL, PDO dedicado sem buffering, `REPEATABLE READ` e transação com snapshot consistente para os dados. DDL é lido pela conexão padrão separada. |
| Formato | DDL e INSERTs em gzip, separados por uma linha marcadora própria. Lotes padrão de 500 linhas; flush quando o acumulado alcança aproximadamente 8 MiB. Não usa executável `mysqldump`. |
| Conteúdo | Apenas tabelas físicas: não exporta views, triggers, rotinas, eventos nem os objetos/arquivos de storage da aplicação. |
| Ajustes de dados | Acrescenta ao fim do SQL a troca de senhas de usuários e a mudança das integrações de produção para teste. |
| Artefatos | Temporário em storage da aplicação, nome fixo por tipo; upload por Flysystem/S3 sobrescreve a mesma chave. Disco padrão tem `throw=true`. |
| Agenda | Apenas em produção: `tiny` às 02:00 e `full` às 03:00 no fuso configurado; `withoutOverlapping` por entrada. Os comentários que chamam um de completo/enxuto estão invertidos. |
| Janela manual | Criação permitida entre 00h e 05h do fuso da aplicação por padrão; `--force` ignora essa janela. O comando manual não repete a restrição de ambiente do scheduler. |
| Restore | Recusa `app()->isProduction()`, confirma banco/host salvo `--force`, baixa o arquivo e executa seus statements na conexão padrão atual. Aumenta o limite de memória do processo. |
| Testes | Nenhum teste específico foi localizado por nomes dos comandos/concern ou pelas chamadas `snapshot:create` e `snapshot:restore` em `api/tests` e testes de módulos. Isso não prova ausência de testes externos. Nenhuma suíte do projeto foi executada. |

## Limitações e melhorias propostas

Estas são consequências inferidas do fluxo lido e requisitos para a nova skill;
não são correções já presentes na origem nem incidentes comprovados.

- **Sanitização tardia:** os INSERTs mantêm hashes e outros valores originais no
  arquivo. O UPDATE final só muda o banco restaurado. Não há anonimização geral
  de dados pessoais nem remoção abrangente de credenciais de integração.
  A nova implementação transforma/exclui valores antes da serialização.
- **Dependências do `tiny`:** recortes independentes podem excluir um pai ainda
  referenciado por um filho recente. O restore desliga FKs e não verifica órfãos.
  A nova implementação fecha relações necessárias e valida o resultado.
- **Destino:** a checagem de ambiente não detecta um processo local apontando
  para banco de produção. A nova implementação identifica e autoriza o recurso
  real, sem fallback para a conexão corrente.
- **Publicação e concorrência:** nomes locais/remotos fixos permitem colisões
  entre execuções manuais ou ambientes. A nova implementação usa identidade por
  projeto/origem/execução, lock no comando e publicação apenas após validação.
- **Integridade e falha:** não há manifesto, checksum esperado, versão de formato,
  verificação de contagens ou validação relacional. Restore aplica DDL destrutivo
  diretamente e pode deixar estado parcial. A nova implementação verifica o
  artefato primeiro e mantém a aplicação afastada até validar a restauração.
- **Limites técnicos:** valores de dias não têm validação estrita; o flush de
  INSERT ocorre depois de adicionar a linha; retorno de escrita gzip não é
  conferido. A nova implementação limita entradas, tamanho individual/total e
  detecta escrita curta, gzip truncado e buffers excessivos.
- **Consistência:** a transação dos dados não certifica DDL concorrente ou engines
  não transacionais. A nova implementação define o que suporta e falha quando
  não pode garantir um snapshot coerente.

O disco S3, horário e valores de limite são decisões da origem. Reutilize os
conceitos, não seus valores, inventário ou configuração operacional.
