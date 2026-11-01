# Preservação e remoção dos candidatos elegíveis

Leia após comprovar o merge e o escopo no `SKILL.md`. Este procedimento não amplia a autorização para descartar trabalho pendente, outros ambientes ou branches remotas.

## Preservar o que não pode ser recriado

Crie um diretório único por execução, fora dos repositórios, no local de recuperação combinado com o usuário (por exemplo `<recuperação>/<projeto>-<data-hora>/`), com diretórios privados (`0700`) e arquivos privados (`0600`). Não reutilize nem sobrescreva uma recuperação anterior.

Para cada candidato, guarde:

- Identidade do repositório, caminho real da worktree, branch real, HEAD, referência remota verificada e evidência de integração; omita credenciais dos metadados.
- Patches binários separados do índice e do diretório de trabalho quando existirem alterações elegíveis. Guarde também os arquivos novos e as versões atuais dos arquivos alterados; patches não incluem arquivos não rastreados.
- Arquivos ignorados que não podem ser reconstruídos do Git: configurações locais, uploads, bancos em arquivo, scripts locais, documentos e evidências. Mantenha os caminhos relativos. Arquive links simbólicos como links, sem seguir destinos externos.
- A pasta de estado do ambiente, incluindo Compose, overrides e inicialização do banco.
- Quando o HEAD original não for ancestral da branch padrão por causa de squash ou rebase, um bundle dos commits locais ausentes dessa referência pode preservar a base exata dos patches. Valide o bundle e registre seus pré-requisitos de restauração.

Dependências instaláveis e caches identificados como regeneráveis podem ser descartados, como `node_modules`, dependências Composer, caches do framework e builds regeneráveis. Não aplique exclusões apenas pelo nome de uma pasta sem conferir sua função naquele projeto. Arquivos alterados que justificaram o backup devem ser incluídos mesmo quando estiverem em pastas de build.

Verifique a cópia antes de apagar: abra o arquivo de recuperação, confira a presença dos arquivos selecionados e compare conteúdo/hashes com a origem. Guarde um inventário dos preservados e das categorias descartadas. Nunca imprima `.env`, dumps, tokens, cookies ou conteúdo de documentos privados na conversa.

## Revalidar imediatamente antes da remoção

Para cada candidato:

1. Releia HEAD, branch, estado Git e arquivos locais selecionados. Se houver mudança desde a auditoria/backup, reavalie esse candidato e refaça a preservação necessária antes de prosseguir.
2. Confira que a worktree está registrada no repositório identificado, não é a raiz principal e não está bloqueada/protegida. Respeite worktrees gerenciadas pelo aplicativo: use a ferramenta de arquivamento apropriada quando disponível e aplicável, preservando arquivos ignorados antes; não remova proteções para contorná-la.
3. Reconsulte **todos** os containers e seus mounts. Para um ambiente existente dentro do escopo, confirme os containers exatos que serão parados/removidos, preserve os dados necessários e assegure que nenhum container de outro ambiente dependa da worktree ou de seus volumes. Se o usuário restringiu a limpeza aos ambientes já ausentes, a presença de qualquer container impede a remoção desse candidato. Recursos novos desde a auditoria exigem reavaliação antes de prosseguir.
4. Inspecione volumes, redes e caminhos apontados pelo Compose. Verifique a propriedade exclusiva dos recursos que serão apagados. Um banco local remanescente não é coberto pelo merge do código: preserve seus dados ou obtenha autorização específica para descartá-los. Preserve infraestrutura compartilhada, incluindo Traefik, rede proxy, certificados e DNS.

Quando houver banco em execução, use uma cópia consistente e validada antes de apagar seu volume. A parada dos serviços do próprio ambiente está incluída em um pedido autorizado de `destroy`; organize-a para evitar novas gravações durante a preservação. Não pare serviços de outros ambientes.

## Usar a skill env sem presumir caminhos ou branches

Leia a versão instalada de `scripts/destroy.sh` e seus helpers. No Bezalel,
ela exige `--confirm <projeto>/<ambiente>`, valida o contexto e a propriedade do
estado/volumes, não usa força e não remove imagens. Outras versões podem ter
contratos diferentes. Não substitua o script nem contorne suas proteções.

