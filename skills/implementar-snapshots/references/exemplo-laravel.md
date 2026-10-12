# Exemplo opcional: projeto Laravel

Leia esta referência somente quando Laravel já for o stack do projeto alvo.
Ela ilustra uma adaptação; nenhuma dependência PHP, comando Artisan, estrutura
de pastas ou configuração abaixo é obrigatória para usar a skill em outro stack.
A origem Laravel/MySQL da inspiração está em [Origem e diferenças](origem.md).

## Adaptação possível

Dois comandos Artisan finos podem encaminhar criação e restauração para funções
ou serviços da aplicação. Uma configuração convencional, como
`config/snapshots.php`, pode guardar a política adaptada do
[modelo conceitual](../templates/snapshot-policy.example.json). Não copie nomes de
tabelas de outro projeto nem crie um loader JSON adicional sem necessidade.

Contrato ilustrativo, a implementar e documentar conforme a versão do projeto:

```text
snapshot:create {full|tiny} --source=<alias> [--days=<n>] [--dry-run]
snapshot:restore {snapshot-id} --target=<alias> --expect-target=<identidade> [--dry-run] [--yes]
```

Esses comandos não passam a existir pela instalação da skill. `--dry-run` não
abre writers nem executa DDL/DML; `--yes` só suprime a pergunta interativa. Toda
proteção de origem/destino e artefato continua obrigatória no consumidor.

Reaproveite conexões nomeadas, storage privado, locks e mecanismo de configuração
existentes. Não use a conexão default como fallback para restore. Verifique a
configuração efetiva, inclusive cache, URL de conexão e driver. Segredos ficam
no mecanismo local do projeto, sem valores no template ou nos logs.

Se usar PDO/MySQL, trate streaming, cursores abertos, binários, colunas geradas,
escaping e limites de bytes. Não copie o delimitador textual ou a sanitização
tardia da implementação de origem. Um dump nativo também precisa cumprir a
política de sanitização antes de produzir qualquer artefato persistido.

## Testes e sintaxe

Use o runner já adotado pelo projeto, com fixtures e doubles de banco/storage.
Não faça bootstrap do projeto real apenas para validar documentação. Nenhum
teste padrão desta skill chama Artisan ou conecta a banco.

Se forem criados arquivos PHP no projeto alvo, valide-os com o linter/runner
compatível e já disponível. `php -l` é uma opção somente quando `php` for um
binário utilizável sem iniciar serviços. Não instale PHP nem acione Docker ou
OrbStack para satisfazer um gate desta referência. Se indisponível, reporte a
checagem não executada; isso não estabelece uma exigência PHP para outros stacks.
