---
name: vps-deploy
description: Opera e diagnostica serviços de uma VPS gerenciada pelo Coolify com configuração por projeto em .bezalel/vps-deploy.local.json e COOLIFY_API_TOKEN fornecido pelo usuário ao processo. Use quando o pedido for "faz o redeploy do serviço X", "troca a variável de ambiente Y no Coolify", "por que o container está reiniciando?", "o healthcheck está falhando", "aponta o domínio para esse serviço" e o usuário indicar projeto e operação. Para ambientes locais de desenvolvimento, use env; para limpar ambientes locais, use limpar-orbstack. É de invocação explícita e cada operação remota precisa de autorização própria.
---

# VPS Deploy

## Objetivo e escopo

Operar e diagnosticar serviços no Coolify do projeto indicado pelo usuário: ler
estado, alterar configuração, fazer redeploy e conferir a saúde do serviço. Cada
projeto tem a própria instância, servidor e credencial; a skill não instala
serviços nem cria acesso persistente.

## Entradas e pré-requisitos

- Diretório absoluto do projeto alvo e a operação pedida (serviço, variável,
  domínio ou sintoma).
- `<projeto>/.bezalel/vps-deploy.local.json`, criado pelo usuário a partir de
  `templates/vps-deploy.example.json` conforme [configuração por projeto](references/configuracao.md).
- `COOLIFY_API_TOKEN` da instância correta, disponível só no processo da operação.
- `$SKILL_DIR`: pasta desta skill na instalação carregada; Python 3.9+, `curl` e `jq`.

## Procedimento

### Preparar

1. **Identifique o projeto.** Se não estiver claro, pergunte só o projeto; senha,
   token ou chave nunca são pedidos pelo chat.
2. **Valide a configuração local:**

   ```sh
   python3 "$SKILL_DIR/scripts/check_config.py" --project <projeto>
   ```

   Ela lê o JSON e confere que o token existe no processo, sem rede. Se faltar
   arquivo ou token, explique ao usuário como configurar no ambiente dele e pare.
   Tokens de outras skills, projetos, históricos ou cofres não são alternativa.
3. **Confirme a associação** entre a credencial e a instância deste projeto com o
   usuário; reconfirme ao trocar de projeto.
4. **Prepare a chamada sem expor o token**, enviando o cabeçalho por stdin:

   ```sh
   BASE="$(jq -r .coolify_base_url <projeto>/.bezalel/vps-deploy.local.json)"
   coolify() { printf 'header = "Authorization: Bearer %s"\n' "$COOLIFY_API_TOKEN" | curl -sS --fail-with-body --config - "$@"; }
   ```

   Sem tracing de shell ou HTTP. Se o cliente disponível não permitir isso, pare
   e explique a limitação.

### Operar

Os caminhos abaixo são da API v4 do Coolify e servem de **exemplo**: confirme
endpoints, parâmetros e nomes de campos na documentação da versão instalada
(passo 5) antes de usá-los.

5. **Leia versão e estado (somente leitura):** `coolify "$BASE/api/v1/version"`;
   localize o serviço pelo nome em `coolify "$BASE/api/v1/applications" | jq '.[] | {uuid, name, status, fqdn}'`
   e confira com o usuário o UUID alvo. UUIDs e domínios nunca vêm de exemplos.
6. **Leia as variáveis mascaradas:** `coolify "$BASE/api/v1/applications/<uuid>/envs" | jq '[.[] | {key, is_build_time}]'`.
   Mostre só as chaves e flags; valores, logs, compose e saídas de inspect podem
   conter segredos.
7. **Antes de alterar, informe alvo, mudança e efeito esperado** (inclusive se o
   serviço reinicia) e obtenha a autorização dessa operação.
8. **Altere a variável** pelo mecanismo da versão instalada, por exemplo
   `PATCH /api/v1/applications/<uuid>/envs` com o corpo JSON enviado por stdin
   (`--data @-`), para o valor também ficar fora dos argumentos. Reinício de
   container sozinho pode não aplicar configuração; use o redeploy da versão.
9. **Faça o redeploy**, por exemplo `coolify "$BASE/api/v1/deploy?uuid=<uuid>"`,
   e acompanhe o deployment retornado até um estado final.
10. **Verifique a saúde** (veja Validação) antes de relatar sucesso.

### Diagnosticar

Comece pelos passos 5–6 e pelos logs do deployment, limitados ao serviço pedido.
Investigue healthchecks pela porta, interface e protocolo realmente atendidos;
correções de IPv4/IPv6 ou prazos de certificado só com evidência do ambiente
atual. SSH é segunda opção: use somente o `ssh_target` configurado, confirmado
com o usuário e já autorizado, sem criar chaves nem deduzir usuário privilegiado.

### DNS e TLS

Cloudflare ou outro provedor de DNS é opcional por projeto. Confirme zona,
domínio, destino e política de proxy/TLS antes de alterar; o token do Coolify
não dá acesso ao provedor de DNS.

## Saídas

Relato do que foi verificado, do que mudou e do que continua pendente, sem
valores sensíveis. Separe validação local, autenticação, autorização e saúde do
serviço. A [proveniência e as diferenças](references/proveniencia.md) documentam
a versão comum, as remoções e as limitações desta preparação.

## Validação

Antes de relatar, confira o resultado da própria operação:

- A leitura posterior das variáveis mostra a chave alterada com o valor esperado
  (comparado sem imprimi-lo, por exemplo com `jq` retornando `true`/`false`).
- O deployment terminou com sucesso no estado retornado pela API.
- O serviço está saudável no Coolify e a URL ou o healthcheck responde com o
  status esperado (`curl -sS -o /dev/null -w '%{http_code}' <url>`).
- Os logs recentes do serviço não mostram erro novo relacionado à mudança.

Resposta HTTP sem erro, sozinha, não prova sucesso. Comandos de teste da própria
skill ficam em [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. O token aparece somente como
`COOLIFY_API_TOKEN` no processo: fora do chat, Git, relatórios, arquivos, URLs,
argumentos visíveis e logs. A configuração aceita apenas os campos documentados.

Banco interno do Coolify (Tinker) e arquivos gerados por ele ficam fora do
procedimento padrão; uma recuperação excepcional exige diagnóstico, plano e
autorização específicos. Apagar volumes ou dados, recriar banco ou substituir
domínio exige explicar o impacto, conferir a preservação dos dados e obter
autorização específica; falha de autenticação no banco não justifica apagar um
volume. Push, publicação e rotação de credenciais acontecem só quando pedidos.
