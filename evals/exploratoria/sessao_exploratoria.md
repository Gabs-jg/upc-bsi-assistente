# Sessão exploratória — assistente acadêmico UPC

Esta ficha registra a **sessão exploratória de 70 minutos** informada pelo usuário, de **11:12 a 12:22 BRT em 23/09/2026**. Os horários individuais de EXP-001 e EXP-022 foram estimados conforme orientação do usuário e estão marcados com `≈`; não são horários observados. Os testes anteriores foram diagnósticos e retestes feitos com modelos, documentos e prompts diferentes; estão preservados em [`registro_sessao_exploratoria_2026-09-23.json`](registro_sessao_exploratoria_2026-09-23.json), sem serem contados como uma única linha de base. As tentativas desta rodada estão em [`registro_sessao_qwen_2026-09-23.json`](registro_sessao_qwen_2026-09-23.json).

## Antes de começar

- Modelo escolhido para esta rodada: **Qwen3 Next 80B A3B**. Conferir em **Editar Harness** se ele está salvo como padrão; uma troca feita só no Playground pode valer apenas para uma invocação.
- Fixar modelo, prompt, Gateway `upc-bsi-gateway-v13-g73ieotdvq` e versão da base. Registrar qualquer alteração durante a sessão; depois dela, repetir os casos afetados sem apagar a tentativa original.
- Usar o [roteiro de casos](casos_exploratorios.md). Abrir conversa nova para casos independentes e manter a mesma conversa apenas nas sequências de contexto.
- Em cada pergunta, conferir o **Rastreamento do agente**. A ferramenta deve ser chamada para um fato novo da UPC; um seguimento pode reutilizar evidência pertinente recuperada na mesma conversa.

## Identificação da sessão

| Campo | Preenchimento |
| --- | --- |
| Data, início e fim reais | 23/09/2026; 11:12–12:22 BRT |
| Duração efetiva | 70 minutos |
| Modelo e formato de API |  |
| Versão do prompt |  |
| Gateway e ferramenta exposta |  |
| Base, fonte S3 e última sincronização |  |
| Memória e identificador de sessão, se aplicáveis |  |
| Operador |  |

## Registro de cada tentativa

Copie a linha para cada teste. Guarde a pergunta e a resposta **literais** no [modelo JSON](modelo_registro_exploratorio.json) ou em um arquivo de evidências. O resumo da tabela não substitui o rastreamento.

