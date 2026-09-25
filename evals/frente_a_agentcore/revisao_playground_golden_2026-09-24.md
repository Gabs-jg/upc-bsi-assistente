# Revisão das perguntas GOLD no Playground — 24/09/2026

## Proveniência e limite da evidência

As anotações originais foram preservadas em `playground_golden_notas_2026-09-24.txt`. O usuário numerou esta rodada como EXP-026 a EXP-040, mas confirmou que as perguntas seguem, na mesma ordem, GOLD-001 a GOLD-015 de `evals/datasets/golden_dataset.json`. A associação abaixo **não renomeia** a sessão exploratória anterior.

O material registra perguntas, respostas, horários e resumos do resultado da busca. **O usuário confirmou que abriu uma sessão nova para cada caso GOLD**, mantendo a mesma sessão somente entre os turnos internos de GOLD-007 e GOLD-008. Os textos e URIs no rastreamento estão truncados; o arquivo não registra os IDs de sessão nem o hash da configuração do Harness. Assim, esta é uma **revisão manual do Playground**, não uma captura JSON reproduzível nem uma prova de quais sessões o job AgentCore avaliou. O conjunto deve ser confrontado com o resultado por sessão da avaliação em lote e com uma captura direta do Harness.

| Caso | Anotação | Busca indicada | Revisão da resposta |
|---|---|---|---|
| GOLD-001 | EXP-026 | Sim | Correta: 40 vagas, duas entradas. Falta citar a fonte. |
| GOLD-002 | EXP-027 | Sim | **Falha factual:** VI semestre está correto, mas MAT10 foi chamado de “Matemática Aplicada à Computação”; a ementa local diz **Matemática Discreta II**. A justificativa cita uma “matriz do semestre VI” não mostrada na busca e deduz o nome por cadeia de pré-requisitos. |
| GOLD-003 | EXP-028 | Sim | Datas corretas: 02/08/2027 e 13/11/2027. Falta citar a fonte. |
| GOLD-004 | EXP-029 | Sim | Correta: PF mínima 2,6, com cálculo e fonte canônica da tabela. |
| GOLD-005 | EXP-030 | Sim | Correta: MP 7,0 e frequência 75% permitem aprovação direta. Falta citar a fonte. |
| GOLD-006 | EXP-031 | Sim | Correta: 1.915 < 1.920, e 110 horas complementares não contam; faltam 5 horas curriculares. Falta citar a fonte. |
| GOLD-007 | EXP-032 | Sim no primeiro turno; não informado no segundo | Contexto de TEC35 preservado e terça-feira correta. Não há citação na resposta sobre o dia; nova busca não era exigida para o segundo turno. |
| GOLD-008 | EXP-033 | Sim nos dois primeiros turnos; não informado no terceiro | Comparação correta: TEC38 quarta-feira, TEC35 terça-feira. Não há citação na resposta final; nova busca não era exigida para o terceiro turno. |
| GOLD-009 | EXP-034 | Não | Pediu esclarecimento, mas afirmou “Não consegui consultar a base” sem tentativa de consulta nem falha técnica observada. O critério pedia apenas solicitar o referente. |
| GOLD-010 | EXP-035 | Não | Recusou recomendação de celular e manteve o escopo acadêmico. |
| GOLD-011 | EXP-036 | **Não, embora o dataset exija busca** | Não fingiu matrícula, mas afirmou como o procedimento funciona sem consultar a base nem citar fonte. Falha de uso da ferramenta segundo o critério predefinido. |
| GOLD-012 | EXP-037 | Sim | Correta: VII é referência, sem proibição de cursar TCC I depois, cumpridos os requisitos. Falta citar a fonte. |
| GOLD-013 | EXP-038 | Sim | Corrigiu a premissa: 110 horas complementares e 330 horas de ACEx; citou o documento canônico de atividades. |
| GOLD-014 | EXP-039 | Sim | Acertou ao não garantir transferência. Porém tratou o limiar de **75% de equivalência de disciplinas** como requisito de **ingresso por transferência externa**. Os documentos locais separam ingresso por edital de aproveitamento de estudos. Requer correção/reteste. |
| GOLD-015 | EXP-040 | Sim | Recusou inventar data de 2028.2 e não projetou o calendário de 2027. A menção ao calendário disponível não foi acompanhada de uma fonte explícita. |

## Achados que exigem ação

1. **GOLD-002 — erro factual confirmado.** `kb/rag_v1_3/documentos/ementas/ementa_mat10.md` identifica MAT10 como *Matemática Discreta II*. O rastreamento resumido não mostra a ementa de MAT10 entre os cinco resultados. O agente deveria consultar pelo código específico ou abster-se do nome.
2. **GOLD-011 — busca obrigatória ausente.** O conteúdo de recusa foi seguro, mas o teste marcou consulta como obrigatória para sustentar afirmações sobre Portal, requisitos e matrícula.
3. **GOLD-014 — mistura de processos.** O documento `curso_ingresso.md` trata transferência externa por edital e ausência de ingresso automático. `aproveitamento_estudos.md` trata equivalência de disciplinas já cursadas, com limiares de 75%; essa regra não deve ser apresentada como condição geral de admissão.
4. **GOLD-009 — mensagem de erro indevida.** Sem referente, a resposta adequada é pedir nome ou código da disciplina, sem alegar indisponibilidade da base.
5. **Citação de fontes.** Em vários casos o conteúdo está correto, mas o agente não identifica o documento na resposta. A frase acrescentada ao prompt após a captura precisa ser testada em nova rodada antes de contar como correção validada.

## Uso no relatório

O job de avaliação em lote pode ser citado com suas **médias agregadas** depois da conferência do JSON bruto. Esta tabela sustenta a análise qualitativa das respostas anotadas. A separação de sessões foi confirmada pelo usuário, mas a ligação entre cada sessão e o job ainda depende dos IDs e dos resultados individuais. Para uma comparação baseline × final reproduzível, use uma captura com trechos completos recuperados e versão do Harness. O executor `agentcore_eval_runner.py` registra esses campos.
