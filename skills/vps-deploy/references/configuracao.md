# Configuração por projeto

Cada projeto mantém seu próprio arquivo `.bezalel/vps-deploy.local.json`.
Não há configuração global, servidor padrão compartilhado nem token persistido
pelo Bezalel. `--project` é obrigatório no validador; o diretório de trabalho do
terminal não escolhe implicitamente o destino.

O [modelo versionado](../templates/vps-deploy.example.json) acompanha esta skill,
em `templates/vps-deploy.example.json`. Ele contém somente um domínio reservado e uma opção vazia;
não é uma configuração válida para operar.

## Preparação pelo usuário

1. No projeto alvo, copie o modelo para `.bezalel/vps-deploy.local.json` apenas
   se esse arquivo ainda não existir. Preserve configurações existentes.
2. Inclua `.bezalel/vps-deploy.local.json` no ignore daquele projeto. Copie também
   `templates/project.gitignore` da skill como `.bezalel/.gitignore`, ou acrescente
   sua regra sem sobrescrever regras existentes. Confirme com
   `git check-ignore .bezalel/vps-deploy.local.json` antes de preencher valores.
3. Edite localmente a URL da instância; preencha `ssh_target` apenas se precisar
   de SSH e já tiver o acesso autorizado. Restrinja a leitura do arquivo a seu
   usuário, por exemplo com `chmod 600 .bezalel/vps-deploy.local.json`.
4. Disponibilize `COOLIFY_API_TOKEN` somente ao processo que fará a operação,
   preferencialmente por um gerenciador de segredos que você controla. Não
   coloque o valor no JSON, modelo, Git, chat ou linha de comando registrada.
   O Bezalel não lê o Keychain automaticamente nem configura o seu shell.
5. Confirme que a credencial selecionada pertence à instância deste projeto.
   Ao trocar de projeto, selecione novamente a credencial apropriada; não
   reutilize a variável herdada sem conferir a associação.

Esta preparação é feita pelo próprio usuário. A criação de um modelo ou a
presença de um token não autoriza uma operação remota.

## Campos aceitos

| Campo | Uso |
|---|---|
| `coolify_base_url` | URL da instância, sem usuário, senha, query string ou fragmento. Use HTTPS. HTTP só é aceito em loopback, por exemplo para um acesso local já preparado pelo usuário. |
| `ssh_target` | Opcional; alias SSH ou `usuario@host`, sem opções ou comandos. Vazio significa que SSH não foi configurado. Não cria conexão nem acesso. |

Campos adicionais são rejeitados para evitar persistência acidental de tokens
ou opções sem contrato. Endereços de exemplo e placeholders também são
rejeitados. Configurações locais por symlink não são aceitas, para evitar que
dois projetos usem o mesmo arquivo sem que isso fique explícito.

## Validação local

```sh
python3 <pasta-da-skill>/scripts/check_config.py --project <caminho-do-projeto>
```

Requer Python 3.9 ou superior, sem dependências externas. O comando apenas lê o
arquivo daquele projeto, verifica seus campos e a presença não vazia de
`COOLIFY_API_TOKEN`. Não imprime URLs, alvos SSH ou conteúdo de variáveis. Não
faz requisições, não verifica validade do token, não testa SSH e não altera
arquivos ou ambiente. Uma falha produz mensagem genérica sem ecoar a entrada.
