<a id="process-postMerge"></a>

# Conferir merge e encerrar a tarefa

**Referência:** `postMerge`. **Responsável:** Tech Lead.

Aplique as [regras comuns](../dream-team.md#regras-comuns) do fluxo.

Retomada por aprovação humana da entrega ou aviso de merge, sem serviço de monitoramento. Pode ocorrer depois de outra sessão; reutilizar identidade das PRs, candidato e branch da tarefa, nunca o diretório atual como único indício.

1. **Consultar todas as PRs da entrega.** Registrar a interação humana e consultar GitHub pelo MCP/API/CLI disponível. Confirmar repositório, URL, base, head validado, estado merged, data e commit de merge para cada PR. PR aprovada, fechada sem merge, inacessível ou com versão divergente impede fechamento/limpeza; informar o estado e aguardar nova orientação ou evento real. Não executar merge, auto-merge, deploy ou polling por inferência.

2. **Encerrar somente o escopo concluído.** Confirmar que todas as PRs necessárias foram mergeadas e que não resta trabalho nas issues abrangidas. Fechar a issue existente e as histórias integralmente resolvidas; reler e verificar o estado. Se já fechada automaticamente, apenas verificar. Sem issue, registrar não aplicável. Não fechar história alheia, intenção residual ou principal com pendências; falha mantém a retomada registrada e precede a limpeza.

3. **Encaminhar e conferir o encerramento do ambiente.** Passar ao DevOps a identidade registrada de projeto/branch/worktree/ambiente, evidência de merge e estado das issues. O pedido deste fluxo autoriza encerrar somente esse ambiente após preservar o necessário. Receber e registrar resultado, alvos removidos/preservados e pendências. Guardar evidências na conversa/PR/issue ou fora da worktree antes da remoção. Se não houver ambiente gerenciado, registrar a verificação; não simular destruição. Falha de limpeza não reabre uma issue resolvida nem repete o fechamento.

**Pronto:** merges reais verificados, issues aplicáveis conferidas e ambiente encerrado ou comprovadamente não aplicável. Branch/worktree preservada por bloqueio significa encerramento parcial, informado ao usuário.

| Saída | Tipo | Destino |
|---|---|---|
| Merge ainda não comprovado | Estado próprio | Aguardar orientação/evento real, preservando ambiente e issues |
| Versão divergente ou trabalho restante | Encaminhamento | Coordenar a entrega |
| Issues verificadas: encerrar ambiente | Encaminhamento | Preparar, recuperar ou encerrar o ambiente |
| Encerramento concluído | Estado próprio | Informar resultado final |
| Encerramento parcial | Estado próprio | Registrar bloqueio, dono e condição de retomada |

**Condições locais das etapas:**

- Etapa 1 → **Merge ainda não comprovado**: Qualquer PR necessária não está mergeada/verificável.
- Etapa 2 → **Encerramento parcial**: Falha ao fechar/verificar issue; não passar à limpeza.
- Etapa 3 → **Encerramento parcial**: Preservação, identificação ou execução da limpeza ficou incompleta.
