<a id="process-fullstack"></a>

# Executar contribuição fullstack

**Referência:** `fullstack`. **Responsável:** Desenvolvedor fullstack.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Abrange as camadas selecionadas. Preparar telas/contrato e próprio mock quando pertinente; integrar front, negócio/persistência e serviços sem presumir que dispensa outro especialista. Um procedimento por especialidade; cada entrada executa somente a fase designada.

1. **Receber a tarefa e conferir pré-condições.** Conferir fase, pergunta/escopo, versão, dependências e entrega esperada. Aplicar R5–R6: investigação com isolamento; interface/mock após investigação; implementação após investigação, UI/UX e aprovações aplicáveis. Falta material ou dúvida de dependência volta ao TL.

2. **Executar a fase atribuída.** Investigar com iss-audit no modo dev: entregar diagnóstico/viabilidade e alternativas, mantendo experimento separado. Preparar interface/mock: entregar estados, contrato e demonstração sintética, sem antecipar banco/migration/API definitiva pendentes. Implementar/corrigir conforme plano e .bezalel/project.json, usando clean-code no código alterado e clean-architecture somente quando afetar responsabilidades, fronteiras ou dependências; executar testes próprios por risco e integrar consumidores reais. Toda operação somente de dados entrega artefato versionado com seleção, validação, repetição e recuperação. Corrigir falha ordinária autorizada; decisão de escopo/contrato/banco ou dependência externa volta ao TL. Preservar view → entrada HTTP/action fina → negócio específico → fachadas de persistência → banco; negócio fora de HTTP/Filament, sem Request/Response/forms. Domain-kernel somente quando definido pelo projeto; sem fachada universal, interface por classe ou refatoração geral. Aplicar implementar-snapshots somente se construir/corrigir essa funcionalidade for a tarefa. agent-browser pode apoiar reprodução e jornadas web, nas condições comuns.

3. **Entregar a contribuição identificada.** Entregar fase, versão, provas e limites ao TL. Na implementação, o dev integrador reúne contribuições/histórias, confere contratos/mock/API real e entrega candidato completo com base/head e testes. Contribuição parcial ou complemento de prova não libera o conjunto nem substitui revisão independente.

**Pronto:** entrega da fase verificável e limites explícitos. Conclusão de investigação/mock não autoriza implementação; TL confirma o próximo passo.

| Saída | Tipo | Destino |
|---|---|---|
| Contribuição ou prova concluída: TL | Conclusão da atividade | Coordenar a entrega |
| Condição ausente ou decisão necessária: TL | Impedimento/reprovação | Coordenar a entrega |

**Condições locais das etapas:**

- Etapa 1 → **Condição ausente ou decisão necessária: TL**: Pré-condição da fase ausente ou versão/autorização/dependência materialmente incerta.
- Etapa 2 → **Condição ausente ou decisão necessária: TL**: Descoberta exige decisão, recurso externo ou altera escopo/contrato/banco; interromper dependentes.
