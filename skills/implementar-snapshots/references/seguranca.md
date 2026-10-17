# Integridade e isolamento

## Identidade antes da escrita

Valide projeto, ambiente e recurso efetivamente acessado. Uma combinação útil é
raiz do projeto + ambiente + contexto/endpoint Docker explícito + identidade do
container/volume + servidor/porta/schema/usuário observados pela conexão. Adapte
para recursos sem Docker sem inventar um runtime universal. Use as evidências
locais de propriedade disponíveis; não confie apenas no nome/prefixo do recurso.

Recuse quando ambiente for produção, desconhecido ou não permitido; quando a
conexão observada divergir do alvo esperado; ou quando faltar evidência de
isolamento. Cheque também a configuração efetiva após cache de configuração,
URLs de conexão, aliases, sockets e túneis: `localhost` não prova banco local.
Use credenciais de restore restritas ao schema autorizado, sem privilégios de
servidor, arquivo, concessão ou acesso a outras bases. Não gere essas credenciais
nem procure segredos para conseguir executar a tarefa.

O snapshot nunca fornece o destino ou amplia sua allowlist. `--yes`, `--force`
e ausência de interação não contornam bloqueios. A autorização humana para uma
operação deve corresponder ao alvo/artefato revisados; uma flag ou JSON de plano
não prova autorização. Revalide identidade após adquirir o lock e imediatamente
antes da primeira escrita para reduzir divergências entre plano e execução.

## Integração com ENV

Quando o projeto usa ENV, consulte seu manifesto e o estado local da instalação
atual, sem copiar estado de outro checkout/agente. Confira raiz registrada,
contexto Docker, Compose/serviço, banco e volumes específicos. Não use contexto
ativo por fallback. Prefixos iguais e disponibilidade HTTP não provam propriedade.

Use ambiente já isolado quando houver. Se criar/iniciar ambiente exigir efeitos
sobre DNS, CA, Traefik ou rede compartilhada, siga o escopo e a autorização da
skill `env`; o pedido para implementar snapshots não os autoriza automaticamente.
`ENV_DRY_RUN=1` ainda gera arquivos/worktrees, não é uma operação de leitura pura.

Isolamento inclui arquivos, banco, filas/Redis, portas e storage. Mantenha workers,
scheduler, webhooks de saída, e-mail, cobrança e integrações externas incapazes
de agir sobre dados restaurados. Aplique esse bloqueio antes do import; não
dependa da última instrução SQL nem de `integrations.mode` isoladamente.

Verifique o boot do stack: migrations/seeds automáticos e workers podem tocar
no banco antes do comando de restore. Execute o restore por um caminho controlado
que não dispare esses efeitos. Não pare/remova serviços compartilhados para obter
isolamento. Não use limpeza de volumes como recuperação automática.

## Antes do restore

1. Resolver ID imutável do artefato em origem confiável e projeto esperado.
   Baixar para temporário privado com nome gerado. Não aceitar caminhos absolutos,
   `..`, symlinks ou arquivos fora da raiz de trabalho a partir de metadados.
2. Verificar manifesto, formato, engine, versão de schema, versão de sanitização,
   hash e tamanhos. Limitar bytes comprimidos/descomprimidos, quantidade de frames
   e tamanho de cada statement; validar gzip/frames até o fim antes de qualquer DDL.
   Arquivo vazio, truncado, incompatível ou incompleto falha sem tocar no destino.
3. Validar separadamente a identidade e isolamento do destino; adquirir lock por
   destino. Conferir espaço disponível e plano de preservação dos dados existentes.
   Uma base de desenvolvimento pode conter trabalho valioso.
4. Apresentar o plano concreto, sem credenciais: projeto, alias e identidade do
   destino, snapshot, modo, schema e efeito de substituição. Reutilizar autorização
   já dada para esse escopo, pedindo decisão só quando ela estiver ausente.

Checksum e marcador de conclusão não tornam SQL arbitrário confiável. Restrinja
quem pode publicar o payload e o manifesto; rejeite artefatos fora do contrato
do produtor. Não implemente “segurança” filtrando SQL por regex. O importador e
suas credenciais não devem permitir que o payload afete outro banco ou execute
objetos não suportados. Não execute helpers/scripts vindos do snapshot.

## Restauração e recuperação

Prefira restaurar numa base descartável isolada e validá-la antes de habilitar
a aplicação nela. A criação dessa base e eventual troca de configuração seguem
o plano aprovado; não faça a troca nem apague a anterior implicitamente.

Se o projeto realmente precisar substituir uma base existente, preserve o que
for necessário e defina recuperação antes de iniciar. Não prometa rollback de
um dump DDL: `CREATE TABLE` e `DROP TABLE` comuns causam commits implícitos no
MySQL. Uma falha deixa o destino indisponível para uso até recuperação explícita.
Veja [commits implícitos no MySQL](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html).

Após importar, confira inventário esperado (inclusive tabelas extras), schema,
contagens, campos sanitizados, unicidade, pais obrigatórios, pivôs e invariantes
de domínio. Resolver uma FK com checks desativados não é prova de integridade:
reativá-los não verifica retroativamente as linhas inseridas. Use consultas de
órfãos/validações explícitas adequadas às chaves simples e compostas.
Veja [verificação de FKs no MySQL](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html).

Restaure opções de sessão e feche conexões mesmo em erro. Falha de SQL, disco,
storage ou validação impede a mensagem de sucesso e a liberação do app. Guarde
apenas diagnóstico seguro e IDs da execução; não imprima SQL com dados ou DSN.
Não retome cegamente do statement seguinte após erro. Limpe só os temporários
criados pela execução, preservando a falha principal e relatando limpeza parcial.

Não execute migrations, seeds, envio de notificações ou rebuilds externos como
pós-restore implícito. Compatibilidade deve ser decidida antes; eventual migração
posterior é uma etapa separada, testada e autorizada conforme o projeto.

## Limite da consistência de origem

Uma transação consistente protege leituras de dados nas condições suportadas
pelo engine; ela não resolve mudanças concorrentes de estrutura. A origem precisa
de janela sem DDL ou outra estratégia comprovada pelo projeto. Não tome locks
invasivos em produção como consequência automática de implementar a feature.
Veja [leituras consistentes e DDL no MySQL](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html).
