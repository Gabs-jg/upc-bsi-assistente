"""Verifica a consulta obrigatória e a resposta de prova final na Lambda do agente.

Execute em um ambiente com credenciais AWS para a região us-east-2:
    python evals/smoke_assistente_prova_final.py
"""

import json
import re

import boto3


FUNCAO = "upc-bsi-assistente-v13"
PERGUNTA = "Minha média parcial é 4,5. Quanto preciso tirar na prova final?"


def main():
    cliente = boto3.client("lambda", region_name="us-east-2")
    resultado = cliente.invoke(
        FunctionName=FUNCAO,
        InvocationType="RequestResponse",
        Payload=json.dumps({"pergunta": PERGUNTA}, ensure_ascii=False).encode("utf-8"),
    )
    corpo = resultado["Payload"].read().decode("utf-8")
    if resultado.get("FunctionError"):
        raise RuntimeError(f"A Lambda falhou: {corpo}")

    dados = json.loads(corpo)
    print(json.dumps(dados, ensure_ascii=False, indent=2))
    if "erro" in dados:
        raise RuntimeError(dados["erro"])

    fontes = dados.get("fontes_recuperadas", [])
    resposta = dados.get("resposta", "")
    verificacoes = {
        "busca executada": dados.get("ferramenta_executada") == "upc-bsi-busca-kb-v13",
        "regra recuperada": any(
            fonte.endswith("/avaliacao/prova_final.md")
            or fonte.endswith("/regras/avaliacao_frequencia.md")
            for fonte in fontes
        ),
        "nota 6,0 informada": bool(re.search(r"\b6(?:[,.]0)?\b", resposta)),
        "fonte citada por caminho": any(fonte in resposta for fonte in fontes if fonte),
        "frequência condicionada": "frequ" in resposta.lower() and "75%" in resposta,
        "sem pedido de disciplina": not bool(
            re.search(r"(?:informe|diga|preciso saber).{0,60}disciplina", resposta, re.I)
        ),
    }
    for nome, passou in verificacoes.items():
        print(f"{'OK' if passou else 'FALHOU'}: {nome}")
    if not all(verificacoes.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
