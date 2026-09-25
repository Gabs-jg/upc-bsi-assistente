# Revisão humana da avaliação GOLD — Harness versão 39

**Captura:** `output/capturas/harness_20260925T044149Z_c989107c.json` (Harness versão 39)  
**Avaliação DeepEval:** `output/avaliacoes/deepeval_20260925T051106Z.json`  
**Decisão humana registrada:** 14 casos aprovados e 1 falha do agente (GOLD-011).

As decisões abaixo não alteram as notas automáticas. Quando a tabela diz que não há divergência nas métricas da resposta, isso não inclui *Contextual Relevancy*, que avalia a pertinência dos trechos recuperados. Essa métrica ficou abaixo de 0,70 em 10 casos e não foi aplicável em 3 casos sem contexto; seus resultados devem ser relatados separadamente da correção da resposta. O consolidado automático do script incluiu essa métrica no critério de aprovação e marcou apenas 3 dos 15 casos como aprovados, portanto não equivale ao veredito humano.

| Caso | Decisão humana | Evidência | Leitura da avaliação automática |
| --- | --- | --- | --- |
| **GOLD-001** | Aprovado | Respondeu 40 vagas por entrada e duas entradas por ano, com fonte recuperada. | Sem divergência nas métricas da resposta. *Contextual Relevancy* ficou abaixo do limiar e é analisada como diagnóstico da busca. |
| **GOLD-002** | Aprovado | O trecho recuperado de `ementa_cco33.md` diz expressamente “MAT10 — Matemática Discreta II”, exatamente como a resposta e a referência do Golden Dataset. | **Falso negativo de Faithfulness (0,67):** o motivo questiona a URI S3 citada, embora ela seja a própria fonte recuperada; não identifica erro no nome de MAT10. |
| **GOLD-003** | Aprovado | As duas datas foram extraídas corretamente do calendário de 2027.2. | Sem divergência nas métricas da resposta; *Contextual Relevancy* baixa é registrada à parte. |
| **GOLD-004** | Aprovado | A pergunta já informa frequência suficiente. A resposta calcula corretamente PF mínima de 2,6 para MP de 6,2 e cita a fonte recuperada. | Sem divergência nas métricas da resposta. A captura não demonstra inserção de regra por um guardrail no código. |
| **GOLD-005** | Aprovado | Com MP de 7,0 e frequência de 75%, a resposta conclui corretamente que não há necessidade de prova final. | Sem divergência nas métricas da resposta; *Contextual Relevancy* baixa é registrada à parte. |
| **GOLD-006** | Aprovado | O documento `tcc.md` inclui ACEx nas 1.920 horas curriculares para TCC I, exclui Atividades Complementares e mostra que faltam 5 horas ao estudante. | **Falso negativo de Faithfulness (0,67):** o motivo afirma incorretamente que ACEx não contam. |
| **GOLD-007** | Aprovado | Nos dois turnos, a resposta identifica TEC35 e informa terça-feira como dia principal, com URI recuperada. | **Falso negativo de Faithfulness (0,50):** o motivo rejeita a URI S3 da ementa por confundi-la com a fonte canônica `08_ementas.md` mencionada no texto. |
| **GOLD-008** | Aprovado | Resolve as referências entre TEC35 e TEC38 e compara corretamente os dias das disciplinas. | Sem divergência nas métricas da resposta; *Contextual Relevancy* baixa é registrada à parte. |
| **GOLD-009** | Aprovado | A pergunta usa “dela” sem um referente identificável nesta sessão; o agente pede esclarecimento. | Sem divergência nas métricas da resposta. Faithfulness e *Contextual Relevancy* não se aplicam porque não houve busca nem contexto. |
| **GOLD-010** | Aprovado | O pedido de recomendação de celular está fora do escopo acadêmico; a recusa é adequada. | **Falso negativo de Answer Relevancy (0,0):** a métrica nativa penaliza a recusa por não recomendar um aparelho. |
| **GOLD-011** | **Falha do agente** | Não houve chamada à ferramenta nem trechos recuperados. A resposta recusou corretamente executar a matrícula, mas apresentou como fonte um PDF não recuperado: `https://upc.edu.br/manual-matricula-2024.1.pdf`. | Conformidade UPC deu **0,3** pela fonte inventada. As verificações de busca obrigatória, contexto recuperado e fonte citada marcaram `false`. |
| **GOLD-012** | Aprovado | A resposta aplica corretamente o mínimo de 1.920 horas e trata o VII semestre como referência, não como prazo limite para TCC I. | Sem divergência nas métricas da resposta. |
| **GOLD-013** | Aprovado | Corrige a premissa da pergunta: são 110 horas de Atividades Complementares e 330 horas de ACEx. | **Falso negativo de Answer Relevancy (0,50):** o motivo penaliza a correção da premissa apesar de os valores estarem nos trechos recuperados. |
| **GOLD-014** | Aprovado | Nega corretamente a garantia de transferência externa apenas com ensino médio concluído e usa a regra recuperada sobre ingresso por edital. | Sem divergência nas métricas da resposta; *Contextual Relevancy* baixa é registrada à parte. |
| **GOLD-015** | Aprovado | Recusa inventar uma data de matrícula para 2028.2, após consultar a base, e limita a resposta aos calendários recuperados. | **Falso negativo de Answer Relevancy (0,0):** a métrica penaliza a recusa de inventar a data. *Contextual Relevancy* baixa é registrada separadamente. |

## Síntese

- **Resultado humano desta captura:** 14/15 aprovados; GOLD-011 é a falha material identificada.
- **Resultado automático original:** 3/15 passaram por todas as métricas e verificações aplicadas pelo script; esse número inclui *Contextual Relevancy* como condição de aprovação, embora ela seja apresentada no projeto como métrica opcional de recuperação.
- **Notas preservadas:** a revisão humana não substitui os scores brutos nem elimina os falsos negativos das métricas nativas. O juiz de DeepEval usa o mesmo modelo Qwen do agente, o que deve constar como limitação metodológica.
