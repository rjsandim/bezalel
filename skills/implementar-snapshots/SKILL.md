---
name: implementar-snapshots
description: Implementa no código do projeto a criação e a restauração de snapshots full e tiny para desenvolvimento e teste, com recorte relacional, sanitização de dados sensíveis, verificação de integridade e proteção do destino. Use quando o pedido for "cria um comando de snapshot do banco", "quero um dump tiny anonimizado para dev", "o restore está quebrando FKs", "corrige o snapshot que vaza dados pessoais". Não use para rodar uma restauração avulsa, baixar snapshot real ou administrar backups de produção; para subir o ambiente onde restaurar, use env.
---

# Implementar snapshots

## Objetivo e escopo

Construir no projeto uma funcionalidade de snapshots reproduzíveis para
ambientes de desenvolvimento e teste. `full` preserva os dados permitidos pela
política; `tiny` reduz o volume mantendo os relacionamentos necessários aos
fluxos escolhidos. Ambos obedecem à mesma política de dados sensíveis.
Snapshot de desenvolvimento é diferente de backup de recuperação.

O núcleo independe de linguagem e framework: adapte interfaces, formato,
configuração e testes ao stack real. A implementação Laravel/MySQL que inspirou a
skill está descrita em [Origem e diferenças](references/origem.md), como
conceitos a reaproveitar, e o [exemplo Laravel](references/exemplo-laravel.md)
só interessa quando esse for o stack.

## Entradas e pré-requisitos

- Projeto alvo, instruções do repositório e escopo autorizado de implementação.
- Stack e versões dos manifests, conexão de origem, destino de restauração,
  storage e isolamento existentes, lidos no código e na configuração pública
  (dumps e segredos ficam fora da leitura).
- Migrations, modelos e regras dos fluxos que precisam funcionar no `tiny`:
  FKs, pivôs, relações sem FK, polimórficas e limites entre tenants.
- Quando o projeto usa a skill env: `.envstack/stack.yaml`, contexto Docker
  explícito e associação verificável entre projeto, ambiente e recursos locais.
- Ferramentas de teste já disponíveis; a skill não instala banco, cliente,
  pacote, serviço ou runtime.

## Procedimento

1. **Mapeie o fluxo atual.** Localize comandos, serviços, configuração,
   scheduler e testes pertinentes. Separe comportamento existente de requisito
   novo e registre se o escopo inclui só banco ou também arquivos. Descubra as
   APIs lendo código, sem executar criação ou restauração.
2. **Defina o contrato do projeto** com [Implementação e configuração](references/implementacao.md):
   classifique tabelas e colunas e defina recorte, relações, anexos, formato,
   compatibilidade e critérios observáveis. Configuração ausente significa
   bloqueio, não exportação completa. O [modelo de política](templates/snapshot-policy.example.json)
   ilustra as decisões; formato, nomes e loader seguem as convenções locais.
3. **Trate mudança de banco antes de implementar.** Se a feature exigir tabela,
   coluna, índice ou qualquer migration (inclusive tabela de controle), prepare
   a proposta revisável com a skill proposta-banco e aguarde a aprovação humana
   da versão exata antes de escrever a migration ou o código que depende dela.
   Se o schema da aplicação não muda, registre "não aplicável" e siga.
4. **Prepare proteção e isolamento antes dos efeitos**, conforme
   [Integridade e isolamento](references/seguranca.md). Valide a identidade real
   de origem, destino e storage; rótulo de ambiente, hostname local ou flag de
   força não demonstram isolamento. Restaurar no banco corrente por fallback
   está fora de questão.
5. **Implemente criação e restauração** com pontos de entrada pequenos e
   serviços coesos na arquitetura existente. Separe seleção/sanitização do I/O
   para testá-las sem banco. Reaproveite bibliotecas e adaptadores presentes e
   comece pelo banco real do projeto, sem plataforma genérica de backups.
6. **Cubra os caminhos de falha** adaptando os cenários de
   [Validação com fixtures](references/testes.md): bloqueios antes de qualquer
   escrita, snapshot incompleto nunca publicado e base parcialmente restaurada
   mantida longe da aplicação.
7. **Documente e entregue** comandos implementados, configuração sem segredos,
   limites do `tiny`, garantias medidas e recuperação após falha. Agendamento só
   quando pedido.

## Saídas

- Código integrado ao projeto para criar e restaurar `full` e `tiny`.
- Política versionada de seleção, sanitização e compatibilidade, sem segredos.
- Verificações de arquivo, dados e identidade do destino antes de liberar uso.
- Testes com fixtures e mocks, instruções operacionais e limites.
- Relato separando o que foi implementado, o que foi testado com doubles e o que
  depende de ensaio real autorizado. Checksum prova integridade, não anonimização.

## Validação

Antes de entregar, confira o próprio trabalho:

- A menor seleção de testes do projeto que cobre criação, restore e bloqueios
  passa, com fixtures sintéticas, diretórios temporários e mocks.
- Os testes de falha mostram o bloqueio antes de qualquer escrita (destino
  desconhecido, produção, artefato corrompido).
- No `tiny` gerado pela fixture relacional, todo filho retido tem seu pai e a
  verificação de órfãos passa; colunas sensíveis saem transformadas no arquivo.
- A decisão do passo 3 está registrada: aprovação da proposta de banco ou "não aplicável".

Manutenção da própria skill: [manutenção](references/manutencao.md).

## Limites operacionais

Siga as regras do projeto e os limites do papel. Implementar a feature não
autoriza ler produção, baixar snapshots reais, sobrescrever banco ou storage,
ligar scheduler, subir infraestrutura, publicar ou fazer deploy. Antes de uma
operação real, identifique alvo, efeitos, preservação e autorização já dada e
peça só a decisão que faltar.

Restauração em produção é bloqueada pelo produto, sem bypass; destino
desconhecido ou divergente também. Uma flag de confirmação pode dispensar a
pergunta interativa, nunca a validação de identidade, integridade ou isolamento.
Dumps, temporários e configuração local ficam fora do Git e dos relatórios.
Falhas ficam visíveis, sem retries destrutivos automáticos nem limpeza por prefixo.
