# Base de agentes do Bezalel

Agentes definem **papel e processo**; instruções do projeto definem arquitetura e
regras de negócio; skills descrevem procedimentos reutilizáveis. Esta pasta
contém definições versionáveis para um operador ou runtime consumir. Não inicia
agentes, delega trabalho, conecta serviços ou concede permissões.

## Papéis e seleção

| Papel | Quando usar | Responsabilidade principal |
|---|---|---|
| [Produto](roles/produto.md) | Dúvida de necessidade, prioridade ou desvio de visão | Explicitar escolhas; o usuário decide mudanças de produto |
| [Coordenador/arquiteto](roles/coordenador.md) | Integrações, risco arquitetural ou múltiplos responsáveis | Impacto, contratos, estratégia e entrega inteira integrada |
| [Dev fullstack](roles/dev-fullstack.md) | História pequena que atravessa camadas | Implementar uma entrega vertical pequena |
| [Backend](roles/backend.md) | Regras, persistência ou contratos de serviços relevantes | Backend e compatibilidade com consumidores |
| [Frontend web](roles/frontend-web.md) | Interação web exige especialização | Fluxos web, estados de interface e acessibilidade |
| [Mobile](roles/mobile.md) | Apps, versões distribuídas ou comportamento móvel | Contratos, conectividade, versões e plataforma |
| [QA independente](roles/qa.md) | Validação da entrega | Ampliar cenários e confrontar comportamento com a história |
| [Infraestrutura](roles/infraestrutura.md) | Isolamento ou preparação operacional da entrega | Evidenciar isolamento e preparar execução autorizada |
| [Observador de confiabilidade](roles/observador-confiabilidade.md) | Futuro; sempre desativado nesta base | Investigar sinais e propor demandas, sem corrigir |
| [Observador de negócio](roles/observador-negocio.md) | Futuro; sempre desativado nesta base | Investigar anomalias no contexto de negócio, sem corrigir |

Não forme uma equipe completa por padrão. Para uma história simples, um dev e
uma revisão independente podem bastar; um deles ou o usuário é identificado como
responsável pela integração. Especialistas entram pelo risco, não pelo número
de pastas. Papéis podem ser exercidos por pessoas ou agentes; QA precisa de uma
identidade revisora diferente de quem implementou. A indisponibilidade de um
revisor mantém a validação pendente, não permite marcar aprovação fictícia.

O [catálogo](catalog.json) relaciona papéis e skills existentes. Metadados em
`skills/*/agents/openai.yaml` continuam sendo adaptadores de interface das skills;
não devem ser confundidos com estas definições de papéis.

## Unidade de trabalho

Use uma [user story curta](templates/user-story.md), compreensível sem buscar
fragmentos de contexto em várias conversas. Ela contém necessidade, critérios
observáveis identificados, dependências e limites. Referências complementam a
história; não escondem o requisito essencial. Uma história deve ter um responsável
pela integração inteira e um resultado verificável, não uma lista de tarefas por
camada sem entrega ao usuário.

O [fluxo e os contratos](workflow.md) definem isolamento, revisão de banco,
implementação, QA e preparação da PR. O [handoff](templates/handoff.md) deve
transportar resultado, evidência, bloqueios e próximo responsável, sem repetir
um documento enorme. Não transfira um bloqueio silenciosamente.

## Configuração por projeto

Use o [modelo](../.bezalel/project.example.json) como ponto de partida para
`<projeto>/.bezalel/project.json`. É configuração versionável sem segredos: aponta
instruções de arquitetura/negócio e registra comandos de verificação declarados.
Não executa esses comandos. `.bezalel/vps-deploy.local.json` e o token continuam
seguindo o contrato próprio da skill VPS Deploy; nenhuma credencial entra aqui.

Adapte nomes, documentos, interfaces e sinais ao projeto. Exemplos não são SLAs
nem autorização. Observadores permanecem com `enabled: false` e
`mode: proposal_only`; este repositório não oferece agendador nem integração de
telemetria/produção. Um runtime futuro precisará de autorização e fontes corretas.

## O que executa hoje

- `scripts/check_repository.py`: valida o pacote, catálogo, seções e links.
- `scripts/check_delivery.py`: lê configuração, história e registro local de
  entrega; valida declarações exigidas para planejamento, implementação ou entrega.
  Também detecta aprovação ausente ou incompatível com a versão da proposta de banco.
- Scripts existentes das skills: executam somente quando chamados explicitamente,
  com seus próprios limites. Não são chamados pelo validador de entrega.

O validador **não verifica a verdade de uma evidência nem a identidade humana de
quem aprovou**. Não executa testes, aprova alterações, implementa, delega ou cria
PR. Sua saída é um check de contrato, não uma autorização. Um runtime precisa
verificar a origem da aprovação na interação humana, executar ferramentas,
observar resultados e impedir efeitos antes dos gates. Markdown sozinho não faz
isso. Veja [contrato do registro](record-contract.md).

## Exemplo local

A [história de exemplo](examples/US-001.md) é sintética. O
[registro modelo](templates/delivery.example.json) começa com verificações
pendentes, sem fabricar aprovação ou QA. Copie/adapte em um projeto descartável
ou no projeto autorizado; não trate o exemplo como entrega concluída.

```sh
python3 <Bezalel>/scripts/check_delivery.py --project <projeto> --record .bezalel/deliveries/US-001.local.json --stage plan
```

`implement` exige declarações de isolamento e situação de banco resolvidas;
`deliver` acrescenta evidências, QA independente, integração e rascunho da PR.
Nenhuma etapa publica. A PR é uma etapa prevista da entrega, mas sua criação
remota, merge e deploy dependem da autorização concreta de cada tarefa.
