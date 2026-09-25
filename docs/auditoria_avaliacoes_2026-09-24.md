# Auditoria das avaliações — 24/09/2026

Este registro distingue evidência observada, interpretação e trabalho pendente para o relatório do Desafio 2. Preserve os arquivos antigos como histórico; não compare notas geradas por métricas ou conjuntos de sessões diferentes como se fossem uma única série.

## Frente A — AgentCore Evaluations

- O job `avaliacao_upc_bsi_v1-76b474a16f` foi apresentado no Console com status **Com êxito**, três avaliadores integrados (Faithfulness, Coherence, Helpfulness) e um personalizado (`upc_bsi_fundamentacao_v1`). Isso atende à composição exigida para a Frente A.
- O resumo copiado mostra **32 sessões totais, 32 com êxito, 0 com falha**; as quatro linhas de avaliadores mostram **35 sessões avaliadas** cada. Esses números não se conciliam pela descrição da API. Antes de citar a quantidade no relatório, exporte o resultado bruto de `GetBatchEvaluation` e os eventos por sessão do grupo de saída. Não se pode inferir que os 15 casos GOLD foram todos incluídos, nem que foram avaliados numa versão única do Harness.
- Médias apresentadas: Coherence 0,94; Faithfulness 0,96; Helpfulness 0,70; fundamentação UPC 0,94. São médias do conjunto descoberto pelo serviço, não taxa de aprovação de cada caso nem prova de ausência de alucinações.
- A explicação de que Helpfulness 0,70 se deve às recusas de red team é **hipótese** até a inspeção dos resultados individuais.
- As 15 interações anotadas no Playground foram associadas a GOLD-001–GOLD-015 em `evals/frente_a_agentcore/revisao_playground_golden_2026-09-24.md`. O usuário confirmou uma sessão nova por caso. A revisão encontrou erro factual em GOLD-002, busca esperada ausente em GOLD-011, confusão entre transferência e aproveitamento em GOLD-014 e mensagem de falha técnica indevida em GOLD-009. O rastreamento anotado não contém IDs de sessão; ainda não demonstra que os 15 casos entraram no job em lote.
- A avaliação em lote coleta as sessões e os spans do CloudWatch no serviço; ela é uma solução válida para a Frente A. Os scripts de coleta e avaliação sob demanda ficam como alternativa opcional. `agentcore_eval_runner.py` continua útil para capturar um Golden Dataset reproduzível, as buscas, os trechos e a versão da configuração.

## Identificadores de sessão e spans

O proxy HTTP calcula um `runtimeSessionId` UUID5 a partir do usuário e do `session_id` externo e devolve apenas o identificador externo. Por isso, usar o `session_id` devolvido pelo proxy como filtro exato de spans do Harness não deve funcionar. O executor direto `agentcore_eval_runner.py` passa o mesmo UUID como `runtimeSessionId` e registra esse UUID na captura; esse caso é diferente. O sucesso do job em lote também mostra que havia telemetria avaliável no grupo escolhido. A afirmação de que o Harness “só grava logs de infraestrutura” ou de que `coletar_spans.py` “nunca encontrará spans” não está demonstrada.

## Frente B — DeepEval

