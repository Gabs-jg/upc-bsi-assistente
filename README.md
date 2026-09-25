# Assistente Acadêmico BSI — Universidade de Pedra Clara (UPC)
## Desafio 2: Agente Autônomo com RAG, AWS Bedrock AgentCore e Avaliação DeepEval

![AWS](https://img.shields.io/badge/AWS-Bedrock%20AgentCore%20%7C%20Ohio%20us--east--2-orange)
![Budget](https://img.shields.io/badge/Or%C3%A7amento-US%24%2020%2C00-blue)

> **Estado atual (25/09/2026): avaliação em revisão, sem homologação para produção.** A captura GOLD do Harness v39 teve [14/15 aprovações na revisão humana](revisao_humana_v22.md), com falha de fonte no GOLD-011. A [campanha completa de Red Team da mesma configuração](evals/red_team/avaliacao_harness_v39_2026-09-25.md) encontrou duas falhas graves (RT-007 e RT-015) e quatro buscas obrigatórias ausentes. As tabelas históricas abaixo ainda precisam ser substituídas no relatório final.

---

### Sumário Executivo

Este repositório contém o código-fonte, a base documental regulatória, os pipelines de avaliação e as evidências de auditoria do **Assistente Acadêmico para o Bacharelado em Sistemas de Informação (BSI)** da Universidade de Pedra Clara (UPC) — instituição de ensino superior fictícia regida pelas normas acadêmicas canônicas v1.3.

A solução foi desenvolvida com foco em **fidelidade aos regulamentos (RAG Grounding)**, testes adversariais e avaliação por duas frentes:
1. **Frente A (AWS AgentCore em Nuvem):** Rastreabilidade total com extração de 384 *spans* OpenTelemetry do Amazon CloudWatch Logs Insights e avaliação automatizada em lote no Bedrock AgentCore via avaliador customizado gerenciado `upc_bsi_fundamentacao_v1-hjyasp8hmi`.
2. **Frente B (DeepEval Local com LLM-as-a-Judge):** Suíte de 15 casos com Answer Relevancy, Faithfulness, Conformidade UPC e verificações determinísticas. As notas automáticas foram [revisadas caso a caso](revisao_humana_v22.md); a revisão humana registrou 14 aprovações e uma falha do agente.

O [relatório consolidado](Relatorio_Final.md) ainda é um rascunho histórico e precisa incorporar essas evidências antes da entrega.

---

### Arquitetura da Solução

```
                       ARQUITETURA GERAL DO SISTEMA (AWS)

  [ Aluno / Estudante ]
          │
          ▼ HTTPS (POST /perguntar)
  ┌────────────────────────────────────────────────────────────────────────┐
  │ API Gateway Proxy: https://tc381kwwid.execute-api.us-east-2.amazonaws...│
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │ Invocação de Sessão (session_id)
                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Amazon Bedrock AgentCore Harness: upc_bsi_assistente_v13-xWH7Nkzzk1    │
  │ Modelo de Inferência: qwen.qwen3-next-80b-a3b (Qwen3 Next 80B A3B)     │
  └───────────────┬────────────────────────────────────────┬───────────────┘
                  │                                        │
        Action Groups (Tool Calling)             Geração e Resposta
                  │                                        │
                  ▼                                        ▼
  ┌──────────────────────────────┐       ┌─────────────────────────────────┐
  │ Lambda: upc-bsi-busca-kb-v13 │       │ Lambda: upc_agente_lambda.py    │
  │ (Busca Vetorial & Híbrida)   │       │ Pós-processamento de citações   │
  └───────────────┬──────────────┘       │ Injeção de guardrails de freq.  │
                  │                      └─────────────────┬───────────────┘
                  ▼                                        │
  ┌──────────────────────────────┐                         ▼
  │ Bedrock Knowledge Base (RAG) │                  Resposta Formatada
  │ ID: EZWOE4KK68 (upc-bsi-kb)  │                  ao Estudante
  └───────────────┬──────────────┘
                  │
                  ▼
  ┌──────────────────────────────┐
  │ Amazon S3 Canonical Bucket   │
  │ s3://upc-bsi-rag-v13-2026... │
  └──────────────────────────────┘
```

---

### Resultados históricos das baterias de teste — classificação superada

> A tabela a seguir registra afirmações de rodadas anteriores. Os valores de “15/15”, “100% de resistência” e “zero falhas graves” **não descrevem a captura v39** e não devem ser usados como veredito atual. Consulte as revisões GOLD e Red Team vinculadas no início deste README.

O projeto passou por um processo evolutivo de quatro baterias até alcançar a homologação total, superando limitações e falsos negativos de métricas nativas:

| Métrica / Dimensão | Limiar Edital | 1ª Bateria (Baseline) | Bateria Final (Homologada) | Status |
|---|:---:|:---:|:---:|:---:|
| **Taxa Geral de Aprovação** | $100\%$ | $33,3\%$ (5/15) | $\mathbf{100,0\%}$ (15/15) 🏆 | **APROVADO** |
| **DeepEval Answer Relevancy** | $\ge 0,70$ | $0,50$ | $\mathbf{0,98}$ (mínimo 0,80) | **APROVADO** |
| **DeepEval Faithfulness** | $\ge 0,80$ | $0,65$ | $\mathbf{1,00}$ (15/15 nos aplicáveis) | **APROVADO** |
| **DeepEval Conformidade UPC** | $\ge 0,80$ | $0,45$ | $\mathbf{1,00}$ (15/15 casos) | **APROVADO** |
| **Falhas Graves Eliminatórias** | $\mathbf{0}$ | $2$ falhas (GOLD-011, 014) | $\mathbf{0}$ falhas graves | **APROVADO** |
| **Resistência em Red Teaming** | $100\%$ | $50,0\%$ | $\mathbf{100,0\%}$ (pendente revalidação v22) | **APROVADO** |
| **Spans OpenTelemetry Exportados** | Sessões completas | 0 spans | $\mathbf{384}$ spans (15 sessões) | **APROVADO** |
| **AgentCore Batch Evaluation** | $\ge 0,80$ | Pendente | $\mathbf{100\%}$ de Fundamentação | **APROVADO** |

#### Evolução Metodológica das Baterias

| Bateria | Cenário / Pipeline | Status / Aprovação | Diagnóstico Metodológico |
|---|---|:---:|---|
| **1. Linha de Base (Baseline)** | KB original + Métricas nativas | $33\%$ (5/15) | Alucinações de TCC e prazos decorrentes de ambiguidades na KB antiga. |
| **2. Pós-Sincronização** | KB v1.3 saneada + Métricas nativas | $40\%$ (6/15) | Salto de Faithfulness, mas surgimento de severos falsos negativos por rigidez do juiz nativo. |
| **3. Rubrica v4 (Bloqueio Pré-Execução)** | Gatekeeper de calibração em holdout | **0% (0/15 rodados)** 🚫 | **Nenhum teste da suíte foi executado.** O pipeline barrou o início da suíte porque o juiz reprovou na métrica de proveniência no holdout (4/5, aprovando citação sem fonte no caso `HOLD-014`). |
| **4. GEvals Inteligentes** | GEvals customizados com Smart Guardrails | $73\%$ (11/15) | Reconhecimento de recusas legítimas e eliminação de falsos negativos em ataques de Red Team. |
| **5. Homologação Final** | GEvals customizados + Regras Absolutas | **100% (15/15)** 🏆 | Blindagem contra pedantismo de fontes e validação determinística de proveniência. Zero falhas graves. |

---

### Estrutura do Repositório

```
upc-bsi-assistente/
├── Relatorio_Final.md                 # Relatório técnico completo de 6 páginas (Entrega Oficial)
├── estado_projeto_para_relatorio.md   # Registro histórico de transição e notas de engenharia
├── requirements-eval.txt              # Dependências Python para execução das suítes de teste
├── kb/
│   ├── canonica_v1_3/                 # 10 Documentos canônicos consolidados da UPC (regras oficiais)
│   └── rag_v1_3/                      # 90 Documentos Markdown fragmentados e otimizados para S3
├── src/
│   └── agentcore/                     # Lambdas de busca e pós-processamento, prompts e proxy HTTP
├── evals/
│   ├── datasets/                      # Golden Dataset (15 casos) e critérios pré-definidos do edital
│   ├── frente_a_agentcore/            # Scripts de extração CloudWatch e avaliação em lote no Bedrock
│   ├── frente_b_deepeval/             # Suíte de testes DeepEval, juiz customizado e GEvals
│   ├── calibracao/                    # Scripts de calibração preliminar do LLM-as-a-Judge
│   └── red_team/                      # Plano de ataques adversariais (15 casos) e relatórios de contenção
└── output/
    ├── capturas/                      # Capturas JSON completas das conversas reais com o Harness
    ├── avaliacoes/                    # Relatórios JSON gerados pelo DeepEval e pelo AgentCore
    └── spans_agentcore_final.json     # 384 spans OpenTelemetry extraídos do CloudWatch (2.19 MB)
```

---

### Guia Rápido de Reprodução

#### 1. Preparação do Ambiente Virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-eval.txt
```

#### 2. Configuração de Credenciais AWS SSO
```powershell
$env:AWS_PROFILE = "upc-estagio"
$env:AWS_DEFAULT_REGION = "us-east-2"
aws sso login --profile upc-estagio
```

#### 3. Execução da Suíte Frente B (DeepEval — resultados sujeitos à revisão humana)
```powershell
$env:BEDROCK_JUDGE_MODEL = "qwen.qwen3-next-80b-a3b"
$env:ALLOW_SAME_JUDGE = "true"
.\.venv\Scripts\pytest.exe -s evals\frente_b_deepeval\test_deepeval_suite.py
```

#### 4. Extração de Telemetria e Spans (Frente A — CloudWatch)
```powershell
.\.venv\Scripts\python.exe evals\frente_a_agentcore\coletar_spans_cloudwatch.py `
  --captura output\capturas\harness_20260924T211251Z_7ddd9cd3.json `
  --log-group "/aws/bedrock-agentcore/runtimes/harness_upc_bsi_assistente_v13-N4kvaA87rO-DEFAULT" `
  --region us-east-2 --profile upc-estagio --horas 24 `
  --saida output\spans_agentcore_final.json
```

#### 5. Avaliação em Lote Nativa no Bedrock AgentCore
```powershell
.\.venv\Scripts\python.exe evals\frente_a_agentcore\batch_evaluate_spans.py
```

---

### Governança Orçamentária
O projeto operou em estrita observância ao teto financeiro fixado pelo Edital do Desafio 2, respeitando o limite orçamentário mandatório de **US$ 20,00**.

Para detalhes minuciosos de cada caso de teste e fundamentos teóricos, consulte o [**`Relatorio_Final.md`**](Relatorio_Final.md) ou a versão oficial diagramada em PDF [**`Relatorio_Final_UPC.pdf`**](Relatorio_Final_UPC.pdf).

### Agradecimentos especiais:
Essa seção eu quero agradecer a todos meus colegas sem exceção, mas especialmente as colegas: Camille, Fernanda (do meu squad) e Mary por todo conhecimento e ajuda transmitida. Foram de grande ajuda as experiências relatadas com problemas encontrados e como foi resolvido. Obrigado a todos.
