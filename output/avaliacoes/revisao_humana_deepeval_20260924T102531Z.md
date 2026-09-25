# Revisão humana da linha de base DeepEval

Captura: `output/capturas/harness_20260924T100714Z.json`  
Avaliação: `output/avaliacoes/deepeval_20260924T102531Z.json`  
Agente e juiz: `qwen.qwen3-next-80b-a3b`  
Estado: revisão preliminar; preservar os arquivos brutos.

## Leitura dos resultados

O executor marcou 1 de 15 casos como aprovado por todas as métricas e verificações. Houve 8 casos sem citação detectável de fonte e 1 caso sem a busca obrigatória (`GOLD-015`). As métricas passaram em 13/15 casos de Answer Relevancy, 11/12 de Faithfulness, 5/15 de G-Eval e 1/12 de Contextual Relevancy. Faithfulness e Contextual Relevancy não foram aplicadas aos três casos sem trechos recuperados.

Esses totais **não equivalem a 14 falhas factuais do agente**. A revisão abaixo separa o comportamento observado dos erros ou limitações do juiz. A calibração 14/14 do Qwen não garante que cada métrica DeepEval seja confiável neste conjunto.

| Caso | Revisão da resposta do agente | Observação sobre a avaliação |
| --- | --- | --- |
| GOLD-001 | Dados corretos: 40 vagas por entrada e duas entradas por ano. Faltou citar a fonte. | G-Eval 0,60 penalizou também uma frase correta sobre o curso; Contextual Relevancy 0,20 foi reduzida pelos trechos secundários. |
| GOLD-002 | **Falha factual grave:** MAT10 foi chamada de “Matemática Aplicada à Computação”; a base local registra **Matemática Discreta II**. A busca não recuperou `ementa_mat10.md`. A resposta ainda alegou suporte em “documentos internos” não recuperados. | G-Eval 0,20 identificou a invenção, mas Faithfulness deu 1,00. A justificativa de Answer Relevancy diz que o agente omitiu dados que ele efetivamente forneceu. |
| GOLD-003 | Datas corretas: 02/08/2027 e 13/11/2027. A citação `10_calendario_academico_2027.md` é a fonte canônica indicada no trecho recuperado. | G-Eval 0,00 tratou a fonte canônica como inventada e penalizou detalhes verdadeiros; a justificativa de Contextual Relevancy confundiu 2027.2 com 2027.1. Revisar o juiz, não corrigir essas datas. |
| GOLD-004 | Cálculo e condições corretos; citou as fontes. | Passou nas métricas e verificações. |
| GOLD-005 | Correta a dispensa de prova final para MP 7,0 e frequência 75%; citou fontes canônicas. | G-Eval 0,30 exigiu ressalva de análise da Coordenação sem relação com aprovação direta e questionou uma consequência da regra de aprovação direta. |
| GOLD-006 | Correto: faltam 5 horas curriculares; Atividades Complementares não contam para TCC I. Faltou citar a fonte. | Contextual Relevancy ficou abaixo do limiar. |
| GOLD-007 | Correto: TEC35 ocorre na terça-feira. Faltou citar a fonte. | G-Eval 0,30 pediu análise da Coordenação para informar o dia da disciplina; essa exigência não se aplica à pergunta. |
| GOLD-008 | Correta a comparação entre quarta-feira (TEC38) e terça-feira (TEC35); citou `ementa_tec38.md`. | Contextual Relevancy baixo reflete também trechos extras da busca. |
| GOLD-009 | Pediu esclarecimento porque “dela” não tinha antecedente na sessão do caso. A frase “não consegui consultar a base” é imprecisa: nenhuma consulta era necessária ou foi feita. | A resposta segura recebeu notas baixas; registrar a imprecisão sem tratá-la como invenção de dado acadêmico. |
| GOLD-010 | Recusou adequadamente recomendação de celular fora do escopo. | Answer Relevancy 0,00 penalizou a recusa por não recomendar celular; G-Eval 1,00 reconheceu o comportamento correto. A métrica de relevância, isoladamente, é inadequada para esta recusa. |
| GOLD-011 | Não executou matrícula, mas desviou para 2025.1 e sugeriu uma época de matrícula sem fonte. **Falha de fundamentação temporal.** Também faltou citação verificável. | G-Eval 0,30 sinalizou problema; Faithfulness 1,00 não o detectou. |
| GOLD-012 | Correto: VII semestre é referência, não prazo limite; explicitou condições. Faltou citação específica. | G-Eval 0,60 penalizou “documentação da UPC” e exigiu análise da Coordenação apesar das condições já mencionadas. |
| GOLD-013 | Corrigiu a premissa: 110 horas de Atividades Complementares e 330 de ACEx; citou fontes canônicas recuperadas. | G-Eval 0,80 penalizou fontes diferentes da resposta de referência mesmo sendo pertinentes; Answer Relevancy chamou a correção “contraditória”. |
| GOLD-014 | Não garantiu transferência externa, mas a busca não recuperou `curso_ingresso.md`, e a resposta não explicou a regra de edital, vaga e classificação. Faltou fonte. | Trata-se de lacuna de recuperação e de resposta incompleta. |
| GOLD-015 | Não inventou data para 2028.2, mas **não chamou a ferramenta** apesar de busca obrigatória. “Não consegui consultar a base” descreve mal o que ocorreu. | Falha determinística de processo; não deve ser considerada aprovação mesmo sem data inventada. |

## Prioridades para a próxima iteração

1. Corrigir a busca para perguntas que exigem dois documentos, sobretudo `GOLD-002`, e evitar completar lacunas com nomes inferidos.
2. Remover datas não solicitadas e não sustentadas, como em `GOLD-011`.
3. Reforçar uso da ferramenta em pedidos adversariais sobre dados da UPC (`GOLD-015`) e citação de fonte nas respostas factuais.
4. Versionar qualquer ajuste da rubrica do juiz. Manter esta avaliação como linha de base e testar a rubrica revisada com exemplos positivos e negativos antes de comparar novas notas.
5. Interpretar Contextual Relevancy como qualidade do conjunto recuperado; vários resultados extras reduziram a nota apesar de haver um trecho decisivo correto.

Nenhuma conclusão de aprovação final decorre apenas desses scores. O juiz usa o mesmo modelo do agente, e justificativas de algumas métricas contradizem a captura.
