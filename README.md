# Bezalel

Preservação local das skills confirmadas pelo usuário em 9 de outubro de 2026.

| Skill | Pasta preservada | Origem |
|---|---|---|
| clean-code | `skills/clean-code/` | `~/.codex/skills/clean-code/` |
| clean-architecture | `skills/clean-architecture/` | `~/.codex/skills/clean-architecture/` |
| env — variante Agents | `skills/env-agents/` | `~/.agents/skills/env/` |
| env — variante Claude | `skills/env-claude/` | `~/.claude/skills/env/` |

São três skills, em quatro pastas, com 89 arquivos úteis. As variantes de `env`
divergem e foram mantidas separadas; nenhuma foi escolhida como canônica.
Os nomes internos, referências e caminhos de instalação foram preservados.
Esta cópia não instala nem ativa as skills.

87 arquivos são idênticos aos originais. Em cada variante de `env`, foi removida
uma linha de comentário de `templates/node.Dockerfile.tpl` que identificava um
projeto interno e uma medição. Não houve mudança de instruções executáveis.
Os originais permanecem intactos.

`inventory.json` registra a proveniência, os tamanhos, as permissões, os hashes
SHA-256 de origem e destino e as duas sanitizações. Para conferir as cópias:

```sh
shasum -a 256 -c SHA256SUMS
```

Metadados do sistema, histórico Git, configurações do IDE, caches, estado de
execução e backups não fazem parte da cópia. Outras skills ficaram fora do
escopo. A proposta de `vps-deploy`, quando presente em `.local-review/`, é local,
ignorada pelo Git e não integra este snapshot.

A revisão procurou credenciais, chaves privadas, autenticação literal e
referências internas. Permaneceram placeholders e dados sintéticos de
desenvolvimento. Nenhum script das skills foi executado. A preservação foi
verificada por hashes e comparação dos arquivos, sem testes de execução.

As referências bibliográficas das skills foram mantidas. Nenhuma licença foi
atribuída nesta etapa. Este registro não reivindica direitos sobre obras citadas.
Nenhum push ou publicação foi feito.
