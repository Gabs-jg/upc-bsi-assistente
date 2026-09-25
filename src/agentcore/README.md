# Arquitetura de Integração — Amazon Bedrock AgentCore

Este diretório contém os códigos-fonte das funções **AWS Lambda**, especificações de permissões IAM, definições de prompts de sistema e configurações do proxy HTTP que integram o agente conversacional ao ecossistema **Amazon Bedrock AgentCore** na região `us-east-2` (Ohio).

---

### Componentes Arquiteturais

```
                     FLUXO DE EXECUÇÃO INTERNA DO AGENTCORE

  [ Requisitante / Aluno ]
              │
              ▼ HTTPS (POST /perguntar)
  ┌────────────────────────────────────────────────────────┐
  │ API Gateway Proxy (`upc-bsi-api-v1`)                   │
  │ Lambda Proxy: `upc-bsi-harness-proxy-v1`               │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │ Amazon Bedrock AgentCore Harness                       │
  │ ID: `upc_bsi_assistente_v13-xWH7Nkzzk1` (Versão 22)    │
  │ Modelo: `qwen.qwen3-next-80b-a3b`                      │
  │ System Prompt: `prompt_harness_busca_obrigatoria.txt`  │
  └─────────────┬────────────────────────────┬─────────────┘
                │                            │
      Invocação de Ação                      Geração Textual
      (Tool Calling)                         com Contexto
                │                            │
                ▼                            ▼
  ┌──────────────────────────┐  ┌──────────────────────────┐
  │ Lambda de Busca RAG:     │  │ Lambda do Agente:        │
  │ `upc-bsi-busca-kb-v13`   │  │ `upc_agente_lambda.py`   │
  │ Código:                  │  │ - Pós-processamento      │
  │ `upc_busca_kb_lambda.py` │  │ - Expansão de fontes     │
  └─────────────┬────────────┘  │ - Injeção freq. 75%      │
                │               └────────────┬─────────────┘
                ▼                            │
  ┌──────────────────────────┐               ▼
  │ Bedrock Knowledge Base:  │      Resposta Formatada
  │ `EZWOE4KK68`             │      com Citação Canônica
  └──────────────────────────┘
```

---

### Descrição dos Arquivos e Funções

| Arquivo | Função e Responsabilidade Técnica |
|---|---|
| **`upc_busca_kb_lambda.py`** | Função Lambda que atua como *Action Group* do AgentCore. Recebe a query semântica formulada pelo modelo, invoca a API `Retrieve` da Knowledge Base `EZWOE4KK68` e retorna os 5 trechos mais relevantes do bucket S3. |
| **`upc_agente_lambda.py`** | Camada de pós-processamento e enriquecimento de resposta. Implementa duas regras de negócio críticas: <br>1. *Expansão de Citações:* Substitui índices numéricos genéricos (`[1]`, `[2]`) pelo nome real dos arquivos (ex: `08_ementas.md`, `curso_ingresso.md`). <br>2. *Injeção de Guardrail de Frequência:* Assegura que qualquer cálculo ou menção à prova final inclua explicitamente a exigência mandatória de **75% de frequência mínima**. |
| **`prompt_harness_busca_obrigatoria.txt`** | Prompt de sistema mestre injetado no Harness. Instruções estritas de: <br>- Busca obrigatória na base para qualquer fato novo da UPC. <br>- Proibição de inventar datas ou projetar prazos de 2027 para 2028. <br>- Recusa de ações administrativas (matrículas e trancamentos). <br>- Recusa polida de perguntas fora do escopo acadêmico da UPC. |
| **`politica_upc_agente_lambda.json`** | Política de permissões mínimas IAM (Least Privilege) concedendo permissão para invocação de modelos no Bedrock e leitura de logs no CloudWatch. |
| **`PROXY_HTTP.md`** | Documentação técnica da API Gateway HTTP para acesso externo autenticado via token privado de cabeçalho (`x-upc-proxy-token`). |

---

### Procedimento de Atualização e Deploy

Para empacotar e atualizar a Lambda de busca no console AWS:
```powershell
Compress-Archive -Path src\agentcore\upc_busca_kb_lambda.py `
  -DestinationPath output\deploy\upc-bsi-busca-kb-v13.zip `
  -Force
```

Em seguida, faça o upload do `.zip` gerado para a função Lambda `upc-bsi-busca-kb-v13` na região `us-east-2`.
