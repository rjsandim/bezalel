# Instruções de contribuição do Bezalel

Este arquivo atende ao pedido de instruções do repositório (`AGENTS.md`). Não
implementa agentes, orquestração, instalações ou integrações com aplicativos.

## Escopo e estrutura

- Trabalhe nesta árvore; não edite as instalações originais fora do Bezalel.
- Cada pasta em `skills/` contém `SKILL.md` com `name`, `description` e, nesta
  ordem: Objetivo e escopo; Entradas e pré-requisitos; Procedimento; Saídas;
  Validação; Limites operacionais. Use português nas instruções e interfaces.
- Referências extensas ficam em `references/`; scripts, templates e testes são
  opcionais conforme a função. Não crie pastas vazias ou runtimes artificiais.
- Caminhos executáveis devem partir da pasta da skill carregada. Não introduza
  caminhos fixos de usuário/agente ou dependências ocultas da raiz do Bezalel.
- Metadados `agents/openai.yaml` são adaptadores opcionais. Não prometa suporte
  de um aplicativo sem validá-lo. Invocação implícita não autoriza efeitos externos.

## Configuração e segurança

- Segredos nunca entram em Git, exemplos, relatórios, chat ou saída de comandos.
  VPS usa `.bezalel/vps-deploy.local.json` por projeto, ignorado, e referência a
  `COOLIFY_API_TOKEN` no ambiente. Não leia/preencha credenciais reais para testar.
- ENV usa `.envstack/stack.yaml`, contexto Docker explícito e base local verificável.
  Não acrescente fallback para contexto ativo, remoção por prefixo ou força.
- Não altere DNS, CA, proxy, containers, volumes, imagens, cofres ou credenciais
  para validar mudanças. Não rode limpeza real, deploy ou integração real sem
  autorização específica. Use fixtures, temporários e mocks de comandos mutáveis.
- Preserve arquivos e configurações preexistentes. Falhas devem resultar em erro
  e estado diagnóstico; nunca as oculte para mostrar sucesso. Relate parcialidade.
- Não faça push, publicação, merge remoto ou exclusão remota por inferência.

## Validação proporcional

- Para toda mudança, execute `python3 -B scripts/check_repository.py` e confira
  `git diff --check`. Após editar arquivos, atualize hashes com
  `python3 -B scripts/check_repository.py --refresh` e revise o diff do inventário.
- Mudanças em ENV: `python3 -B -m unittest discover -s skills/env/tests -v` e
  `bash -n` nos scripts shell alterados. Os testes usam Docker simulado; o CLI
  real só pode ser usado por eles para `compose config`, sem daemon.
- Mudanças em VPS: `python3 -B -m unittest discover -s skills/vps-deploy/tests -v`.
- Mudanças documentais: confira links e comandos descritos; não execute comandos
  destrutivos apenas porque aparecem nos exemplos. Para limpar-orbstack, revise
  também seus cenários em `references/validacao.md` e o contrato atual de ENV.
- Não rode `integration_lifecycle.py` como parte da suíte padrão. Não instale
  ferramentas por conta própria para contornar pré-requisitos ausentes; reporte-os.
- Antes do commit, revise arquivos rastreados, diferenças, credenciais e alvos
  internos; adicione somente arquivos da tarefa. Não enfraqueça testes para obter verde.

## Inventário e entrega

Preserve os hashes/fontes históricas de `inventory.json`; atualize os hashes
atuais quando adaptar arquivos. Registre adições e motivos sem valores privados.
Informe o que mudou, testes executados, limites, commit e eventual bloqueio.
Não descreva presença de token como autenticação ou testes locais como deploy.
