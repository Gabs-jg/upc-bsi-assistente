"""Roda avaliações AgentCore sob demanda em spans reais já exportados.

Não habilita avaliação contínua. Requer arquivo JSON com `sessionSpans` em
formato OpenTelemetry, obtido do CloudWatch/Transaction Search.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spans", required=True, type=Path)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--case", help="ID do caso; obrigatório se a captura contém várias sessões")
    parser.add_argument("--evaluator-id", required=True, action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    spans = json.loads(args.spans.read_text(encoding="utf-8"))
    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    if capture.get("tipo") != "harness_capture_real":
        parser.error("A captura deve vir do Harness real")
    cases = capture.get("casos", [])
    if args.case:
        cases = [case for case in cases if case.get("id") == args.case]
    if len(cases) != 1:
        parser.error("Selecione exatamente uma sessão da captura com --case")
    case = cases[0]
    session_id = case.get("session_id")
    if not session_id:
        parser.error("O caso selecionado não contém session_id")
    records = spans.get("sessionSpans") if isinstance(spans, dict) else spans
    if not isinstance(records, list) or not records:
        parser.error("O arquivo de spans precisa conter sessionSpans não vazio")
    if isinstance(spans, dict) and spans.get("session_id") not in (None, session_id):
        parser.error("O arquivo de spans pertence a outra sessão")
    serialized_spans = json.dumps(records, ensure_ascii=False)
    if session_id not in serialized_spans:
        parser.error(f"Os spans não incluem a sessão do caso {case['id']}")
    if args.validate_only:
        print(f"{case['id']}: {len(records)} spans e {len(args.evaluator_id)} avaliadores; nenhuma chamada à AWS.")
        return

    import boto3

    control = boto3.client("bedrock-agentcore-control", region_name="us-east-2")
    client = boto3.client("bedrock-agentcore", region_name="us-east-2")
    results = []
    for evaluator_id in args.evaluator_id:
        metadata = control.get_evaluator(evaluatorId=evaluator_id, includedData="METADATA_ONLY")
        model_config = (metadata.get("evaluatorConfig", {}).get("llmAsAJudge", {})
                        .get("modelConfig", {}))
        model = (model_config.get("bedrockEvaluatorModelConfig", {}).get("modelId")
                 or model_config.get("responsesEvaluatorModelConfig", {}).get("modelId"))
        if metadata.get("evaluatorType") == "Custom" and not model:
            raise ValueError(f"Não foi possível confirmar o modelo do avaliador {evaluator_id}")
        if model and model.casefold() == capture["modelo_agente"].casefold():
            print(f"Aviso: Avaliador {evaluator_id} usa o mesmo modelo do agente ({model})")
        if metadata.get("status") != "ACTIVE":
            raise ValueError(f"Avaliador {evaluator_id} não está ativo")
        response = client.evaluate(evaluatorId=evaluator_id,
                                   evaluationInput={"sessionSpans": records})
        results.append({"evaluator_id": evaluator_id, "modelo_juiz": model,
                        "resultados": response.get("evaluationResults", [])})
        print(f"{evaluator_id}: {len(results[-1]['resultados'])} resultado(s)")
    output = args.output or ROOT / "output" / "avaliacoes" / f"agentcore_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"tipo": "agentcore_ondemand_spans_reais",
                                  "captura": str(args.capture), "caso": case["id"],
                                  "session_id": session_id, "spans": str(args.spans),
                                  "modelo_agente": capture["modelo_agente"],
                                  "avaliado_em_utc": datetime.now(timezone.utc).isoformat(),
                                  "avaliadores": results, "revisao_humana": "pendente"},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resultados salvos em {output}")


if __name__ == "__main__":
    main()