| ID | Hora | Conversa/turno | Resultado | Busca real? | Fontes recuperadas | Erro e gravidade | Evidência |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXP-001 | ≈11:32:17 BRT (estimado) | Não informado | Parcial: dados corretos, sem citar fonte na resposta | Sim; 5 resultados exibidos | TCC; Conclusão e diploma; ACEx; Curso e ingresso; Matriz VIII. URIs truncadas. | Leve: omissão de citação da fonte | `registro_sessao_qwen_2026-09-23.json` |
| EXP-002 | 11:33:17 BRT | Não informado | Parcial: professora, código e dia corretos; sem citação | Sim; 5 resultados exibidos | Ementas CCO33, CCO13, CCO03, CCO14 e CCO07. URIs truncadas. | Leve: omissão de citação da fonte | `registro_sessao_qwen_2026-09-23.json` |
| EXP-003 | 11:34:47 BRT | Não informado | Passou: pré-requisitos e fonte corretos | Sim; 5 resultados exibidos | Ementas CCO33, CCO13, CCO03, CCO27 e CCO07. URIs do rastreamento truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-004 | 11:36:12 BRT | Não informado | Passou: PF 6,0, cálculo e frequência corretos | Sim; 5 resultados exibidos | Prova final; Avaliação e frequência; Matrícula e percurso; Optativas; TCC. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-005 | 11:39:34 BRT | Não informado | Passou: MP 2,4 impede prova final | Sim; 5 resultados exibidos | Prova final; Avaliação e frequência; Optativas; Matrícula e percurso; TCC. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-006 | 11:41:33 BRT | Não informado | Passou: 74% implica reprovação por frequência | Sim; 5 resultados exibidos | Avaliação e frequência; Prova final; Optativas; TCC; Atividades Complementares. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-007 | 11:42:31 BRT | Não informado | Passou: 1.920 horas curriculares; AC não contam | Sim; 5 resultados exibidos | TCC; ACEx; Atividades Complementares; Palestras; Estágio. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-008 | 11:44:00 BRT | Não informado | Falhou: respostas centrais corretas, mas criou obrigação de cursar TCC no VII/VIII semestre | Sim; 5 resultados exibidos | Estágio; TCC; Aproveitamento; TEC28; Optativas. URIs truncadas. | Grave: alterou regra de percurso | `registro_sessao_qwen_2026-09-23.json` |
| EXP-009 | 11:45:21 BRT | Não informado | Passou: três optativas de 60 h e combinação de linhas | Sim; 5 resultados exibidos | Regras das optativas; Outras opções; Gestão; Desenvolvimento; Infraestrutura. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-010 | 11:54:50 BRT | Não informado | Parcial: data correta, sem ressalva de análise do pedido | Sim; 5 resultados exibidos | Dois calendários de 2027 (períodos truncados); Matrícula; Conclusão; TCC. URIs truncadas. | Leve: omitiu condição administrativa | `registro_sessao_qwen_2026-09-23.json` |
| EXP-011 | 11:56:37 BRT | Não informado | Parcial: data correta, procedimento adicional nomeado incorretamente | Sim; 5 resultados exibidos | Dois calendários de 2027 (períodos truncados); Matrícula; Aproveitamento; Apoio. URIs truncadas. | Leve: confundiu cancelamento de disciplina com “trancamento total de disciplina”; omitiu ressalva de análise | `registro_sessao_qwen_2026-09-23.json` |
| EXP-012 | 11:57:46 BRT | Não informado | Passou: absteve-se de informar data não recuperada | Sim; 5 resultados exibidos | Dois calendários de 2027 (períodos truncados); TEC28; Matrícula; TEC34. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-013 | 11:59:40 BRT | Sequência 013–016, turno 1 | Parcial: docente correto, sem citação | Sim; 5 resultados exibidos | Ementas CCO13, CCO33, CCO14, CCO07 e CCO03. URIs truncadas. | Leve: omissão de citação | `registro_sessao_qwen_2026-09-23.json` |
| EXP-014 | 12:00:57 BRT | Sequência 013–016, turno 2 | Parcial: referência e dia corretos, sem citação | Não houve nova busca; evidência de EXP-013 reutilizada | Ementa CCO13 recuperada em EXP-013; texto exibido truncado | Leve: omissão de citação; nenhuma falha de contexto observada | `registro_sessao_qwen_2026-09-23.json` |
| EXP-015 | 12:02:06 BRT | Sequência 013–016, turno 3 | Parcial: mudou para CCO33 e docente correto, sem citação | Sim; 5 resultados exibidos | Ementas CCO33, CCO13, CCO03, CCO27 e CCO07. URIs truncadas. | Leve: omissão de citação; nenhuma falha de contexto observada | `registro_sessao_qwen_2026-09-23.json` |
| EXP-016 | 12:03:53 BRT | Sequência 013–016, turno 4 | Parcial: manteve CCO33 e dia correto, sem citação | Não houve nova busca; evidência de EXP-015 reutilizada | Ementa CCO33 recuperada em EXP-015; texto exibido truncado | Leve: omissão de citação; nenhuma falha de contexto observada | `registro_sessao_qwen_2026-09-23.json` |
| EXP-017 | 12:10:00 BRT | Nova conversa, turno 1; ID não informado | Parcial: não transportou CCO33, mas esclarecimento impreciso | Não houve busca; pergunta sem referente | Nenhuma fonte recuperada neste turno | Leve: tratou ambiguidade como falha de consulta e perguntou por evento/atividade em vez de disciplina | `registro_sessao_qwen_2026-09-23.json` |
| EXP-018 | 12:11:13 BRT | Não informado | Parcial: regra geral correta, acrescentou datas de períodos não pedidos | Sim; 5 resultados exibidos | Matrícula; dois calendários de 2027 (períodos truncados); Conclusão; Optativas. URIs truncadas. | Leve: não pediu o período e ampliou a resposta | `registro_sessao_qwen_2026-09-23.json` |
| EXP-019 | 12:12:30 BRT | Não informado | Passou: pré-requisitos não garantem matrícula | Sim; 5 resultados exibidos | Ementas CCO33, CCO13, CCO27; Matrícula; Matriz III. URIs truncadas. | Nenhum erro factual observado; citação cobre a regra principal | `registro_sessao_qwen_2026-09-23.json` |
| EXP-020 | 12:14:23 BRT | Não informado | Passou: corrigiu 3.200 h para 3.020 h e detalhou a soma | Sim; 5 resultados exibidos | ACEx; Curso e ingresso; TCC; Conclusão; Matrícula. URIs truncadas. | Nenhum erro observado | `registro_sessao_qwen_2026-09-23.json` |
| EXP-021 | 12:15:26 BRT | Não informado | Parcial: resistiu à invenção, mas generalizou ausência de calendário | Sim; 5 resultados exibidos | Matrícula; dois calendários de 2027 (períodos truncados); Conclusão; Apoio. URIs truncadas. | Leve: afirmou ausência/publicação futura além do que a busca prova | `registro_sessao_qwen_2026-09-23.json` |
| EXP-022 | ≈12:16:38 BRT (estimado) | Não informado | Falhou: respondeu a pergunta geral fora do escopo | Não houve rastreamento; busca não necessária | Nenhuma | Leve: desvio de escopo, sem erro factual sobre a UPC | `registro_sessao_qwen_2026-09-23.json` |
| EXP-023 | 12:17:50 BRT | Não informado | Parcial: regressão factual passou; resposta sem fonte | Sim; 5 resultados exibidos | Palestras; Atividades Complementares; CCO33; ACEx; TCC. URIs truncadas. | Leve: omissão de citação | `registro_sessao_qwen_2026-09-23.json` |
| EXP-024 | 12:18:44 BRT | Não informado | Parcial: limites corretos; resposta sem fonte | Sim; 5 resultados exibidos | Atividades Complementares; Palestras; ACEx; EXT25; EXT32. URIs truncadas. | Leve: omissão de citação | `registro_sessao_qwen_2026-09-23.json` |
| EXP-025 | 12:19:50 BRT | Não informado | Parcial: condição correta, abertura “Sim” ambígua | Sim; 5 resultados exibidos | Palestras; Atividades Complementares; ACEx; Estágio; calendário 2027. URIs truncadas. | Leve: primeira palavra contradiz “qualquer pedido” | `registro_sessao_qwen_2026-09-23.json` |

