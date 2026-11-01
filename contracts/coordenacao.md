# DreamTeam — coordenação de atribuições

Regras para quem delega: o agente que inicia a conversa e o Tech Lead, ou qualquer
recebedor que atribua uma nova tarefa. Papéis que só executam a própria atribuição
seguem o resumo em [R3](dream-team.md#r3-passagem-entre-atividades) e não precisam ler este arquivo.

## Seleção proporcional de modelos

O agente que inicia a conversa avalia a demanda e indica, antes de delegar, o modelo
mais apropriado para a coordenação e para cada atividade prevista, com justificativa
curta. Identifique o modelo inicial quando a aplicação o informar; se desconhecido,
registre essa limitação. A indicação não troca automaticamente o modelo da conversa.

Em toda atribuição, inclusive novas delegações por um recebedor, tente primeiro
selecionar o menor modelo disponível capaz de cumprir a tarefa, priorizando opções
menores que o modelo que iniciou a conversa. Não herde o modelo inicial por
conveniência e não use o modelo mais potente para todos os papéis. Escolha pela
complexidade, incerteza, impacto, contexto e ferramentas necessários, não pelo título
do agente. Leitura delimitada, ajustes simples e verificações objetivas favorecem
modelos menores; raciocínio amplo, diagnóstico difícil ou risco elevado podem
justificar maior capacidade já na seleção, sem exigir uma tentativa inadequada.

Consulte as opções e capacidades expostas pela aplicação na sessão, sem fixar nomes
ou presumir uma ordem de capacidade a partir deles. Passe o modelo escolhido
explicitamente na ferramenta de delegação quando houver suporte. Se a escolha
exigir contexto novo em vez de herança da conversa, forneça objetivo, instruções,
fontes, decisões, versão e critérios suficientes no handoff. Não reduza isolamento,
independência de QA/AppSec, verificações ou critérios de entrega para economizar.

Registre no handoff o modelo inicial conhecido, o recomendado, a razão da escolha e
o modelo efetivo apenas quando confirmado pela ferramenta. Uso do mesmo modelo ou
de um maior exige motivo concreto: capacidade necessária, insuficiência observada
ou ausência de opção menor disponível. Escale quando houver limitação demonstrada,
preservando contexto e provas; reavalie a escolha na próxima atividade, sem manter
a escalada como padrão. Não repita tentativas inadequadas apenas para cumprir a regra.

Sem seleção de modelo na ferramenta, informe a recomendação e a limitação, seguindo
com o modelo disponível quando suficiente e autorizado. Não alegue redução executada,
não invente IDs, nem altere configurações globais ou a conversa por inferência.
Esta política orienta os executores; arquivos e instalação não impõem roteamento
nem comprovam qual modelo foi usado.

## Economia de contexto e coordenação

Aplicar estas regras à passagem R3 em todos os cenários, mantendo R2 e
R5–R11, a ordem das revisões e as condições de cada etapa:

- **Comunicar por mudança relevante.** Enviar resultado, bloqueio, dúvida necessária
  ou alteração de escopo/versão/dependência que afete outro responsável. Evitar
  confirmações repetidas, pedidos de andamento sem motivo e mensagens que apenas
  repitam estado já registrado. Bloqueios e riscos são comunicados assim que
  identificados; economia não justifica silêncio sobre impedimentos. Preservar as
  atualizações ao usuário exigidas pela aplicação. Preferir notificações de conclusão
  das ferramentas; sem esse suporte, usar espera apropriada à duração prevista e
  consultas pontuais quando necessárias, sem ciclos curtos de consulta/mensagem
  apenas para constatar que nada mudou. Isso não autoriza monitoramento contínuo.
- **Delimitar o contexto de cada atribuição.** Fornecer objetivo/fase, escopo,
  responsável, candidato/base/versão, decisões e restrições aplicáveis, critérios,
  dependências, fontes e evidências relevantes. Preferir referências e trechos
  pertinentes a copiar o histórico integral ou carregar todos os documentos/skills.
  Manter as fontes completas acessíveis; o recebedor consulta o necessário e amplia
  a leitura quando houver ambiguidade, risco ou dependência. Não omitir instruções
  obrigatórias, decisões humanas, achados pendentes ou contratos de integração.
  Se a ferramenta permitir contexto novo, preferi-lo com esse handoff suficiente;
  não alegar isolamento de contexto quando a ferramenta herdar a conversa.
- **Reutilizar provas com validade conferida.** Identificar origem, executor,
  candidato/versão, cobertura e limitações antes de aproveitar evidência existente.
  Conferir diferenças de código, composição, schema, dependências, configuração e
  ambiente pertinentes. Sem impacto, referenciar o resultado válido em vez de
  repetir leitura, teste ou parecer. Mudança material invalida a cobertura afetada;
  dúvida de impacto exige investigação/revalidação, nunca aprovação presumida.
  O revisor independente avalia as fontes e lacunas por conta própria: testes do
  autor não substituem QA/AppSec nem suas verificações obrigatórias. Reutilização
  não dispensa testes exigidos para o candidato nem converte prova parcial em aceite.
- **Delegar uma entrega completa por fase.** Agrupar investigação, preparação,
  implementação/correção ou revisão em uma atribuição com resultado verificável,
  limites, dependências e condição de conclusão. Dentro do escopo autorizado, o
  executor realiza os passos necessários e correções ordinárias sem nova atribuição
  para cada comando, arquivo ou teste. Retorna resultado/evidências ou impedimento;
  esclarecimentos necessários continuam permitidos. Retomadas trazem a diferença,
  o ponto pendente e as provas válidas, sem reiniciar a fase inteira. Não agrupar
  fases para atravessar aprovação pendente, mudar responsabilidades ou eliminar
  revisão independente; mudança de escopo segue PM/humano.

Estas orientações não alteram quantidade de papéis, seleção de modelos, testes,
critérios de entrega ou autorizações. São contratos documentais, sem medição ou
limitação automática de tokens; a economia efetiva precisa ser observada no uso.
