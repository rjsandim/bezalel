# Modelos de issue

Use como corpo da issue ou submissão versionada. Não crie MD paralelo por demanda.
Escolha o modelo do cenário: bug (abaixo) ou história de melhoria/feature.

## Bug: relato

**Observado:** <o que acontece, com mensagem de erro ou captura sanitizada>.
**Esperado:** <o que deveria acontecer e a regra que o define>.
**Reprodução:** <passos ou entrada mínima, versão/commit e ambiente>.
**Impacto:** <quem é afetado, frequência e dados envolvidos>.
**Critério de correção:** <resultado verificável depois da correção>.
**Classe sugerida:** pequena | normal (o TL confirma).

---

# US-000 — Resultado desejado

Em feature, vincule as histórias à principal e explicite critérios globais;
a decisão humana abrange a versão exata do conjunto.

## Necessidade

Como <pessoa>, preciso <capacidade> para <resultado>. Contexto essencial:
<regra de negócio que permite compreender a história isoladamente>.

## Critérios observáveis

- AC-01: <situação, ação e resultado verificável>.
- AC-02: <negativa, limite ou comportamento relevante>.

## Dependências e limites

- Dependências: <história/contrato necessário, ou nenhuma com motivo>.
- Fora do escopo: <limite concreto>.
- Contratos afetados: <API/web/mobile, ou não aplicável>.
- Responsável pela integração: <identidade, não apenas nome da equipe>.