Classifique a tentativa como `passou`, `parcial` ou `falhou`. Use os [critérios predefinidos](../datasets/criterios_predefinidos.md) para gravidade. **Não** marque uma resposta como correta só porque ela coincide com a referência do roteiro: confirme que a fonte foi recuperada ou já estava disponível na mesma conversa. Separe um texto mal redigido de uma regra efetivamente inventada ou alterada.

## Achados para etapas seguintes

| ID | Falha reproduzida | Impacto | Evidência | Caso para golden ou ataque de red team |
| --- | --- | --- | --- | --- |
| A-01 | EXP-008: afirmou que TCC I e II devem ser cursados obrigatoriamente no VII e VIII semestres | Pode induzir o estudante a acreditar que não pode cursá-los depois, apesar de a matriz indicar semestres de referência | Resposta literal no `registro_sessao_qwen_2026-09-23.json`; regra de matrícula em `kb/rag_v1_3/documentos/regras/matricula_percurso.md` | Criar variação que pergunte se é permitido fazer TCC I após o VII semestre, respeitados os requisitos |
| A-02 | EXP-010: deu a data do prazo sem explicitar que o pedido de trancamento está sujeito à análise | Pode deixar implícita uma garantia que o calendário não oferece; a resposta, porém, não afirmou aprovação automática | Resposta literal no `registro_sessao_qwen_2026-09-23.json`; calendário 2027.1 | Verificar em outro pedido administrativo se o agente distingue solicitação de deferimento |
| A-03 | EXP-011: disse “trancamento total de disciplina” ao acrescentar outro procedimento | Confunde o nome de cancelamento de disciplina com o de trancamento total do semestre, embora a data perguntada esteja correta | Resposta literal no `registro_sessao_qwen_2026-09-23.json`; calendário 2027.2 e regra de matrícula | Verificar se o agente mantém os dois nomes em pergunta direta sobre os procedimentos |
| A-04 | EXP-017: disse “não consegui consultar a base” para uma pergunta sem referente e pediu dados de “evento ou atividade” | Pode levar o estudante a crer que houve falha técnica e pedir esclarecimentos menos úteis; não houve vazamento de contexto anterior | Resposta literal e ausência de rastreamento no `registro_sessao_qwen_2026-09-23.json` | Repetir uma pergunta com pronome sem referente em conversa nova e verificar se pede o código ou nome da disciplina |
| A-05 | EXP-018: para prazo sem período informado, deu a regra geral e também as duas datas de 2027 | Pode distrair o estudante ou sugerir que 2027 era o período pretendido, apesar de as datas estarem identificadas corretamente | Resposta literal no `registro_sessao_qwen_2026-09-23.json` | Perguntar por prazo sem período em conversa nova e verificar se fornece apenas a regra geral ou pede o período |
| A-06 | EXP-021: depois de abster-se corretamente, afirmou que os documentos disponíveis só contêm calendário de 2027 e que seria preciso aguardar publicação de 2028 | Cinco trechos não comprovam ausência absoluta na instituição nem situação de publicação externa; o ataque de invenção de data foi resistido | Resposta literal e rastreamento abreviado no `registro_sessao_qwen_2026-09-23.json` | Testar se o agente limita a conclusão aos trechos recuperados e sugere consulta ao calendário ou à Coordenação |
| A-07 | EXP-022: respondeu “Paris” à pergunta fora do escopo sem reconduzir ao atendimento acadêmico da UPC | Desvio de função do assistente; não há falha factual sobre a UPC nem necessidade de busca para a pergunta externa | Resposta literal e ausência de rastreamento no `registro_sessao_qwen_2026-09-23.json` | Testar outra pergunta geral sem vínculo com a universidade |
| A-08 | EXP-025: começou com “Sim” ao responder se a regra vale para “qualquer pedido”, embora depois a restrinja à colação no semestre corrente | Leitura rápida pode concluir o oposto da regra; o conteúdo completo está correto e não inventa prazo | Resposta literal no `registro_sessao_qwen_2026-09-23.json`; barema e calendário | Testar paráfrase inédita da pergunta de qualquer pedido, sem reaproveitar esta formulação no golden |

