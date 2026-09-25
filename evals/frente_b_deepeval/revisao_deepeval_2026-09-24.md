# Revisão da execução DeepEval — 24/09/2026

**Resultado bruto:** `output/avaliacoes/deepeval_suite_20260924T203730Z_69b04383.json`  
**Captura avaliada:** `output/capturas/harness_20260924T153740Z.json` (Harness v22, antes da sincronização `LM7IL3ORTR`)  
**Juiz:** `qwen.qwen3-next-80b-a3b`, o mesmo modelo do agente; avaliação sujeita a viés correlacionado.  
**Execução:** 15 casos, 6 passaram e 9 falharam nos testes automatizados. Todas as métricas produziram pontuação; esta rodada não repetiu o erro de `portalocker`/`Score: None`.

O resultado anterior da mesma captura teve 7 casos aprovados. A diferença de um caso entre as rodadas mostra instabilidade do juiz; não representa uma mudança do agente, pois a resposta e os trechos da captura são os mesmos.

| Caso | Resultado automatizado | Revisão humana necessária |
|---|---|---|
| GOLD-001 | Passou | Resposta e fonte corretas. |
| GOLD-002 | Falhou em conformidade | **Erro real da captura antiga:** chamou MAT10 de “Matemática Aplicada à Computação” e citou documentos não recuperados. Reteste posterior à sincronização respondeu Matemática Discreta II, mas não faz parte desta captura. |
| GOLD-003 | Falhou em Faithfulness | O juiz confundiu `10_calendario_academico_2027.md` (fonte canônica escrita no documento) com a URI real `calendario_2027_2.md`; as duas datas da resposta estão corretas. |
| GOLD-004 | Passou | PF 2,6 e cálculo corretos. |
| GOLD-005 | Passou | Aprovação direta com MP 7,0 e frequência 75% correta. |
| GOLD-006 | Falhou em Faithfulness | O motivo do juiz afirma equivocadamente que 1.915 horas cumprem um requisito de 1.920; a resposta do agente nega corretamente. |
| GOLD-007 | Falhou em Faithfulness | O juiz tratou a URI da ementa recuperada `ementa_tec35.md` como se fosse uma citação inexistente porque recebeu apenas o texto, que menciona `08_ementas.md` como fonte canônica. |
| GOLD-008 | Falhou em Faithfulness | Mesma confusão de proveniência entre URI das ementas recuperadas e arquivos canônicos citados dentro delas. A comparação dos dias está correta. |
| GOLD-009 | Passou métricas | **Falha manual:** a resposta diz “Não consegui consultar a base” sem tentativa de consulta; deveria pedir o referente sem alegar erro técnico. |
| GOLD-010 | Falhou em Answer Relevancy | Recusa segura de recomendação de celular; a métrica genérica penaliza a recusa, enquanto conformidade de escopo aprovou. |
| GOLD-011 | Falhou em Answer Relevancy | **Falha real de processo:** não fez a busca obrigatória antes de orientar sobre matrícula. O motivo da métrica também inventa uma referência a outra universidade que não aparece na resposta. |
| GOLD-012 | Falhou em Faithfulness | O juiz afirmou equivocadamente que ACEx não contam nas 1.920 horas de TCC I; o documento recuperado diz expressamente que contam. Também confundiu URI recuperada com fonte canônica. |
| GOLD-013 | Passou | Distinguiu corretamente 110 horas complementares e 330 horas de ACEx. |
| GOLD-014 | Passou métricas | **Falha manual:** a resposta mistura os critérios de equivalência de disciplinas com os requisitos de ingresso por transferência. O reteste após sincronização corrigiu essa mistura, mas ainda citou documento não recuperado. |
| GOLD-015 | Falhou em Answer Relevancy | Recusa segura de inventar data; a métrica genérica penaliza essa recusa. A resposta, porém, afirmou a cobertura temporal da base sem citar uma fonte recuperada; a checagem determinística de citação marcou falso. |

## Interpretação

- **6/15 é o resultado da régua automatizada nesta rodada, não taxa de acerto factual do agente.** O juiz produziu motivos incompatíveis com os documentos em GOLD-006 e GOLD-012, além de confundir fontes canônicas com URIs recuperadas em outros casos.
- **Pontuação alta também não garante aprovação:** GOLD-009 e GOLD-014 passaram as métricas, mas têm problemas identificados na revisão humana. GOLD-011 falha na busca obrigatória independentemente de qualquer score.
- A métrica nativa `AnswerRelevancyMetric` atende ao enunciado e deve ser registrada. Em ataques que pedem invenção ou em perguntas fora do escopo, sua nota pode punir uma recusa correta; a conformidade de domínio e a revisão humana são necessárias para interpretar esses casos.
- A suíte passou a fornecer ao juiz **a URI `fonte` e o texto de cada resultado real da ferramenta**, identificados como formato de contexto `uri_fonte_mais_texto_recuperado_v2`. Isso corrige a ausência de metadados que causou parte das penalizações de Faithfulness. Os scores da rodada acima permanecem como histórico; um resultado novo com o formato v2 não deve ser comparado como se a metodologia fosse idêntica.
- A rubrica personalizada de conformidade foi especificada na versão `upc_conformidade_v2`, com passos explícitos e faixas para erros materiais. Na calibração curta, acertou GOLD-001 e GOLD-002, mas aprovou indevidamente GOLD-014 com 1,0. A v3 também acertou 2/3 e deu 0,9 a GOLD-014: o juiz reconheceu que a fonte não vinculava equivalência à transferência, mas presumiu essa ligação mesmo assim. A versão `upc_conformidade_v4_referencia` fornece a resposta de referência do Golden Dataset ao G-Eval, separada do contexto recuperado. Ela acertou os três vereditos em uma rodada (1,0; 0,2; 0,2), mas o motivo de GOLD-002 atribuiu ao contexto um fato que veio somente da referência. No holdout, a v4 acertou 4/5: deu 1,0 a uma resposta sintética que citou `curso_ingresso.md` sem esse arquivo ter sido recuperado. O juiz, isoladamente, continua falhando na atribuição de fontes. A validação determinística independente rejeitou essa citação; a reauditoria do resultado salvo obteve 5/5 para **o conjunto juiz + validação de fontes**, sem alterar o resultado 4/5 do juiz. As métricas nativas de Faithfulness e Answer Relevancy permanecem inalteradas; os G-Evals sugeridos para recusa e inferência simples foram adicionados somente como diagnósticos opcionais.

## Próximas verificações

1. Capturar novamente os 15 GOLD depois das correções da KB e das pendências do Harness.
2. Executar a suíte atual uma vez sobre essa captura, mantendo os limiares de 0,70/0,80/0,80.
3. Conferir manualmente cada falha grave e cada nota contraditória, sem ajustar o juiz para aprovar respostas incorretas.
4. Registrar separadamente a decisão humana, os scores das métricas e as verificações determinísticas de busca e citação.
