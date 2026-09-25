"""Código da Lambda `upc-bsi-busca-kb-v13` usada pelo Gateway.

Variáveis opcionais: UPC_KNOWLEDGE_BASE_ID e UPC_RETRIEVAL_RESULTS.
O código local precisa ser implantado separadamente para atualizar a AWS.
"""

import os

import boto3


BASE_ID = os.getenv("UPC_KNOWLEDGE_BASE_ID", "EZWOE4KK68")
RESULTS = int(os.getenv("UPC_RETRIEVAL_RESULTS", "5"))
bedrock = boto3.client("bedrock-agent-runtime", region_name="us-east-2")


def lambda_handler(event, context):
    if not isinstance(event, dict):
        return {"erro": "Envie um objeto com o campo pergunta."}
    pergunta = event.get("pergunta")
    if not isinstance(pergunta, str) or not pergunta.strip():
        return {"erro": "Informe uma pergunta para consultar a base."}
    response = bedrock.retrieve(
        knowledgeBaseId=BASE_ID,
        retrievalQuery={"text": pergunta.strip()},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": RESULTS}},
    )
    return {"resultados": [
        {"texto": item.get("content", {}).get("text", ""),
         "fonte": item.get("location", {}).get("s3Location", {}).get("uri", "")}
        for item in response.get("retrievalResults", [])
    ]}
