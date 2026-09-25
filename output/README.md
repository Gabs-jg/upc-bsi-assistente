# Repositório de Evidências e Artefatos — Pasta `output/`

Este diretório armazena todos os artefatos gerados durante o ciclo de desenvolvimento, captura de conversas em tempo real, extração de telemetria da nuvem e homologação de métricas para o **Desafio 2 (UPC BSI)**.

---

### Estrutura Organizacional

```
output/
├── capturas/                      # Sessões conversacionais brutas com o Harness
├── avaliacoes/                    # Relatórios estruturados de métricas (DeepEval e AgentCore)
├── calibracao/                    # Ensaios preliminares e holdouts de calibração do juiz
├── deploy/                        # Pacotes compactados (.zip) para funções AWS Lambda
└── spans_agentcore_final.json     # 384 spans OpenTelemetry extraídos do CloudWatch (2.19 MB)
```

---

### Principais Arquivos e Evidências Oficiais do Edital

Para fins de auditoria da banca avaliadora, os seguintes arquivos constituem as **evidências oficiais homologadas**:

| Arquivo / Caminho | Descrição e Relevância Técnica |
|---|---|
| **`output/spans_agentcore_final.json`** | **Evidência Central da Frente A:** Arquivo JSON com 384 spans em formato OpenTelemetry minerados do CloudWatch Logs Insights (`/aws/bedrock-agentcore/runtimes/...`), cobrindo as 15 sessões do Golden Dataset com identificadores únicos `traceId` e `spanId`. Comprova a execução real do agente e a consulta legítima à Knowledge Base. |
| **`output/avaliacoes/agentcore_batch_20260924T225356Z.json`** | **Avaliação em Lote Bedrock:** Relatório oficial emitido pela API `Evaluate` do Bedrock AgentCore utilizando o avaliador customizado `upc_bsi_fundamentacao_v1-hjyasp8hmi`. Registra as notas de fundamentação retornadas pela AWS para os 15 casos. |
| **`output/capturas/harness_20260924T211251Z_7ddd9cd3.json`** | **Captura Homologatória Oficial:** Registro íntegro dos 15 casos do Golden Dataset executados contra a versão 22 do Harness, contendo as perguntas dos estudantes, as respostas emitidas pelo agente e a lista literal dos trechos recuperados da base vetorial. |
| **`output/avaliacoes/deepeval_suite_*.json`** | **Resultados da Frente B:** Relatórios detalhados gerados pela suíte PyTest/DeepEval, contendo as pontuações e justificativas semânticas de *Answer Relevancy*, *Faithfulness* e *Conformidade UPC* que atestam os **15/15 testes aprovados**. |

---

### Políticas de Preservação e Rastreabilidade

1. **Imutabilidade de Evidências:** Os scripts de execução recusam terminantemente a sobrescrita de capturas ou avaliações existentes, gerando sempre identificadores com timestamp UTC (`%Y%m%dT%H%M%SZ`) e hash criptográfico.
2. **Histórico de Baterias:** Os arquivos com sufixo `baseline` ou timestamps anteriores registram as etapas de evolução do projeto (Baterias 1, 2 e 3) e foram mantidos para demonstrar a trajetória metrológica de resolução dos falsos negativos, conforme documentado na Seção 5 do [**`Relatorio_Final.md`**](../Relatorio_Final.md).
