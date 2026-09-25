# Revisão da captura do Harness — 24/09/2026

**Captura atual:** `output/capturas/harness_20260924T211251Z_7ddd9cd3.json`  
**Estado:** concluído, 15 casos GOLD, modelo `qwen.qwen3-next-80b-a3b`.  
**Avaliação colada após a captura:** `output/avaliacoes/deepeval_suite_20260924T211514Z_536515be.json`, que aponta para a captura **anterior** `harness_20260924T153740Z.json`. Seus scores não avaliam as respostas atuais.

## Revisão direta da captura atual

| Caso | Observação | Classificação preliminar |
|---|---|---|
| GOLD-002 | A resposta diz que MAT10 é Matemática Discreta II. O trecho recuperado de `ementa_cco33.md` contém explicitamente esse nome após a atualização da KB. | Informação sustentada. |
| GOLD-006 | Conclusão e diferença de 5 horas corretas. A explicação lista disciplinas obrigatórias e optativas, mas omite ACEx, que também contam para as 1.920 horas segundo `tcc.md`. | Resposta incompleta; corrigir redação do agente. |
| GOLD-009 | Em sessão sem referente para “ela”, não houve chamada à ferramenta. A resposta diz “Não consegui consultar a base”, o que a captura não confirma. | Falha de comunicação; deve pedir o referente sem alegar falha técnica. |
| GOLD-011 | Pedido de executar matrícula recebeu recusa adequada, mas a busca marcada como obrigatória no dataset não ocorreu. A resposta acrescenta orientação sobre pré-requisitos e prazo sem consulta. | Falha de processo conforme o critério do caso. |
| GOLD-014 | A regra geral de transferência por edital aparece em trechos recuperados, mas a resposta cita `01_curso_e_ingresso.md`, que não foi retornado. Também sugere possíveis critérios do edital (histórico/desempenho) sem suporte nos trechos. | Fonte não recuperada e detalhe especulativo. |
| GOLD-015 | Recusa corretamente inventar data de 2028.2, mas não identifica uma das fontes recuperadas ao afirmar a cobertura do calendário. | Falha de citação. |

Os demais casos não mostraram erro evidente nesta leitura preliminar. Uma revisão final deve conferir as respostas completas, os trechos integrais e os rastros de ferramenta.

## Próxima avaliação

O critério `CRITERIO_FUNDAMENTACAO_LOGICA` havia recebido texto de relevância por engano e foi restaurado. Ele pertence apenas ao G-Eval diagnóstico opcional; com `UPC_DEEPEVAL_DIAGNOSTICOS=0`, não altera Faithfulness nativa nem os testes principais. A suíte agora bloqueia uma seleção antiga em `UPC_DEEPEVAL_CAPTURE` quando há captura completa mais recente. Para avaliar esta captura, selecione explicitamente `harness_20260924T211251Z_7ddd9cd3.json` e confira o caminho impresso antes de interpretar scores.
