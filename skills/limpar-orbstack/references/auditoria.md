# Limpar OrbStack

Remova ambientes locais concluídos sem perder trabalho pendente. Determine o repositório e a integração de cada worktree; o diretório atual pode não pertencer a nenhum dos projetos envolvidos.

## Escopo e autorização

- Quando o critério pedido for **estar mergeado**, avalie os ambientes da skill `env` independentemente de seus containers estarem rodando, parados ou ausentes. Estar em uso é informação para planejar a parada e preservar dados, não motivo automático para excluir o ambiente da auditoria.
- Inclua as imagens locais exclusivas dos ambientes elegíveis, desde que nenhum container nem ambiente preservado as use ou referencie. Para uma continuação após excluir worktrees, use o registro da limpeza anterior para comprovar a origem das imagens; não exija recriar a worktree.
- Respeite filtros de projeto ou ambiente pedidos pelo usuário. Se ele limitar a limpeza aos que já deletou no OrbStack, consulte todos os containers e exclua do escopo os que ainda existem (`exited`, `created` e `restarting` também contam). Não acrescente esse filtro quando o pedido for limpar os mergeados. Outras worktrees e máquinas Linux ficam fora do escopo. Não execute `system prune`, `volume prune` nem limpezas por prefixos amplos.
- Um pedido de limpar ou excluir os ambientes já mergeados autoriza a remoção dos elegíveis nesse escopo. Confira essa autorização antes da mutação; não peça confirmação novamente quando ela já estiver clara na conversa. Um pedido apenas para olhar ou listar autoriza somente a auditoria.
- Ao criar ou editar esta skill, não execute a limpeza real para demonstrá-la.
- Trabalhe localmente: não faça merge, push, exclusão de branch remota, fechamento de PR ou alteração de produção.

## Inventário

Use a CLI com contexto explícito `docker --context orbstack`. Se esse contexto estiver indisponível, interrompa a operação; não use outro engine como substituto.

1. Localize a instalação da skill `env` disponível e leia seu `SKILL.md` antes de executar seus scripts. Use o caminho explícito da instalação identificada; não presuma diretório de agente. Seus registros ficam em `state/<projeto>/<ambiente>/docker-compose.yml`. Não trate pastas de infraestrutura, como `_traefik`, como ambientes.
2. Consulte `docker ps -a`, labels `com.docker.compose.project`, mounts e os registros de Compose. Projete somente nomes, estados, labels necessárias e caminhos; não imprima configurações completas que possam conter credenciais. Derive o nome do projeto Compose do arquivo ou dos metadados, sem confundi-lo com o nome de um serviço.
3. Relacione cada registro às pastas usadas nos bind mounts e contextos de build. Confirme a worktree em `git worktree list --porcelain`, seu `--show-toplevel` e seu `--git-common-dir` absoluto. Consulte o remote correspondente sem expor URLs com credenciais.
4. Capture HEAD, branch real (pode ser diferente do nome do ambiente ou estar ausente), estado local, arquivos não rastreados e arquivos ignorados relevantes. Leia as instruções aplicáveis do repositório.
5. Antes de apagar o estado `env`, registre os IDs, tags e labels de projeto/serviço das imagens associadas. Cruze o ID real da imagem de cada container, inclusive parado, e as referências dos ambientes preservados. Imagem sem tag ou sem container não é, por si só, imagem elegível.

**Duas armadilhas concretas:** uma pasta residual sem `.git` pode fazer `git -C` responder pelo repositório pai; isso não a torna uma worktree. Uma worktree pode estar dentro de outra worktree, fora de `<repo-principal>/.worktrees/<ambiente>`; não reconstrua seu caminho por convenção.

Sem correspondência inequívoca entre ambiente, worktree e repositório, preserve o item e registre a dúvida. Ausência de containers comprova ausência atual, não comprova merge nem que o ambiente chegou a ser iniciado.

## Comprovar integração

Descubra a branch padrão atual no remote de **cada** repositório. Atualize sua referência remota com fetch direcionado, sem checkout, reset, prune ou alteração da branch local. Se a atualização ou consulta remota falhar, preserve o candidato; uma referência antiga não basta.

Aceite uma destas evidências, registrando SHAs e a URL da PR quando houver:

| Evidência | Verificação necessária |
|---|---|
| Integração pelo histórico | O HEAD local é ancestral da branch padrão remota atualizada. |
| PR integrada por squash/rebase | A PR está merged no repositório e destino corretos; o HEAD local é igual ao HEAD integrado da PR ou comprovadamente seu ancestral; o commit de merge está contido na branch padrão atualizada. |
| Conteúdo integrado por outra branch | A árvore completa do HEAD local é idêntica à árvore de um commit comprovadamente contido na branch padrão atualizada (`git diff --quiet <commit-integrado> <HEAD-local>`). |

Nome de branch, título de PR, PR fechada, CI verde, similaridade parcial ou um merge antigo da mesma branch não provam integração do HEAD atual. Procure PRs pelo HEAD/commits quando o nome local diferir do remoto. `git cherry` ajuda a investigar, mas não substitui prova completa quando há squash ou merges.

Um HEAD integrado não cobre mudanças no diretório de trabalho:

- Preserve a worktree quando houver código, documentação, evidências ou outros arquivos locais ainda não integrados cuja exclusão não esteja autorizada. Compare arquivos locais com a branch remota quando isso puder resolver a dúvida; não exiba conteúdo sensível.
- Alterações comprovadamente regeneradas por instalação ou build podem acompanhar a limpeza, após backup verificado. Relatórios e evidências locais também podem ser retirados da worktree quando forem preservados integralmente na recuperação e não representarem implementação pendente. Um lockfile alterado não é automaticamente descartável: inspecione o diff. Em caso de dúvida, preserve a worktree.
- Verifique também arquivos ignorados, mesmo quando `git status` estiver limpo: `.env`, uploads, SQLite, relatórios e evidências podem existir apenas ali. Preserve esses arquivos em backup antes de remover uma worktree elegível.

## Executar e verificar

Apresente um resumo curto dos elegíveis e dos preservados. Para candidatos autorizados, leia [remoção](remocao.md) e execute a preservação, a remoção e a verificação descritas ali. Um candidato bloqueado não impede a limpeza dos demais que estejam comprovados e autorizados.

Relate em português quantas worktrees, branches locais e imagens foram removidas, os nomes agrupados por projeto, o motivo dos itens preservados e o caminho da recuperação. Diferencie remoção de worktree, remoção do estado `env`, remoção de tags e remoção efetiva de imagens. Só informe espaço recuperado quando houver medição confiável; a soma do tamanho das imagens inclui camadas compartilhadas. Não anuncie sucesso de um item cujo resultado não foi verificado.