1. Confirme que o manifesto e o registro `docker-context` apontam para `orbstack`
   e que `project-root` corresponde ao repositório auditado. Se houver divergência
   ou estado legado sem associação verificável, preserve o candidato.
2. Use a pasta da skill env identificada no `SKILL.md` (`$ENV_SKILL_DIR`), a partir do repositório
   confirmado: `bash "$ENV_SKILL_DIR/scripts/destroy.sh" <ambiente>
   --confirm <projeto>/<ambiente> --keep-worktree`. Isso ainda remove volumes;
   só execute após autorização e preservação verificadas. Não altere o manifesto
   para forçar elegibilidade nem remova registros para contornar uma recusa.
3. Remova a worktree apenas pelo caminho real registrado, sem força, depois de
   confirmar que nenhum arquivo necessário será perdido. Se o Git recusar,
   preserve-a e investigue. Não reconstrua caminhos pelo nome do ambiente.
4. Remova apenas a branch local real e o SHA auditado, sem `-D`. Squash/rebase
   podem exigir uma decisão separada quando a remoção segura por Git é recusada.
   Não transforme prova de integração em autorização para descartar dados locais.


## Limpar as imagens correspondentes

O `destroy` do Bezalel não remove imagens. A seleção e remoção de imagens é uma operação separada, explicitamente autorizada. Confira o resultado e remova as restantes elegíveis por referências exatas, inclusive versões antigas sem tag quando sua origem estiver comprovada.

1. Comprove o vínculo ao ambiente removido pelas labels Compose de projeto/serviço, pelos IDs capturados no inventário ou pelas referências exatas do Compose preservado. Não selecione por um prefixo aproximado. Sem evidência de origem, preserve a imagem.
2. Reconsulte todos os containers imediatamente antes da remoção e compare seu campo `Image` com o ID real do candidato. Qualquer container usando esse ID, mesmo parado ou com outro nome/tag, impede a remoção.
3. Confira todas as tags, digests e referências dos demais ambientes. Preserve imagens compartilhadas, bases como MySQL/Redis/Node/PHP, infraestrutura e imagens necessárias a ambientes mantidos, mesmo que atualmente não tenham containers. Uma imagem com alias de outro ambiente não é exclusiva. Não remova imagens referenciadas por um build em andamento.
4. Use `docker --context orbstack image rm <referência-exata>` **sem `--force`**, após revalidar que a tag ainda aponta para o ID auditado. Para imagem sem tag, use o ID completo. Se houver várias tags exclusivas de ambientes elegíveis, remova somente essas tags; confirme depois se o ID também deixou de existir. Não use `image prune -a`, `system prune`, `builder prune` ou exclusão de cache de build como substitutos desta seleção.
5. Se o Docker recusar por uso ou conflito, preserve a imagem e investigue; não pare/remova containers nem force a exclusão para liberar a imagem. Registre os IDs efetivamente removidos e os motivos das preservações.

Para imagens regeneráveis, registre sua origem e receita de build já preservada, sem gerar grandes cópias das próprias imagens por rotina. Uma imagem que seja a única cópia de trabalho ou dados não é descartável com base apenas no merge do repositório.

## Verificação posterior

Confira separadamente:

- Worktree ausente no disco e no registro Git (ou arquivamento gerenciado confirmado).
- Branch local removida quando prevista; nenhuma branch adicional afetada.
- Estado do ambiente e recursos exclusivos removidos conforme o escopo, sem confiar apenas no código de saída de scripts que ocultam erros.
- Containers e volumes exclusivos previstos na remoção ausentes; imagens compartilhadas e infraestrutura permanecem disponíveis.
- IDs das imagens removidas ausentes após a operação; tags e imagens preservadas continuam disponíveis. Registre separadamente casos em que somente uma tag foi removida.
- Containers e worktrees preservados continuam presentes; compare IDs de containers e HEAD/estado das worktrees com o inventário inicial. Mudanças concorrentes devem ser relatadas, não revertidas.
- Recuperação disponível no caminho registrado.

Se uma etapa falhar, inspecione a causa e registre o estado parcial. Não aumente a força ou o alcance da remoção para obter uma mensagem de sucesso. Continue apenas com outros candidatos independentes e seguros.
