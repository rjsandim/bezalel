---
name: implementar-snapshots
description: Implementa criação e restauração de snapshots full e tiny em um projeto, com recorte relacional, sanitização, integridade e proteção de destino. Use para construir ou corrigir essa funcionalidade no código; não para executar uma restauração avulsa ou administrar backups de produção.
---

# Implementar snapshots

## Objetivo e escopo

Construa no projeto uma funcionalidade de snapshots reproduzíveis para ambientes
de desenvolvimento e teste. `full` preserva os dados permitidos pela política;
`tiny` reduz o volume sem quebrar os relacionamentos necessários aos fluxos
escolhidos. Ambos obedecem à mesma política de dados sensíveis.

A referência inicial é uma implementação Laravel/MySQL real. Seus mecanismos
úteis e suas limitações estão em [Origem e diferenças](references/origem.md).
Não copie nomes de tabelas, SQL de domínio, credenciais ou infraestrutura da
origem. Snapshot de desenvolvimento não substitui backup de recuperação.

## Entradas e pré-requisitos

- Projeto alvo, instruções do repositório e escopo autorizado de implementação.
- Stack e versões verificadas nos manifests, conexão de origem, destino de
  restauração, storage e isolamento existentes. Descubra pelos arquivos de código
  e configuração pública; não leia dumps ou segredos para entender a feature.
- Migrations, modelos e regras dos fluxos que precisam funcionar no `tiny`.
  Identifique FKs, pivôs, relações sem FK, polimórficas e limites entre tenants.
- Contrato do ENV, quando adotado: `.envstack/stack.yaml`, contexto Docker
  explícito e associação verificável entre projeto, ambiente e recursos locais.
  Consulte a instalação de `env` efetivamente carregada antes de operá-la.
- Ferramentas de teste já disponíveis no projeto. A skill não instala banco,
  cliente, pacote, serviço ou runtime próprio.

## Procedimento

1. **Mapeie o fluxo atual.** Localize comandos, serviços, configuração, scheduler
   e testes pertinentes. Diferencie comportamento existente de requisito novo.
   Registre se o escopo inclui só banco ou também arquivos. Preserve o checkout
   e o trabalho concorrente; não execute criação/restauração para descobrir APIs.
2. **Defina o contrato por projeto.** Use
   [Implementação e configuração](references/implementacao.md). Classifique
   tabelas e colunas, defina recorte, relações, tratamento de anexos, formato,
   compatibilidade e critérios observáveis. Não converta configuração ausente
   em exportação completa. A [configuração Laravel](templates/snapshots.php)
   é um ponto de partida inativo, a adaptar ao schema e às convenções locais.
3. **Prepare proteção e isolamento antes dos efeitos.** Siga
   [Integridade e isolamento](references/seguranca.md). Valide a identidade real
   de origem, destino e storage. `APP_ENV`, um hostname local e `--force` não
   demonstram isolamento. Não restaure no banco corrente por fallback.
4. **Implemente criação e restauração.** Use comandos finos e funções/serviços
   coesos conforme a arquitetura existente. Separe seleção/sanitização de I/O
   para testá-las sem banco. Reaproveite bibliotecas e adaptadores presentes;
   não crie uma plataforma de backups, uma camada por classe ou múltiplos
   engines sem necessidade. Implemente primeiro o banco real do projeto.
5. **Cubra os caminhos de falha.** Adapte os cenários de
   [Validação com fixtures](references/testes.md). Comprove que os bloqueios
   ocorrem antes de qualquer escrita e que uma falha não publica um snapshot
   incompleto nem libera uma base parcialmente restaurada para a aplicação.
6. **Documente e entregue.** Registre comandos efetivamente implementados,
   configuração sem segredos, limites do `tiny`, garantias medidas e recuperação
   após falha. Prepare o agendamento só se solicitado; não o habilite por inferência.

Mudança estrutural de banco segue a aprovação humana anterior à implementação
exigida pelo projeto/Bezalel, vinculada à proposta exata. Primeiro prepare a
proposta revisável. Se a feature não altera o schema da aplicação, registre
“não aplicável”; não invente migração ou tabela de controle só para esta skill.

## Saídas

- Código integrado à estrutura do projeto para criar e restaurar `full`/`tiny`.
- Política versionada de seleção, sanitização e compatibilidade, sem segredos.
- Verificações de arquivo, dados e identidade do destino antes de liberar uso.
- Testes e evidências com fixtures/mocks, instruções operacionais e limites.

Informe separadamente o que foi implementado, o que foi testado com doubles e
o que depende de ensaio real autorizado. Não descreva uma proposta como feature
executada nem um checksum como prova de anonimização.

## Validação

Execute a menor seleção de testes que cubra criação, restore e bloqueios no
ambiente comprovadamente isolado. Nesta skill, os exemplos e o roteiro padrão
usam somente fixtures sintéticas, diretórios temporários e mocks. A fixture
incluída define resultados esperados, não implementa um motor de snapshots.

Para contribuir no Bezalel, execute o checker do repositório e `git diff --check`
na árvore autorizada. Confira links e metadados. Não rode os comandos destrutivos
do projeto como teste da documentação ou do template.

## Limites operacionais

Implementar a feature não autoriza ler produção, baixar snapshots reais,
sobrescrever banco/storage, ligar scheduler, subir infraestrutura, publicar ou
fazer deploy. Antes de uma operação real, identifique alvo, efeitos, preservação
e autorização já dada; se faltar escopo, peça somente a decisão pendente.

Restauração em produção é bloqueada pelo produto, sem bypass. Destino desconhecido
ou divergente também é bloqueado. Uma flag de confirmação pode suprimir a pergunta
interativa, mas não a validação de identidade, integridade ou isolamento.

Não copie estado de outra instalação de ENV. Não altere DNS, CA, proxy ou contexto
Docker global para validar a skill. Mantenha dumps, temporários e configuração
local fora do Git e de relatórios. Falhas permanecem visíveis, sem retries
destrutivos automáticos nem limpeza ampla por prefixo.
