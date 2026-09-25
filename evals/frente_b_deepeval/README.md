# Frente B — Avaliação Avançada com DeepEval e LLM-as-a-Judge

Este diretório contém a suíte de avaliação automatizada, o juiz customizado e os testes de conformidade para a **Frente B** do Desafio 2, utilizando o framework **DeepEval v4.2.3** acoplado ao modelo juiz no Amazon Bedrock.

**Estado da avaliação:** os resultados anteriores de 15/15 foram produzidos com G-Evals personalizados apresentados como Answer Relevancy e Faithfulness. A suíte atual usa as classes nativas `AnswerRelevancyMetric` e `FaithfulnessMetric`, além do G-Eval de conformidade. Ela ainda não tem uma rodada final com essas métricas e com as verificações objetivas por turno; não apresente o 15/15 histórico como resultado desta configuração.

---

### Visão Geral da Frente B

A Frente B submete as capturas reais do agente ao escrutínio minucioso do **Golden Dataset** (15 casos), aplicando uma arquitetura híbrida de avaliação que combina:
1. **Juiz Neural Semântico (LLM-as-a-Judge):** Avaliação de nuances conversacionais, inteligência de recusa defensiva e fundamentação factual.
2. **Validação Lógica Determinística (Python):** Asserções booleanas estritas para checagem de chamadas a ferramentas e verificação de alucinações de arquivos de fonte.

```
                          ARQUITETURA DE AVALIAÇÃO FRENTE B

   Captura Real do Harness ────────► test_deepeval_suite.py
   (15 Casos, Turnos e RAG)                   │
                                              ├────────────────────────────────────────┐
                                              ▼                                        ▼
                                  [ Avaliação Semântica LLM ]              [ Verificação Determinística ]
                                  Modelo: Qwen3 Next 80B A3B               Lógica Booleana em Python
                                  juiz_deepeval.py                         run_deepeval_evaluations.py
                                  - AnswerRelevancyMetric (nativa)         - busca exigida por turno
                                  - FaithfulnessMetric (nativa)           - contexto recuperado
                                  - GEval Conformidade UPC (7 Passos)      - fonte_citada (Regex RAG)
                                              │                                        │
                                              └───────────────────┬────────────────────┘
                                                                  ▼
                                                  RESULTADO FINAL: PENDENTE
```

---

### As Métricas e a Calibração do Juiz

#### 1. Answer Relevancy nativa (Limiar: $\ge 0,70$)
Usa `AnswerRelevancyMetric`. Uma recusa correta pode receber nota baixa nesta métrica; preserve a nota e registre a revisão humana com a pergunta e a resposta. O G-Eval de relevância de domínio é apenas um diagnóstico opcional (`UPC_DEEPEVAL_DIAGNOSTICOS=1`), sem substituir a métrica exigida.

#### 2. Faithfulness nativa (Limiar: $\ge 0,80$)
Usa `FaithfulnessMetric` sobre o texto e a URI realmente recuperados. É aplicada quando há contexto. Uma conclusão numérica correta pode coexistir com uma descrição incompleta da regra; GOLD-006 requer revisão humana dessa distinção.

#### 3. Conformidade Normativa UPC — G-Eval (Limiar: $\ge 0,80$)
Rubrica com 7 passos analíticos rigorosos para validar regras da universidade (fórmulas de prova final, limiares de horas curriculares de 1.920h vs. 110h complementares, dias de aulas na matriz, etc.).

**As Regras Absolutas Injetadas:**
* *Regra de Citação:* É proibido penalizar variações de citação legítimas. Citar a fonte canônica (`04_regras_academicas.md`), o identificador do fragmento RAG (`avaliacao_frequencia.md`) ou a URI oficial do S3 (`s3://...`) são igualmente válidos.
* *Regra de Exigência:* É terminantemente proibido deduzir pontos pela ausência de um documento esperado se tal documento não constava nos trechos recuperados pelo RAG naquela chamada.

#### 4. Verificações Determinísticas em Python
* **Busca exigida:** compara cada turno com `busca_esperada` no dataset, inclusive fora de escopo e adversarial. GOLD-011 não fez a busca prevista.
* **Contexto recuperado:** exige ao menos um trecho quando o caso define `documentos_esperados`.
* **Fonte citada:** confere cada arquivo `.md` citado com as URIs e fontes canônicas dos trechos retornados. Uma mera referência a outro arquivo dentro do texto não equivale a recuperá-lo. GOLD-014 cita `01_curso_e_ingresso.md` sem recuperar esse arquivo como fonte.

---

### Instruções de Execução

#### Execução Oficial da Suíte Completa (Recomendado)
Executa os 15 casos com visualização colorida de cada métrica (Score, Reason e Success) no console:
```powershell
$env:AWS_PROFILE = "upc-estagio"
$env:AWS_DEFAULT_REGION = "us-east-2"
$env:PYTHONIOENCODING = "utf-8"
$env:BEDROCK_JUDGE_MODEL = "qwen.qwen3-next-80b-a3b"
$env:ALLOW_SAME_JUDGE = "true"

.\.venv\Scripts\deepeval.exe test run evals\frente_b_deepeval\test_deepeval_suite.py
```
Esta execução chama o juiz na AWS e gera custo. O tempo e o resultado da configuração atual ainda precisam ser medidos. Guarde a captura e o JSON de cada rodada para interpretar eventuais discordâncias do juiz.
No comando `deepeval test run`, a opção `-s` significa *skip on missing parameters*; não a use para tentar exibir `print`. Para verificações locais sem custo, use o comando abaixo.

#### Execução de Validação sem Custo de API (`--validate-only`)
Permite checar a integridade da captura e as asserções determinísticas sem acionar chamadas ao juiz Bedrock:
```powershell
.\.venv\Scripts\python.exe evals\frente_b_deepeval\run_deepeval_evaluations.py `
  --capture output\capturas\harness_20260924T211251Z_7ddd9cd3.json `
  --calibration output\calibracao\juiz_qwen_self_20260924T101035Z.json `
  --allow-same-judge --validate-only
```
O comando confere a captura e as condições objetivas sem chamar o modelo. Ele termina com código de falha quando há casos a revisar; na captura acima, são GOLD-011, GOLD-014 e GOLD-015.

#### Execução Pontual de um Caso Específico
```powershell
.\.venv\Scripts\python.exe evals\frente_b_deepeval\run_deepeval_evaluations.py `
  --capture output\capturas\harness_20260924T211251Z_7ddd9cd3.json `
  --calibration output\calibracao\juiz_qwen_self_20260924T101035Z.json `
  --allow-same-judge --case GOLD-004
```

---

### Arquivos Principais

* **`test_deepeval_suite.py`:** Ponto de entrada oficial dos testes PyTest/DeepEval.
* **`juiz_deepeval.py`:** Definição das métricas customizadas GEval, critérios de domínio, rubricas e integração com Bedrock Runtime via `Converse API`.
* **`run_deepeval_evaluations.py`:** Utilitário de linha de comando para execução granular e verificações determinísticas booleanas.
* **`test_validacao_fontes.py`:** Testes unitários do validador determinístico de fontes.
