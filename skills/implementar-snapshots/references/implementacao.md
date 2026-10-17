# Implementação e configuração

## Decisões antes do código

Use a linguagem, o framework, o banco e as convenções presentes no projeto.
Exponha criação e restauração pelo mecanismo apropriado: comando, serviço de
aplicação, tarefa administrativa ou API com autorização. Não é necessário criar
todos esses pontos de entrada. Separe seleção/sanitização dos efeitos de leitura,
gravação e publicação para testar as regras sem infraestrutura real. Reaproveite
conexões, storage, relógio, logger e locks existentes. Só introduza contratos
onde resolvam uma fronteira concreta; não crie um runtime universal de snapshots.

Leia as instruções e versões do projeto antes de escolher APIs ou ferramentas.
O [modelo de política](../templates/snapshot-policy.example.json) é uma referência
de decisões, não um schema obrigatório nem uma feature pronta. Traduza as regras
para a configuração idiomática do projeto e implemente seus consumidores e
validações. Não crie parser/loader só para preservar esse JSON. Não execute código
ou configuração recebidos de um snapshot. Para um projeto Laravel já existente,
consulte apenas se necessário o [exemplo opcional](exemplo-laravel.md).

| Decisão | Contrato a implementar |
|---|---|
| Origem | Recurso/conexão explícitos e acesso somente de leitura para exportação; sem fallback para o banco corrente. Engine/versão e capacidades suportadas. |
| Conteúdo `full` | Todos os dados classificados como permitidos, inclusive das tabelas que serão recortadas apenas no `tiny`; tabelas operacionais/sensíveis só com estrutura. |
| Conteúdo `tiny` | Sementes recentes/de domínio e relações necessárias, com limites de volume; pode incluir pais mais antigos que a janela. |
| Tabela nova | Falhar até classificação explícita, para impedir vazamento silencioso. Listas sobrepostas, tabela/coluna desconhecida ou política sem versão também falham. |
| Datas | Dias positivos dentro de limite do projeto, instante de corte único, fuso e limite inclusivo documentados. Sem coluna ou com data nula: política explícita, inicialmente erro. |
| Storage | Disco privado configurado, namespace por projeto/origem/tipo/execução e credenciais resolvidas pelo ambiente sem entrar em logs. |
| Sanitização | Política versionada de colunas, JSON e relações; aplicada em ambos os modos antes de persistir qualquer payload exportado. |
| Arquivos | `exclude`, fixtures substitutas ou cópia seletiva autorizada. Declare o efeito sobre URLs, anexos, downloads e telas. |
| Restore | Alvo explícito, identidade verificada, isolamento, arquivo confiável, compatibilidade e recuperação de falha. |

Não converta `--days=0`, texto inválido ou negativo em um valor default. Se o
projeto permitir exportar inteira uma tabela sem data, a opção precisa ser
explícita na política e constar do plano/manifesto; não é fallback silencioso.

## Seleção relacional do `tiny`

Descubra dependências pelas migrations, relações dos modelos e regras do fluxo.
FKs cobrem apenas parte do domínio. Se houver relações polimórficas, identificadores
em JSON, pivôs ou FKs compostas, modele-as explicitamente. Evite gerar um catálogo
de toda a organização: mantenha apenas o mapa necessário a esse projeto.

1. Congele o instante de corte e a política. Selecione as sementes recentes ou
   entidades do cenário autorizado; respeite o filtro de tenant quando existir.
2. Inclua os pais necessários de cada linha selecionada. Repita até estabilizar
   os conjuntos de chaves, deduplicando para terminar mesmo com ciclos.
3. Inclua filhos/pivôs somente quando o fluxo exigir, com regra explícita.
   Exemplo genérico: um pedido selecionado pode exigir todos os seus itens,
   inclusive antigos. Não percorra indiscriminadamente os dois sentidos.
4. Se a relação exigir pai de outro tenant, dados excluídos pela política ou
   acesso não permitido, interrompa e resolva o contrato. Não amplie o escopo,
   invente pai, remova a FK ou converta campos obrigatórios em nulos.
5. Aplique teto de linhas/bytes/tempo definido pelo projeto. Fechamento que
   excede o teto falha com diagnóstico; truncar arbitrariamente quebra relações.
6. Verifique ausência de órfãos e invariantes relevantes. Pai necessário numa
   tabela `schema_only` é conflito da política, não motivo para copiar seus dados.

Carregar pais antigos é deliberado: `tiny` representa uma amostra funcional,
não a promessa de que toda linha terá data dentro da janela. Se não houver ganho
significativo de volume, relate e ajuste as sementes com o usuário.

## Sanitização antes da gravação

Classifique nomes, e-mails, telefones, documentos, endereços, texto livre, dados
de pagamento, tokens, cookies, URLs assinadas, chaves de integração e blobs/JSON.
Escolha por campo entre remover, substituir ou manter por necessidade justificada.
Pseudonimização não deve ser descrita como anonimização comprovada.

Preserve tipo, nulabilidade, unicidade e coerência entre referências. Exemplo:
identidades artificiais como `user-42@example.invalid`, derivadas de uma chave
sintética estável dentro do snapshot. Se a estabilidade exigir um segredo de
mapeamento, forneça-o em runtime e não o exporte. Mantenha IDs/chaves relacionais
quando permitidos ou remapeie todas as referências coerentemente.

