# Frente A — Avaliação Nativa em Nuvem via AWS Bedrock AgentCore

Este diretório contém os scripts de automação, pipelines de extração de telemetria e utilitários de avaliação em lote para a **Frente A** do Desafio 2, operando nativamente no ecossistema Amazon Bedrock AgentCore na região `us-east-2` (Ohio).

---

### Visão Geral da Arquitetura Frente A

A Frente A é responsável por auditar o comportamento do agente diretamente na infraestrutura em nuvem, garantindo rastreabilidade ponta a ponta sem recorrer a simulações sintéticas desconectadas do runtime.

```
                          PIPELINE DE EXECUÇÃO FRENTE A

  1. Execução no Harness ──────> 2. Mineração CloudWatch ──────> 3. Batch Evaluation Bedrock
     (agentcore_eval_runner.py)     (coletar_spans_cloudwatch.py)   (batch_evaluate_spans.py)
              │                               │                               │
              ▼                               ▼                               ▼
     output/capturas/                output/                         output/avaliacoes/
     harness_*.json                  spans_agentcore_*.json          agentcore_batch_*.json
     (Perguntas/Respostas reais)     (384 Spans OpenTelemetry)       (Notas oficiais da AWS)
```

---

### Componentes e Scripts Disponíveis

| Script / Arquivo | Responsabilidade Técnica |
|---|---|
| **`agentcore_eval_runner.py`** | Dispara as perguntas do *Golden Dataset* diretamente contra o Harness via API Bedrock Runtime, criando uma sessão isolada por caso (`session_id`) e registrando se o agente chamou a ferramenta `BuscaUPC___consultar_base_upc`, além das respostas e trechos RAG em `output/capturas/`. A disponibilidade da ferramenta não obriga o modelo a chamá-la. |
| **`coletar_spans_cloudwatch.py`** | Executa queries automatizadas no CloudWatch Logs Insights (`/aws/bedrock-agentcore/runtimes/...`) para minerar os *traces* e *spans* OpenTelemetry correspondentes aos `session_id` da captura, gerando a "caixa preta" definitiva da execução. |
| **`batch_evaluate_spans.py`** | Utilitário consolidado de avaliação em lote. Lê o arquivo de spans, agrupa por caso e despacha as sessões para a API `Evaluate` do Bedrock usando o avaliador customizado `upc_bsi_fundamentacao_v1-hjyasp8hmi`. |
| **`avaliar_spans.py`** | Script de avaliação pontual (caso a caso) sob demanda com suporte a `--validate-only`. |
| **`juiz_agentcore_fundamentacao.json`** | Especificação JSON da configuração do avaliador customizado de Fundamentação UPC no Bedrock. |

---

### Guia de Execução Passo a Passo

#### Passo 1: Captura de Sessão Direta no Harness
Gera as respostas reais do agente na AWS a partir dos 15 casos do *Golden Dataset*:
```powershell
$env:AWS_PROFILE = "upc-estagio"
$env:AWS_DEFAULT_REGION = "us-east-2"

# Modo simulação (sem chamar AWS):
.\.venv\Scripts\python.exe evals\frente_a_agentcore\agentcore_eval_runner.py --dry-run

# Execução completa dos 15 casos:
.\.venv\Scripts\python.exe evals\frente_a_agentcore\agentcore_eval_runner.py --all
```
*O arquivo resultante será salvo em `output/capturas/harness_<TIMESTAMP>_<HASH>.json`.*

#### Passo 2: Extração de Spans do CloudWatch Logs Insights
Conecta-se ao grupo de logs do runtime e minera os eventos estruturados de telemetria das 15 sessões:
```powershell
.\.venv\Scripts\python.exe evals\frente_a_agentcore\coletar_spans_cloudwatch.py `
  --captura output\capturas\harness_20260925T044149Z_c989107c.json `
  --log-group "/aws/bedrock-agentcore/runtimes/harness_upc_bsi_assistente_v13-N4kvaA87rO-DEFAULT" `
  --region us-east-2 --profile upc-estagio --horas 24 `
  --saida output\spans_agentcore_20260925T044149Z.json
```
*Resultado registrado na captura v39:* **384 spans OpenTelemetry exportados** com `traceId` e `spanId` válidos (arquivo de 2,19 MB). Isso comprova a execução das sessões, não a aprovação de todas as respostas.

#### Passo 3: Avaliação em Lote com o Avaliador Customizado
Confere se os spans pertencem à captura atual antes de chamar a AWS:
```powershell
.\.venv\Scripts\python.exe evals\frente_a_agentcore\batch_evaluate_spans.py --capture output\capturas\harness_20260925T044149Z_c989107c.json --spans output\spans_agentcore_20260925T044149Z.json --validate-only
```
Em seguida, executa a avaliação com o avaliador customizado `upc_bsi_fundamentacao_v1-hjyasp8hmi`:
```powershell
.\.venv\Scripts\python.exe evals\frente_a_agentcore\batch_evaluate_spans.py --capture output\capturas\harness_20260925T044149Z_c989107c.json --spans output\spans_agentcore_20260925T044149Z.json
```
O consolidado fica gravado em `output/avaliacoes/agentcore_batch_*.json`. A captura atual tem uma falha objetiva no GOLD-011: ausência da chamada de busca e fonte inventada. Registre-a na revisão humana mesmo se o avaliador atribuir nota alta.

---

### Avaliador Customizado Registrado
* **Nome / ID:** `upc_bsi_fundamentacao_v1-hjyasp8hmi`
* **ARN:** `arn:aws:bedrock-agentcore:us-east-2:276996007591:evaluator/upc_bsi_fundamentacao_v1-hjyasp8hmi`
* **Status:** `ACTIVE`
* **Modelo Juiz:** `qwen.qwen3-next-80b-a3b`
* **Escala:** 0.0 (Sem fundamentação) / 0.5 (Parcialmente fundamentado) / 1.0 (Totalmente fundamentado nos documentos RAG).
