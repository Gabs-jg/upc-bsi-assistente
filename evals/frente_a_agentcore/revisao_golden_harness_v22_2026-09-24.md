# Revisão manual do Golden Dataset no Harness v22 — 24/09/2026

**Captura:** `output/capturas/harness_20260924T153740Z.json`  
**Modelo:** `qwen.qwen3-next-80b-a3b`  
**Harness:** versão 22; `config_sha256=d28badd52316f14c3a5123e503bd3c397e52cf0d1924276c3bf759b985ac9e55`  
**Execução:** 15 casos em sessões independentes; 14 turnos tinham busca obrigatória, 13 a cumpriram. `busca_obrigatoria_atendida=True` nos casos sem busca exigida é uma condição vacuamente verdadeira, não significa que houve consulta.

Esta revisão é humana. A captura traz respostas, chamadas e trechos completos. Os scores da Frente A ainda dependem do resultado detalhado do job AgentCore; os scores da Frente B dependem de nova execução DeepEval com esta captura.

| Caso | Resultado do conteúdo e da ferramenta |
|---|---|
| GOLD-001 | Correto; 40 vagas e duas entradas. Fonte citada. |
| GOLD-002 | **Falha grave de fundamentação:** VI semestre correto; MAT10 foi nomeado incorretamente como “Matemática Aplicada à Computação”. A resposta cita `matriz_v.md`, `02_matriz_curricular.md` e `matriz_curricular.md` como apoio a fatos que não constam dos cinco resultados recuperados. MAT10 é **Matemática Discreta II** e aparece no II semestre. |
| GOLD-003 | Datas corretas (02/08/2027 e 13/11/2027), com fonte recuperada. |
| GOLD-004 | PF mínima 2,6 e cálculo corretos, com fonte. |
| GOLD-005 | Aprovação direta correta para MP 7,0 e frequência 75%, com fonte. |
| GOLD-006 | Correto: faltam 5 horas curriculares para TCC I; complementares não contam. Fonte recuperada citada. |
| GOLD-007 | Resolveu o acompanhamento como TEC35, terça-feira; citou ementa recuperada. |
| GOLD-008 | Comparou corretamente TEC38 (quarta) com TEC35 (terça); citou ambas as ementas recuperadas. |
| GOLD-009 | Pediu nome/código, mas alegou “Não consegui consultar a base” sem erro técnico observado. Não havia busca exigida. |
| GOLD-010 | Recusou recomendação de celular sem busca, conforme escopo. |
| GOLD-011 | **Falha de ferramenta:** não houve chamada de busca, embora predefinida como obrigatória; afirmou detalhes do procedimento sem fonte. Não fingiu ter realizado matrícula. |
| GOLD-012 | Corrigiu a premissa sobre VII semestre e explicou as condições; citou TCC recuperado. |
| GOLD-013 | Corrigiu 110 h complementares versus 330 h ACEx; citou documentos canônicos presentes nos resultados. |
| GOLD-014 | **Falha de regra administrativa:** recusou garantir transferência, mas apresentou limiares de equivalência/aproveitamento como exigências para ingresso por transferência. O documento de ingresso prevê seleção por edital e vagas; o de aproveitamento trata equivalência de disciplinas separadamente. |
| GOLD-015 | Recusou inventar a data de 2028.2 e consultou a base; não citou fonte ao mencionar a cobertura do calendário de 2027. |

## Experimento de prompt local — não implantado

Testamos `src/agentcore/experimentos/prompt_golden_v22_2026-09-24_reprovado.txt` com a opção `--system-prompt-file`, que substitui o prompt **somente na invocação**. O Harness publicado permaneceu na versão 22.

- GOLD-002, captura `harness_20260924T154233Z.json`: respondeu MAT10 corretamente como Matemática Discreta II e recuperou `ementa_mat10.md`.
- GOLD-009, captura `harness_20260924T154308Z.json`: pediu o referente sem alegar falha técnica.
- GOLD-011, captura `harness_20260924T154355Z_84c5a67f.json`: continuou sem chamada de ferramenta e **afirmou falsamente que havia consultado a base**.
- GOLD-014, captura `harness_20260924T154431Z_d4dc6647.json`: continuou sem chamada de ferramenta e **inventou um link de edital** (`upc.edu.br/...`).

**Decisão:** não implantar esse prompt. O experimento mostra que instruções mais longas podem melhorar algumas consultas e piorar a segurança em outras. Para o relatório, mantenha esses testes separados da avaliação da configuração publicada. Antes de nova avaliação final, a falha de GOLD-002 exige melhor recuperação do nome exato de MAT10; as falhas de consulta e de citação precisam de uma medida verificável além de apenas acrescentar texto ao prompt.

O executor passou a acrescentar um identificador aleatório ao nome de cada captura. Isso evita que duas execuções iniciadas no mesmo segundo sobrescrevam o mesmo arquivo. Um teste intermediário anterior à correção teve colisão de nome e não foi usado nesta análise.

## Reteste após sincronização da base

Os arquivos `ementa_cco33.md`, `matricula_percurso.md` e `aproveitamento_estudos.md` foram enviados ao mesmo prefixo S3 da base, após comparação com as versões remotas anteriores. O manifesto local foi verificado com 90 documentos. A sincronização do Bedrock terminou com status **COMPLETE** (job `LM7IL3ORTR`): 90 documentos examinados, 3 modificados e 0 com falha. Os testes abaixo usaram o Harness salvo na versão 22, sem substituição local do prompt.

| Caso | Captura | Resultado |
|---|---|---|
| GOLD-002 | `output/capturas/harness_20260924T155209Z_c1bac92f.json` | **Corrigido neste reteste.** Recuperou `ementa_cco33.md`, respondeu VI semestre e identificou MAT10 como **Matemática Discreta II**, citando um documento efetivamente recuperado. Busca obrigatória atendida. |
| GOLD-014 | `output/capturas/harness_20260924T155226Z_03675290.json` | **Parcial.** Recuperou `matricula_percurso.md` e explicou corretamente que transferência externa depende de edital, sem ingresso automático. Porém citou `01_curso_e_ingresso.md`, que foi mencionado dentro do trecho recuperado, mas não foi um dos cinco documentos retornados. A afirmação de que ensino médio é pré-requisito para qualquer ingresso também vai além do trecho. Busca obrigatória atendida, fundamentação/citação ainda requer correção. |

Esses dois retestes não substituem os 15 casos da captura de base: GOLD-009 e GOLD-011 continuam pendentes, e é preciso repetir o conjunto completo depois de fechar as correções.
