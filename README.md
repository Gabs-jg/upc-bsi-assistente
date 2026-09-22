# Assistente acadêmico UPC

Projeto de avaliação de um assistente acadêmico para a Universidade de Pedra Clara (UPC), uma instituição fictícia. A base de conhecimento está na versão 1.3. O agente principal está implantado no Amazon Bedrock AgentCore Harness, na região `us-east-2`.

## Estado do projeto

- Harness: `upc_bsi_assistente_v13`, com Gemma 4 E2B.
- Ferramenta de busca: `BuscaUPC___consultar_base_upc`, ligada à Knowledge Base `EZWOE4KK68`.
- Juiz de avaliação: Qwen3 Next 80B A3B (`qwen.qwen3-next-80b-a3b`).
- Avaliador personalizado AgentCore: `upc_bsi_fundamentacao_v1-hjyasp8hmi`, ativo. Ainda falta executar uma avaliação com ele.
- As três métricas do DeepEval passaram em um caso inicial. Ainda faltam a sessão exploratória, o conjunto golden e a campanha de red team.

## Pastas

| Pasta | Conteúdo |
| --- | --- |
| `kb/canonica_v1_3/` | Documentos consolidados da UPC fictícia. |
| `kb/rag_v1_3/documentos/` | Documentos curtos indexados na base de conhecimento da AWS. |
| `src/agentcore/` | Código e configurações dos protótipos de orquestração e da entrada Lambda. A busca externa à Lambda não comprova, por si só, que o Harness chamou a ferramenta. |
| `evals/` | Critérios, roteiro de exploração, configuração do juiz e testes iniciais. |

## Começar no VS Code

1. Abra esta pasta inteira no VS Code: **Arquivo → Abrir Pasta**.
2. Abra o painel **Controle do Código-Fonte** para ver o repositório Git local.
3. Abra `evals/sessao_exploratoria.md` e registre os testes no Harness. Os scripts de avaliação ficam na mesma pasta.

Para executar os scripts localmente, crie um ambiente Python e instale `requirements-eval.txt`. As chamadas à AWS exigem credenciais configuradas na sua máquina; não coloque chaves ou tokens neste repositório. Os testes iniciais foram executados no AWS CloudShell.

## Fonte de verdade

O conteúdo institucional da UPC é fictício. Para a versão implantada, use `kb/rag_v1_3/documentos/` como referência do que foi indexado; confira no rastreamento do Harness os trechos realmente recuperados antes de marcar uma resposta como correta. Os critérios de aprovação estão em `evals/criterios_predefinidos.md`.
