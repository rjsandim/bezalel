<a id="process-accept"></a>

# Executar roteiro e decidir aceite

**Referência:** `accept`. **Responsável:** APROVADOR HUMANO.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Aceite funcional externo na PR já aberta, sobre a versão apresentada. A execução do humano permanece distinta do QA; abertura de PR não depende deste aceite.

1. **Conferir candidato e roteiro.** Abrir pacote/ambiente identificados; esclarecer impedimentos de acesso, dados ou versão antes de executar.

2. **Executar e registrar o observado.** Executar os casos humanos aplicáveis e registrar observado, resultado, data/executor e evidência. Casos não executados permanecem assim; não herdar resultado do QA.

3. **Decidir o aceite do conjunto.** Aceitar a versão validada ou descrever falhas/ajustes. Mudança de necessidade vai a PM/TL; defeito segue correção e revisões afetadas. Registrar decisão real; aceite não autoriza merge/deploy nem cobre versão alterada por inferência.

**Pronto:** execução humana suficiente e aceite explícito vinculado à versão.

| Saída | Tipo | Destino |
|---|---|---|
| Aceite registrado: conferir merge | Conclusão da atividade | Conferir merge e encerrar a tarefa |
| Falha, impedimento ou ajuste: TL | Encaminhamento | Coordenar a entrega |
| Roteiro ou decisão pendente | Estado próprio | Estado descrito na saída; não encaminha outro processo |

**Condições locais das etapas:**

- Etapa 1 → **Falha, impedimento ou ajuste: TL**: Acesso, dados ou candidato impedem a execução e precisam de ação/decisão.
- Etapa 2 → **Roteiro ou decisão pendente**: Execução humana permanece pendente, com condição e responsável identificados.
- Etapa 3 → **Falha, impedimento ou ajuste: TL**: Humano rejeita ou solicita alteração/esclarecimento; não concluir a entrega.
- Etapa 3 → **Roteiro ou decisão pendente**: Aceite ausente ou ambíguo.
