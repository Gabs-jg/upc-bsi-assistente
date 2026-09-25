"""Calibra o Qwen3 como juiz de si mesmo — uso quando não há outro modelo disponível.

⚠ LIMITAÇÃO CONHECIDA: usar o mesmo modelo como agente e juiz cria viés de
auto-avaliação. O modelo pode favorecer respostas no mesmo estilo que ele mesmo
produziria. Os resultados desta calibração devem ser descritos no relatório como
'juiz homogêneo (Qwen3)' e não como avaliação independente.

Este script grava um JSON com tipo='calibracao_juiz_qwen_self' e
aprovada=True somente se o modelo acertar todos os casos de calibração.
O run_deepeval_evaluations.py aceita este arquivo com --allow-same-judge.

Uso:
  python evals/calibracao/calibrar_juiz_qwen_self.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import boto3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=False)

from calibrar_juiz_qwen import CASES, RUBRICA, extract_score  # noqa: E402

# Dois casos adicionais críticos
EXTRA_CASES = [
    {
        "id": "tcc_semestre_inventado",
        "expected": 0,
        "question": "Posso cursar TCC I depois do VII semestre?",
        "evidence": (
            "Documento tcc.md: VII é semestre de referência, não prazo limite. "
            "Matrícula posterior é possível com 1.920 horas curriculares, oferta e vaga."
        ),
        "answer": "Não. TCC I deve obrigatoriamente ser cursado no VII semestre.",
    },
    {
        "id": "data_2027_confirmada",
        "expected": 1,
        "question": "Qual é o último dia para pedir trancamento em 2027.1?",
        "evidence": (
            "Documento calendario_2027_1.md: último dia para solicitar trancamento "
            "total em 2027.1 é 27/04/2027. Pedido sujeito à análise."
        ),
        "answer": (
            "O último dia para solicitar trancamento total em 2027.1 é 27/04/2027. "
            "O pedido está sujeito à análise. Fonte: calendario_2027_1.md."
        ),
    },
]

ALL_CASES = CASES + EXTRA_CASES

MODEL_ID = os.getenv("BEDROCK_JUDGE_MODEL", "qwen.qwen3-next-80b-a3b").strip()
REGION = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-2"))


def main():
    print(f"Calibrando juiz: {MODEL_ID} (região {REGION})")
    print("AVISO: Juiz igual ao agente - limitacao de vies declarada no relatorio.\n")

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    kwargs = {}
    if aws_access_key and aws_secret_key:
        kwargs = dict(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
        )
    client = boto3.client("bedrock-runtime", region_name=REGION, **kwargs)

    results = []
    input_tokens = output_tokens = 0

    for round_number in (1, 2):
        for case in ALL_CASES:
            prompt = (
                f"{RUBRICA}\nPergunta: {case['question']}\n"
                f"Evidência: {case['evidence']}\nResposta atual: {case['answer']}"
            )
            response = client.converse(
                modelId=MODEL_ID,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 400, "temperature": 0},
            )
            raw = "".join(
                block.get("text", "")
                for block in response["output"]["message"]["content"]
            ).strip()
            score = extract_score(raw)
            usage = response.get("usage", {})
            input_tokens += usage.get("inputTokens", 0)
            output_tokens += usage.get("outputTokens", 0)
            correct = score == case["expected"]
            results.append({
                "caso": case["id"],
                "rodada": round_number,
                "esperado": case["expected"],
                "observado": score,
                "correto": correct,
                "resposta_bruta": raw,
                "uso": usage,
            })
            print(
                f"{case['id']} rodada {round_number}: "
                f"esperado={case['expected']} observado={score} "
                f"{'OK' if correct else 'REVISAR'}"
            )
            if not correct:
                print(f"  Resposta bruta: {raw}")

    approved = all(item["correto"] for item in results)
    acertos = sum(item["correto"] for item in results)
    estimate = input_tokens * 0.15 / 1_000_000 + output_tokens * 1.20 / 1_000_000

    payload = {
        "tipo": "calibracao_juiz_qwen_self",
        "aviso_viés": (
            "Juiz homogêneo: mesmo modelo Qwen3 usado como agente e juiz. "
            "Auto-avaliação pode favorecer respostas no estilo do modelo. "
            "Declare esta limitação no relatório final."
        ),
        "modelo_juiz": MODEL_ID,
        "modelo_agente_declarado": MODEL_ID,
        "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "aprovada": approved,
        "acertos": acertos,
        "total": len(results),
        "tokens_entrada": input_tokens,
        "tokens_saida": output_tokens,
        "custo_estimado_usd": round(estimate, 6),
        "resultados": results,
    }
    output = ROOT / "output" / "calibracao" / f"juiz_qwen_self_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\nAcertos: {acertos}/{len(results)}")
    print(f"Custo estimado (Qwen3): US$ {estimate:.4f}")
    print(f"Calibração {'aprovada' if approved else 'reprovada'}: {output}")
    if not approved:
        sys.exit(1)


if __name__ == "__main__":
    main()
