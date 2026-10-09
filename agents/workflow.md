# Fluxo por user story

## 1. Preparar e validar o isolamento

Confirme projeto, história, responsável integrado e alvo de execução. Antes de
implementar ou executar testes mutáveis, evidencie isolamento de **arquivos,
banco, filas, portas e storage**. Para cada dimensão, registre verificação e
referência da evidência, ou `not_applicable` com razão concreta. Container ou
worktree, isoladamente, não comprovam isolamento das demais dimensões.

A skill ENV pode preparar parte do ambiente; o responsável ainda precisa
confrontar o que o aplicativo realmente usa. Um banco em outro host, uma fila
compartilhada ou uploads fora do diretório local continuam exigindo análise.
Configuração ausente, alvo incerto ou acesso insuficiente bloqueiam a ação
correspondente. Não reutilize produção como fixture.

## 2. Analisar a história e os impactos

Leia necessidade, critérios, dependências e regras específicas do projeto.
Selecione somente os papéis necessários. O coordenador identifica alterações de
contratos API/web/mobile, versões consumidoras, migração de dados, integração e
riscos. Produto aponta desvios de visão; o usuário decide mudança de requisito.

Use responsabilidades claras: consultas por responsabilidade, contratos e
fachadas quando reduzirem acoplamento. No caso de um professor, uma fachada pode
compor avaliações, materiais e contato através de interfaces próprias; não deve
concentrar todos os SQLs e regras desses módulos num arquivo gigante. Não crie
uma fachada, camada ou abstração sem dificuldade concreta que ela resolva.
Clean-code e clean-architecture não autorizam refatorar fora da história.

## 3. Propor e aprovar mudanças estruturais de banco

Antes de implementar schema, migrations, índices ou restrições, apresente a
[proposta de banco](templates/database-review.md): necessidade, antes/depois,
alternativas, rationale, impactos em dados/contratos, implantação e recuperação.
Use DB Reviewer quando uma integração estiver disponível e autorizada; caso
contrário, apresente esse artefato como proposta revisável. Bezalel não implementa
nem presume uma conexão com DB Reviewer.

Aprovação deve vir do usuário, referir-se à proposta exata e ocorrer **antes** da
implementação estrutural. O registro guarda referência à interação humana e o
SHA-256 somente da proposta aprovada, para detectar mudança posterior. Isso não
é inventário do repositório nem autenticação da aprovação. O runtime precisa
conferir a fonte humana. Não crie ou deduza uma aprovação por silêncio, por um
campo no JSON, por CI verde ou por parecer favorável de outro agente.

Se a proposta mudar, a aprovação anterior deixa de cobrir a nova versão. Sem
mudança estrutural, registre `database.change: none` e uma justificativa; não
invente uma etapa de aprovação. Investigações e proposta podem avançar; a
implementação estrutural fica bloqueada enquanto a decisão estiver pendente.

## 4. Implementar e passar o trabalho adiante

Faça entregas pequenas, com contratos explícitos entre camadas. Cada handoff
identifica história, revisão/artefatos afetados, critérios atendidos, evidências,
bloqueios e próximo responsável. Um especialista não marca a história como
pronta só porque sua camada terminou. Falha de integração retorna ao responsável
pela entrega inteira. Não imponha tecnologia idêntica para funções diferentes.

## 5. Validar independentemente e integrar

O desenvolvedor executa as verificações pertinentes; QA acrescenta cenários a
partir do requisito e do risco, incluindo negativos, integração e regressão.
Confronte comportamento observável, dados e contratos, não apenas testes criados
pelo próprio dev. Identifique cada critério como passado/falhou/bloqueado com
evidência. Se o comportamento real não pôde ser observado, mantenha pendência.

A identidade de quem revisa deve ser diferente dos implementadores. Papéis
nominalmente distintos no mesmo executor não comprovam independência; o runtime
precisa garantir a separação. Em trabalho individual, use revisão por outra pessoa
ou executor, sem afirmar que houve QA independente quando não houve.

O responsável integrado verifica o fluxo completo entre API/web/mobile e serviços
incluídos. Onde não houver dimensão aplicável, justifique em vez de inventar testes.

## 6. Preparar a entrega e executar só o autorizado

Prepare [rascunho da PR e roteiro manual](templates/pull-request.md), incluindo
problema, comportamento resultante, critérios, testes/evidências, impactos de
banco, limitações e operação necessária. Infraestrutura participa conforme risco.

Sem autorização de publicação, entregue a mudança/commit e o rascunho local,
registrando a PR remota como pendente. Autorização para preparar não autoriza
push, criação de PR, merge, deploy ou limpeza. Não transforme configuração ou
papéis em concessões permanentes. Se autorizado posteriormente, o runtime executa
a ferramenta, verifica o resultado e registra a referência real.
