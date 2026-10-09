# Bezalel

Preservação das skills pessoais confirmadas pelo usuário.

| Skill | Pasta | Origem |
|---|---|---|
| clean-code | `skills/clean-code/` | `~/.codex/skills/clean-code/` |
| clean-architecture | `skills/clean-architecture/` | `~/.codex/skills/clean-architecture/` |
| env | `skills/env/` | `~/.agents/skills/env/` |

A versão mais recente de `env`, proveniente de Agents, foi escolhida pelo usuário
como a única cópia no repositório. A duplicata Claude foi removida desta árvore;
continua recuperável no commit `75e65c4be946a3ae8d6ea003db0bcc6000e3ecde`.
Os originais externos em `.agents` e `.claude` não foram alterados.

São 57 arquivos úteis: 56 idênticos aos originais e um com a remoção de uma linha
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
execução e backups não foram copiados. Nenhum script das skills foi executado
para validar funcionamento. A revisão encontrou apenas placeholders e dados
sintéticos de desenvolvimento no conjunto preservado.

As propostas antigas de `vps-deploy` em `.local-review/` estão ignoradas pelo Git.
As referências bibliográficas foram mantidas, sem atribuir uma nova licença ou
reivindicar direitos sobre obras citadas. Nenhum push foi feito.
