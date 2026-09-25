# Evidências geradas — `output/`

Esta pasta preserva capturas, avaliações, calibrações e spans de diferentes rodadas do Desafio 2. **A configuração de referência desta entrega é o Harness v39**; arquivos anteriores são históricos e não comprovam aprovação da v39.

| Evidência v39 | O que registra |
| --- | --- |
| [Captura GOLD](capturas/harness_20260925T044149Z_c989107c.json) | 15 casos e 18 turnos, com respostas, chamadas de busca e trechos recuperados. |
| [Captura red team](capturas/harness_20260925T122031Z_92851915.json) | 15 ataques em sessões independentes, com o mesmo hash de configuração da captura GOLD. |
| [Spans](spans_agentcore_20260925T044149Z.json) | 384 spans de 15 sessões GOLD, extraídos do CloudWatch. |
| [Fundamentação AgentCore](avaliacoes/agentcore_batch_20260925T045130Z.json) | Avaliador personalizado; 18 notas por turno. |
| [Faithfulness AgentCore](avaliacoes/agentcore_batch_20260925T045418Z.json) | Avaliador integrado; 18 notas. |
| [Helpfulness AgentCore](avaliacoes/agentcore_batch_20260925T045631Z.json) | Avaliador integrado; 18 notas. |
| [Suíte DeepEval](avaliacoes/deepeval_suite_20260925T130537Z_944cc9f2.json) | Métricas nativas e G-Eval: **7/15** casos passaram automaticamente. |

A [revisão humana GOLD](../revisao_humana_v22.md) aprovou **14/15** respostas e manteve GOLD-011 como falha real. A [revisão do red team](../evals/red_team/avaliacao_harness_v39_2026-09-25.md) encontrou falhas graves em RT-007 e RT-015. Uma nota alta ou a conclusão bem-sucedida de uma chamada de avaliação não significa aprovação do agente.

Os arquivos de v21 e v22 permanecem para comparação histórica. O resultado intermediário de “15/15” usou outra configuração de métricas; não é o resultado da suíte exigida e executada sobre a v39. Consulte o [relatório final](../Relatorio_Final.md) para método, limites de comparação e parecer de risco.
