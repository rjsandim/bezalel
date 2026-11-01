# Manutenção da skill

Leia somente ao alterar scripts, templates ou o contrato desta skill. Usar a skill
em um projeto não exige rodar estes testes.

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Os testes criam repositórios descartáveis e simulam Docker e comandos de sistema;
só a validação estática de Compose usa o CLI real, sem daemon. Eles cobrem
geração, ativação aditiva, retomada, preservação, destroy e pools compartilhados.

Mudanças nos scripts shell também pedem `bash -n` em cada script alterado.

O roteiro `tests/integration_lifecycle.py` usa containers reais e fica fora da
suíte padrão: rode-o somente com autorização específica, em máquina e dados
descartáveis (iniciar mínimo, acrescentar serviços, parar/retomar e conferir
dados e arquivos).