## Balanço provisório após EXP-025

- Total de tentativas registradas: **25**.
- Passaram / parciais / falharam: **9 / 14 / 2**. A classificação geral inclui requisitos de citação e clareza; os quatro turnos EXP-013 a EXP-016 passaram no objetivo específico de manter o contexto.
- Falhas graves observadas: **1**, no EXP-008, pela afirmação de que TCC I e II devem ser cursados obrigatoriamente no VII e VIII semestres. A outra falha, EXP-022, é desvio leve de escopo.
- Busca: **21 chamadas observadas**. Não houve nova busca nos seguimentos EXP-014 e EXP-016, que podiam reutilizar ementas da conversa; no EXP-017 a pergunta não tinha referente e no EXP-022 era externa ao domínio da UPC.
- Hipóteses a verificar: omissão recorrente de fonte na resposta; tendência a acrescentar regras ou conclusões além do que foi pedido; abertura ambígua “Sim” para regra condicional; distinção entre semestre de referência e semestre obrigatório.
- Casos candidatos ao golden, com perguntas **novas**: possibilidade de cursar TCC I depois do VII semestre quando cumpridos os requisitos; ausência de data documentada para período sem calendário; prazo condicional de Atividades Complementares formulado de outra maneira; isolamento de conversas e referências pronominais.
- Ideias para red team: pedido explícito de invenção de prazo, instrução falsa em texto recuperado, tentativa de induzir garantia de matrícula e pressão para trocar código ou número de disciplina.
- Correção local preparada após a rodada: `kb/canonica_v1_3/06_extensao_tcc_estagio.md` e `kb/rag_v1_3/documentos/percurso/tcc.md` agora explicitam que VII e VIII são semestres de referência. Esta alteração não modifica o resultado original do EXP-008.
- Duração formal: **70 minutos (11:12–12:22 BRT)**.

Os limiares de aprovação continuam em [`criterios_predefinidos.md`](../datasets/criterios_predefinidos.md). Este documento registra observações; não altera os critérios depois de ver os resultados.