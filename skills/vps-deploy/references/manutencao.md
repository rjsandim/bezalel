# Manutenção da skill

Leia somente ao alterar o validador, o modelo de configuração ou o contrato desta
skill. Operar uma VPS com a skill não exige rodar estes testes.

```sh
python3 -B -m unittest discover -s "$SKILL_DIR/tests" -v
```

Os testes usam entradas sintéticas e nenhuma rede. Eles cobrem campos aceitos,
rejeição de segredos e placeholders, links simbólicos e a presença da variável
`COOLIFY_API_TOKEN`. O validador não comprova validade, permissões ou associação
do token ao servidor. A pasta da skill pode ser copiada inteira; ela não depende
de arquivos da raiz do Bezalel.
