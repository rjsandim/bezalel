---
name: vps-deploy
description: Opera e diagnostica serviços de uma VPS gerenciada pelo Coolify usando configuração por projeto em .bezalel e COOLIFY_API_TOKEN fornecido pelo usuário ao processo. Use para deploy, configuração, DNS, containers e diagnóstico quando o usuário indicar um projeto e uma operação.
---

# VPS Deploy

Use a configuração do projeto que o usuário indicou. Não presuma que projetos
diferentes usam a mesma instância, servidor ou credencial. Esta skill não instala
serviços nem cria acesso persistente ao ser carregada.

## Antes de operar

1. Identifique o diretório absoluto do projeto alvo. Se não estiver claro, peça
   somente o projeto; nunca peça senha, token ou chave pelo chat.
2. Leia [Configuração por projeto](references/configuracao.md). Use exclusivamente
   `<projeto>/.bezalel/vps-deploy.local.json`, sem fallback para configuração global
   ou para a configuração de outro projeto.
3. Se o arquivo ou `COOLIFY_API_TOKEN` estiver ausente, explique ao usuário como
   configurar no próprio ambiente e pare antes de conectar. Não procure tokens
   em outras skills, projetos, arquivos antigos, histórico ou cofres de segredos.
   Não copie, preencha ou gere a credencial por conta própria.
4. Execute a validação local, passando o projeto explicitamente:

   ```sh
   python3 <pasta-desta-skill>/scripts/check_config.py --project <projeto>
   ```

   Ela só lê a configuração e verifica a presença da variável no processo. Não
   acessa rede, autentica, escreve arquivos ou comprova permissões do token.
5. Confirme que o usuário selecionou uma credencial apropriada à instância deste
   projeto. Uma variável presente pode pertencer a outro servidor: nunca conclua
   a associação apenas pela validação local. Ao trocar de projeto, reconfirme.
6. Relacione a operação pedida ao serviço alvo. Não deduza UUIDs ou domínios de
   exemplos. Antes de uma alteração, informe o alvo e o efeito esperado.

## Credenciais e informações internas

- A única referência ao token é `COOLIFY_API_TOKEN`, fornecida pelo usuário ao
  processo da operação. O JSON não aceita campos de senha, token ou chave.
- Não imprima o token, não o coloque no chat, Git, relatórios, arquivos de
  configuração, comandos registrados, URLs, argumentos visíveis ou logs de erro.
- Não habilite tracing de shell ou HTTP. Faça a autenticação pelo mecanismo de
  cabeçalho do cliente escolhido, lendo o valor do ambiente e impedindo sua
  inclusão em logs. Não monte comandos remotos com o token interpolado.
- Se o cliente não permitir usar o segredo sem expô-lo, pare e explique a
  limitação. Não recorra a uma credencial literal encontrada em outra fonte.
- Sanitizar respostas é necessário: logs, env vars, compose e saídas de inspect
  podem conter segredos mesmo quando o pedido é somente de diagnóstico.

## Fluxo de trabalho

### Diagnóstico

Quando houver autorização para acessar a instância, comece por consultas de
somente leitura, limitadas ao serviço solicitado. Confirme versão do Coolify,
identidade do serviço, estado e configuração relevante. Consulte a documentação
compatível com essa versão antes de escolher endpoints ou parâmetros.

Use o painel/API do Coolify como primeira opção. Se SSH for necessário, confirme
o alvo opcional `ssh_target` com o usuário e use somente o acesso que ele já
disponibilizou. Não crie chaves nem configure acesso persistente. Não execute
SSH se esse campo estiver vazio e não deduza um usuário privilegiado.

Mostre apenas os dados mínimos para explicar o diagnóstico. Não despeje
configurações de containers ou respostas integrais com variáveis de ambiente.

### Configuração e deploy

- Faça alterações pelo mecanismo suportado na versão instalada do Coolify.
  Não assuma que reiniciar um container aplica alterações de configuração.
- Após uma alteração autorizada, confira a configuração efetiva e a saúde do
  serviço. Não afirme sucesso só porque uma requisição retornou sem erro.
- Não altere o banco interno via Tinker ou os arquivos gerados pelo Coolify como
  procedimento padrão; isso pode divergir do estado gerenciado. Uma recuperação
  excepcional exige diagnóstico, plano específico e autorização compatível.
- Antes de apagar volumes ou dados, recriar um banco, substituir um domínio ou
  realizar outra operação destrutiva, explique o impacto, confira preservação
  dos dados e obtenha autorização específica. Falha de autenticação no banco
  não é motivo suficiente para apagar um volume.

### DNS, TLS e healthchecks

Cloudflare é opcional, não uma propriedade presumida de todo projeto. Confirme
zona, domínio, destino e política de proxy/TLS antes de qualquer alteração. O
token do Coolify não concede autorização ou acesso ao provedor de DNS.

Investigue healthchecks pela porta, interface e protocolo realmente atendidos.
Não aplique correções de IPv4/IPv6 ou prazos fixos de emissão de certificado sem
evidência no ambiente atual. Verifique o resultado depois de uma mudança.

## Encerramento

Informe o que foi verificado, o que mudou e o que continua pendente, sem valores
sensíveis. Diferencie validação local, autenticação, autorização e saúde do
serviço. Não faça push, publicação ou rotação de credenciais por inferência.

A [proveniência e as diferenças](references/proveniencia.md) documentam a versão
comum, as remoções e as limitações desta preparação.