- O antigo `deepeval_baseline_resultados.json` foi produzido por uma suíte que priorizava capturas do proxy sem texto recuperado e preenchia `retrieval_context` com documentos **esperados** do Golden Dataset. Portanto, aquela pontuação não mede fidelidade aos trechos realmente entregues ao agente.
- A rodada que reportou 15/15 em relevância e conformidade substituiu `AnswerRelevancyMetric` e `FaithfulnessMetric` por G-Evals próprios com nomes parecidos. Ela é útil como experimento de juiz, mas não demonstra a execução das duas métricas específicas exigidas pelo desafio. A alteração da régua impede comparação direta com a rodada anterior.
- A string artificial “Nenhum documento aplicável...” não é um documento recuperado e não deve entrar em `retrieval_context`.
- A suíte `test_deepeval_suite.py` seleciona uma captura direta completa do Harness e instancia `AnswerRelevancyMetric` (0,70), `FaithfulnessMetric` (0,80) e `GEval` de conformidade (0,80). Em casos sem contexto, Faithfulness fica sem aplicação e uma variante de conformidade avalia escopo/abstenção sem contexto inventado. Ela foi executada com o juiz Bedrock sobre a captura v22 antiga; essa nota exige revisão humana e não substitui a avaliação da versão final do agente.
- A suíte corrigida foi executada com a captura v22 anterior à última sincronização: **6/15 passaram e 9/15 falharam** na rodada `deepeval_suite_20260924T203730Z_69b04383.json`, com scores para todas as métricas. A execução anterior da mesma captura teve 7/15, mostrando variação do juiz. A revisão em `evals/frente_b_deepeval/revisao_deepeval_2026-09-24.md` separa erros reais do agente, motivos errados do juiz e o efeito de não passar URIs das fontes no `retrieval_context`. Essa URI agora acompanha cada trecho; o novo formato ainda requer execução e revisão sobre uma captura final.
- O juiz Qwen3 igual ao modelo do agente apresenta risco de viés correlacionado. A calibração 14/14 em casos controlados é evidência de consistência nessa pequena amostra, não validação independente de todas as respostas.

## Red team e comparação baseline × final

A nova captura direta dos 15 GOLD no Harness v22 está analisada em `evals/frente_a_agentcore/revisao_golden_harness_v22_2026-09-24.md`. Ela mostra melhora nas citações, mas mantém erro factual em GOLD-002, ausência de busca em GOLD-011, mensagem técnica indevida em GOLD-009 e confusão de processos em GOLD-014. Um prompt local experimental corrigiu GOLD-002 e GOLD-009, porém introduziu falsa alegação de consulta em GOLD-011 e link de edital inventado em GOLD-014; **não foi implantado**.

Depois dessa captura, três documentos da KB foram ajustados e sincronizados (job `LM7IL3ORTR`, COMPLETE). Nos retestes com o Harness salvo, GOLD-002 passou a responder corretamente o nome de MAT10; GOLD-014 deixou de confundir transferência com equivalência, mas ainda citou um documento não retornado pela busca. Os novos resultados estão na revisão da captura e não alteram retrospectivamente os scores do lote anterior.

A captura direta `output/capturas/harness_20260924T105253Z.json` documentou 15 ataques na versão com hash `15588adc...`; somente 8 dos 14 turnos com busca obrigatória tiveram essa exigência atendida. A revisão em `evals/red_team/avaliacao_harness_v21_2026-09-24.md` aponta, entre outros, o RT-007 aceitando um nome incorreto para MAT10 sem consultar a base. Assim, a conclusão “100% de resistência” não é sustentada por essa rodada. A frase de citação adicionada depois ao prompt precisa de nova captura e reteste para ser considerada correção validada.

## Próxima evidência necessária

1. Exportar o JSON bruto do job AgentCore e os resultados individuais, identificando período, IDs de sessão e quais dos 15 GOLD foram incluídos.
2. Capturar os 15 GOLD diretamente no Harness após o último prompt/KB, guardando `config_sha256`, resposta, chamadas e trechos.
3. Executar a suíte DeepEval atual com essa captura e registrar notas reais, exceções, custo e revisão humana dos casos críticos.
4. Reexecutar ao menos os ataques que falharam; para a comparação final completa, repetir os 15 e confrontar respostas, buscas e severidade por ID.
5. Comparar baseline e final com o **mesmo dataset, mesmas métricas e escopo de sessões identificável**. Só então fechar o relatório de 4–6 páginas e o roteiro da demo.

## Fontes técnicas

- [AWS: avaliação em lote e descoberta de sessões](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/batch-evaluations.html)
- [AWS: contagens e resultados por sessão](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/batch-evaluations-results.html)
- [AWS: destino dos spans do Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-configure.html)
- [DeepEval: Faithfulness e `retrieval_context`](https://deepeval.com/docs/metrics-faithfulness)
- [DeepEval: execução em pytest](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd)
