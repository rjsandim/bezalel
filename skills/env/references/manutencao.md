# Manutenção da skill

Leia somente ao alterar scripts, templates ou o contrato desta skill. Usar a skill
em um projeto não exige rodar estes testes.

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Os testes criam repositórios descartáveis e simulam Docker e comandos de sistema;
só a validação estática de Compose usa o CLI real, sem daemon. Eles cobrem
geração, ativação aditiva, retomada, preservação, destroy e pools compartilhados.
Incluem allowlist/major PostgreSQL e pgvector, imagem divergente do pool e
init/ensure/update em worktree com manifesto próprio, verificando bytes e mtime
dos arquivos do checkout principal e recusa de estado vinculado a outra raiz.
Também cobrem comandos dentro de worktree gerenciada com/sem `project`, sem
duplicar estado/worktrees nem chamar Docker, avisos para `database_image` em
MySQL/pool e recusa de minor em tags pgvector.

Mudanças nos scripts shell também pedem `bash -n` em cada script alterado.

O roteiro `tests/integration_lifecycle.py` usa containers reais e fica fora da
suíte padrão: rode-o somente com autorização específica, em máquina e dados
descartáveis (iniciar mínimo, acrescentar serviços, parar/retomar e conferir
dados e arquivos).

`test_tailnet.py` simula o Tailscale e usa temporários para o registro global;
cobre concorrência entre processos, idempotência entre cópias, listener/Serve
alheio, conflito, 443 e `/` preservados, geração só-tailnet, placeholders,
preservação de `.env`, stop/ensure/destroy e respostas HTTP/101 simuladas.
Nenhum teste modifica o Serve real, instala LaunchAgent ou usa o daemon Docker.
Os testes de previews/LaunchAgent ficam em `tests/test_preview.py` na raiz do
pacote, inclusive na suíte de distribuição. Piloto real e iPhone são separados.
