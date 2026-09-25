# Integração com o Amazon Bedrock AgentCore

Esta pasta contém a Lambda de busca RAG, a Lambda proxy HTTP e código experimental de orquestração. A configuração **avaliada** no relatório foi o Harness v39, com `qwen.qwen3-next-80b-a3b`, chamado diretamente pelos testes GOLD e red team. O proxy oferece outro caminho de acesso e não altera aquelas capturas.

```text
Testes diretos / Playground → AgentCore Harness
Cliente HTTP → API Gateway → Lambda proxy → AgentCore Harness
                                      Harness → Gateway / BuscaUPC
                                               ↓
                                         Lambda de busca
                                               ↓
                                    Knowledge Base → S3
```

| Arquivo | Papel |
| --- | --- |
| [`upc_busca_kb_lambda.py`](upc_busca_kb_lambda.py) | Implementa a consulta real à Knowledge Base e devolve até cinco trechos com suas URIs. |
| [`upc_harness_proxy_lambda.py`](upc_harness_proxy_lambda.py) | Encaminha solicitações HTTP ao Harness e devolve resposta, indicação de busca e fontes recuperadas. Na versão avaliada, não valida todas as citações da resposta. |
| [`PROXY_HTTP.md`](PROXY_HTTP.md) | Configuração e uso da API Gateway com autenticação por token. |
| [`prompt_harness_busca_obrigatoria.txt`](prompt_harness_busca_obrigatoria.txt) | Cópia local de instruções para o Harness; confira a versão implantada antes de associá-la a uma captura. |
| [`upc_orquestrador_v2.py`](upc_orquestrador_v2.py) e [`upc_agente_lambda.py`](upc_agente_lambda.py) | Código experimental de consulta e pós-processamento. Não foram o caminho usado nas avaliações diretas do Harness v39. |

A existência da ferramenta no Harness não obriga o modelo a acioná-la. Na v39, GOLD-011 respondeu sem busca e citou um PDF não recuperado. Veja os [resultados e o parecer de risco](../../Relatorio_Final.md) antes de tratar o agente como apto para orientação acadêmica.
