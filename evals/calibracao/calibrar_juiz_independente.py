"""Calibra um juiz diferente do modelo do Harness antes da avaliação completa.

Requer BEDROCK_JUDGE_MODEL e BEDROCK_AGENT_MODEL no ambiente. Faz 14 chamadas
curtas ao Bedrock; rode somente após conferir o custo do modelo escolhido.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3

from calibrar_juiz_qwen import CASES, RUBRICA, extract_score


CASES = CASES + [
    {"id": "tcc_semestre_inventado", "expected": 0,
     "question": "Posso cursar TCC I depois do VII semestre?",
     "evidence": "Documento tcc.md: VII é semestre de referência, não prazo limite. Matrícula posterior é possível com 1.920 horas curriculares, oferta e vaga.",
     "answer": "Não. TCC I deve obrigatoriamente ser cursado no VII semestre."},
    {"id": "data_2027_confirmada", "expected": 1,
     "question": "Qual é o último dia para pedir trancamento em 2027.1?",
     "evidence": "Documento calendario_2027_1.md: último dia para solicitar trancamento total em 2027.1 é 27/04/2027. Pedido sujeito à análise.",
     "answer": "O último dia para solicitar trancamento total em 2027.1 é 27/04/2027. O pedido está sujeito à análise. Fonte: calendario_2027_1.md."},
]


def main():
    model_id = os.getenv("BEDROCK_JUDGE_MODEL", "").strip()
    agent_id = os.getenv("BEDROCK_AGENT_MODEL", "").strip()
    if not model_id or not agent_id or model_id.casefold() == agent_id.casefold():
        raise SystemExit("Defina BEDROCK_JUDGE_MODEL e BEDROCK_AGENT_MODEL com IDs diferentes.")
    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-2"))
    results = []
    for round_number in (1, 2):
        for case in CASES:
            prompt = (f"{RUBRICA}\nPergunta: {case['question']}\n"
                      f"Evidência: {case['evidence']}\nResposta atual: {case['answer']}")
            response = client.converse(
                modelId=model_id, messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 400, "temperature": 0},
            )
            raw = "".join(block.get("text", "") for block in response["output"]["message"]["content"])
            score = extract_score(raw)
            results.append({"caso": case["id"], "rodada": round_number,
                            "esperado": case["expected"], "observado": score,
                            "correto": score == case["expected"], "resposta_bruta": raw,
                            "uso": response.get("usage", {})})
            print(f"{case['id']} rodada {round_number}: {score} {'OK' if results[-1]['correto'] else 'REVISAR'}")
    approved = all(item["correto"] for item in results)
    payload = {"tipo": "calibracao_juiz_independente", "modelo_juiz": model_id,
               "modelo_agente_declarado": agent_id, "executado_em_utc": datetime.now(timezone.utc).isoformat(),
               "aprovada": approved, "acertos": sum(item["correto"] for item in results),
               "total": len(results), "resultados": results,
               "limite": "A calibração verifica a rubrica curta, não substitui a revisão das métricas DeepEval."}
    output = Path(__file__).resolve().parents[2] / "output" / "calibracao" / f"juiz_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Calibração {'aprovada' if approved else 'reprovada'}: {output}")
    if not approved:
        sys.exit(1)


if __name__ == "__main__":
    main()
