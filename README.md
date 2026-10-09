# Bezalel

Preservação das skills pessoais confirmadas pelo usuário.

| Skill | Pasta | Origem |
|---|---|---|
| clean-code | `skills/clean-code/` | `~/.codex/skills/clean-code/` |
| clean-architecture | `skills/clean-architecture/` | `~/.codex/skills/clean-architecture/` |
| env | `skills/env/` | `~/.agents/skills/env/` |
| vps-deploy | `skills/vps-deploy/` | Adaptação comum das variantes locais Agents e Claude |

A versão mais recente de `env`, proveniente de Agents, foi escolhida pelo usuário
como a única cópia no repositório. A duplicata Claude foi removida desta árvore;
continua recuperável no commit `75e65c4be946a3ae8d6ea003db0bcc6000e3ecde`.
Os originais externos em `.agents` e `.claude` não foram alterados.

O snapshot das três primeiras skills preserva 57 arquivos úteis: 56 idênticos aos originais e um com a remoção de uma linha
de comentário que continha uma referência interna e uma medição, em
`skills/env/templates/node.Dockerfile.tpl`. Nenhuma instrução executável mudou.
Os caminhos internos de instalação foram preservados; este repositório não
instala ou ativa as skills nem certifica compatibilidade com ferramentas.

`inventory.json` registra proveniência, permissões, tamanhos, hashes de origem e
destino e a sanitização. Confira as cópias com:

```sh
shasum -a 256 -c SHA256SUMS
```

Metadados do sistema, histórico Git, configurações do IDE, caches, estado de
execução e backups não foram copiados. Os scripts das três skills preservadas não foram executados para validar
funcionamento. A revisão desse conjunto encontrou apenas placeholders e dados
sintéticos de desenvolvimento.

As propostas antigas de `vps-deploy` em `.local-review/` estão ignoradas pelo Git.
As referências bibliográficas foram mantidas, sem atribuir uma nova licença ou
reivindicar direitos sobre obras citadas. Nenhum push foi feito.

## VPS Deploy por projeto

A versão comum usa `<projeto>/.bezalel/vps-deploy.local.json`, sem configuração
global ou destino herdado de outro projeto. O modelo versionado é
[.bezalel/vps-deploy.example.json](.bezalel/vps-deploy.example.json).
O arquivo local é ignorado por [.bezalel/.gitignore](.bezalel/.gitignore) e não
foi criado nem preenchido. Ao usar em outro projeto, leve também essa regra de
ignore antes de configurar os valores locais.

O token é somente referenciado por `COOLIFY_API_TOKEN`. O usuário deve fornecê-lo
pelo próprio ambiente/gerenciador de segredos para a operação e confirmar que
corresponde à instância daquele projeto. Nunca envie o valor no chat ou o grave
no JSON. Consulte a [configuração](skills/vps-deploy/references/configuracao.md)
e as [diferenças entre as variantes](skills/vps-deploy/references/proveniencia.md).

O validador exige o diretório do projeto, verifica o formato da configuração e
a presença do token, sem executar operações remotas:

```sh
python3 skills/vps-deploy/scripts/check_config.py --project <projeto>
```

Dez testes locais com entradas sintéticas cobrem isolamento por projeto,
configuração inválida, campos indevidos de credenciais, mensagens sem valores,
symlinks e ausência de conexão de rede. Para reproduzir:

```sh
python3 -B -m unittest discover -s skills/vps-deploy/tests -v
```

Nenhuma autenticação, configuração de acesso persistente, rotação, operação de
VPS ou publicação foi feita. Presença de token não comprova validade, permissões
ou associação ao servidor. A configuração real continua a cargo do usuário.