Remova sessões/tokens; desative integrações e remova seus segredos, não apenas
a coluna de modo. Para autenticação local, prefira bloquear contas importadas e
criar uma conta de fixture por fluxo local explícito. Se senha de teste for
necessária, receba-a somente no ambiente de teste e gere o hash antes de exportar.
Não forneça uma senha universal no template.

Nunca grave primeiro dados reais no dump para “corrigir no final”. Faça a
transformação em memória/stream. Inspecione o artefato sintético descomprimido nos
testes e prove que os marcadores proibidos não estão presentes. A política precisa
cobrir valores em metadados, DDL/defaults, mensagens de erro e anexos, além das linhas.

## Criação

Fluxo sugerido, adaptável ao stack:

1. Validar configuração, origem, política e capacidade do formato; obter lock
   identificado por projeto/origem. O comando manual usa a mesma proteção que o
   scheduler. Janela opcional deve tratar fuso e passagem pela meia-noite.
2. Abrir visão consistente de dados e capturar versão de schema. No MySQL,
   verificar engine transacional, alterações concorrentes de DDL e diferenças
   entre a conexão de metadata e a de streaming. Se a consistência não puder ser
   sustentada, falhar ou exigir uma estratégia aprovada para essa origem.
3. Selecionar/sanitizar em lotes. Não carregar tabelas inteiras em memória nem
   executar consultas aninhadas incompatíveis com o cursor/driver em uso.
   Calcular dependências e contagens na mesma visão consistente; evitar N+1 por linha.
4. Gravar em arquivo exclusivo e privado, com caminho gerado pelo programa.
   Contar bytes antes de adicionar a próxima linha ao statement, incluindo
   cabeçalho e delimitadores; linha maior que o limite gera erro explícito.
5. Fechar o stream, verificar retornos de escrita, calcular hash/tamanhos e
   validar completude. Falhas de disco, compressão ou upload deixam saída não pronta.
6. Publicar em chave nova por execução, verificar o upload e só então tornar
   a versão elegível para restore. Um ponteiro “latest” é opcional; deve apontar
   apenas para uma versão completa e validada. Nunca sobrescrever o último bom
   como primeira etapa nem presumir rename atômico em todo storage.
7. Liberar lock, cursores e temporários em `finally`, preservando diagnóstico
   sem dados pessoais. Não ocultar falhas de limpeza nem remover arquivos alheios.

Não transportar DDL para views, triggers, rotinas ou eventos incidentalmente.
Declare suporte e testes específicos quando o projeto precisar desses objetos.
Credenciais, privilégios, replicação e tabelas de sistema ficam fora do artefato.

## Formato e manifesto

Prefira uma biblioteca/formato já existente que tenha leitura incremental,
limites, escaping e teste de round-trip. Se implementar SQL próprio, não use
`split(';')` nem uma linha marcadora que possa ocorrer em valores. Um formato
versionado com frames de comprimento explícito é uma alternativa pequena;
teste newline, aspas, barras, NUL, Unicode, bytes binários e marcador literal.
Qualquer adaptador precisa tratar campos binários, colunas geradas e charset
explicitamente; converter todos os valores para strings não comprova fidelidade.

O manifesto acompanha a execução e contém apenas metadados necessários:

- versão do formato, ID da execução, ID público do projeto e alias da origem;
- modo, instante/fuso de corte, versão de sanitização e versão de schema/migrations;
- engine/versão compatível, objetos incluídos, contagens esperadas após sanitização;
- nomes relativos dos payloads, tamanhos comprimidos/descomprimidos e SHA-256;
- declaração de tratamento dos arquivos da aplicação e conclusão da exportação.

Não inclua DSN, hostname privado, segredo, amostras reais ou hash de valores
pessoais. O manifesto deve ser validado por schema e limites antes de seus campos
serem usados como caminhos. Hash prova correspondência de bytes; autenticidade
depende da origem confiável e do controle de escrita, ou assinatura quando exigida.

## Contrato independente de interface

Implemente os comportamentos abaixo na interface escolhida. Os nomes são
conceituais e não prescrevem assinatura, comando, linguagem ou biblioteca:

```text
criar(modo, origem, política, apenas_planejar) -> artefato e manifesto
restaurar(artefato, destino, identidade_esperada, apenas_planejar) -> resultado validado
```

O modo de planejamento resolve o plano e os bloqueios sem DDL/DML, upload, limpeza, abertura
de writers, alteração de config ou consumo de filas; pode usar apenas metadata
explicitamente autorizada. Um mecanismo de confirmação não interativa suprime
somente a pergunta, nunca as validações ou a autorização necessária à operação.

Os destinos permitidos no modelo começam vazios. Cada alvo cadastrado pelo projeto
aponta um recurso existente, ambiente permitido e identidade esperada.
As credenciais continuam no mecanismo de configuração local já usado.
O código deve verificar a identidade observada da conexão antes de executar o
primeiro efeito; configurar uma allowlist não prova que ela corresponde ao servidor.

Antes de habilitar a funcionalidade, implemente e teste todos os consumidores usados:
um booleano de proteção sem efeito no código é uma falsa garantia. Não ative
agendamento automaticamente; se solicitado, use origem e namespace exclusivos,
lock no serviço e falha observável. Não rode testes apontando para o banco padrão.
