# Bezalel para Codex e Claude Code

Bezalel é o plugin; DreamTeam é sua equipe de nove agentes de desenvolvimento.
Pacote gerado. Não edite este cache: altere a fonte e publique uma nova revisão.
Os contratos portáteis ficam em [contracts/README.md](contracts/README.md).
O [modo issue-bot](contracts/issue-bot.md) é adicional: chame a skill ou scripts/issue_bot.py
com uma issue concreta; instalação não inicia sessões. Merge e deploy continuam manuais.
As skills originais são preservadas. Os agentes nativos carregam seus contratos.

## Como adotar o Bezalel em um projeto

Depois de instalar, conecte o projeto com:

```sh
python3 "/caminho/do/plugin/scripts/plugin.py" enable --project "/caminho/do/projeto" --client both
```

Use o caminho realmente instalado mostrado pelo aplicativo. Preencha o contexto do projeto.
Leia o [guia da fonte](https://github.com/rjsandim/bezalel#readme) para instalação,
atualização, confiança nos hooks e limites de suporte.
