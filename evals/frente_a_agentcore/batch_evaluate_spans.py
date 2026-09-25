import json
import boto3
from pathlib import Path
from datetime import datetime, timezone
import argparse

def main():
    parser = argparse.ArgumentParser(description="Avalia spans das sessões de uma captura real do Harness")
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--spans", required=True, type=Path)
    parser.add_argument("--evaluator-id", default="upc_bsi_fundamentacao_v1-hjyasp8hmi")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true", help="Confere arquivos sem chamar a AWS")
    args = parser.parse_args()
    spans_file = args.spans.resolve()
    capture_file = args.capture.resolve()
    evaluator_id = args.evaluator_id
    output_file = args.output or Path(
        f"output/avaliacoes/agentcore_batch_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )

    print("Carregando arquivos...")
    spans_data = json.loads(spans_file.read_text(encoding="utf-8"))
    capture_data = json.loads(capture_file.read_text(encoding="utf-8"))

    if capture_data.get("tipo") != "harness_capture_real" or capture_data.get("estado") != "concluido":
        parser.error("A captura deve ser uma execução completa do Harness real")
    origin = spans_data.get("metadata", {}).get("origem_captura")
    if origin and Path(origin).resolve() != capture_file:
        parser.error("Os spans foram coletados de outra captura")
    session_spans_list = spans_data.get("sessionSpans", [])
    cases = capture_data.get("casos", [])
    if not cases or not session_spans_list:
        parser.error("A captura e os spans devem conter sessões reais")
    session_ids = [case.get("session_id") for case in cases]
    if any(not session_id for session_id in session_ids) or len(set(session_ids)) != len(session_ids):
        parser.error("Há sessões ausentes ou duplicadas na captura")

    spans_by_session = {
        session_id: [span for span in session_spans_list
                     if span.get("attributes", {}).get("session.id") == session_id
                     or span.get("attributes", {}).get("gen_ai.conversation.id") == session_id]
        for session_id in session_ids
    }
    missing = [case["id"] for case in cases if not spans_by_session[case["session_id"]]]
    if missing:
        parser.error("Sessões sem spans: " + ", ".join(missing))

    print(f"Encontrados {len(cases)} casos e {len(session_spans_list)} spans totais.")
    for case in cases:
        print(f"{case['id']}: {len(spans_by_session[case['session_id']])} spans")
    if args.validate_only:
        print("Arquivos conferidos; nenhuma chamada à AWS.")
        return
    if output_file.exists():
        raise FileExistsError(f"Recuso sobrescrever resultado: {output_file}")

    client = boto3.client("bedrock-agentcore", region_name=args.region)
    control = boto3.client("bedrock-agentcore-control", region_name=args.region)

    metadata = control.get_evaluator(evaluatorId=evaluator_id, includedData="METADATA_ONLY")
    model_config = metadata.get("evaluatorConfig", {}).get("llmAsAJudge", {}).get("modelConfig", {})
    model = model_config.get("bedrockEvaluatorModelConfig", {}).get("modelId") or model_config.get("responsesEvaluatorModelConfig", {}).get("modelId")
    
    print(f"Utilizando avaliador: {evaluator_id} (Modelo: {model})")

    results = []
    
    for i, case in enumerate(cases, 1):
        case_id = case["id"]
        session_id = case["session_id"]
        
        # Filtra os spans apenas desta sessão
        case_spans = spans_by_session[session_id]
        
        print(f"[{i}/{len(cases)}] Avaliando {case_id} ({len(case_spans)} spans)... ", end="", flush=True)
        
        try:
            response = client.evaluate(
                evaluatorId=evaluator_id,
                evaluationInput={"sessionSpans": case_spans}
            )
            eval_results = response.get("evaluationResults", [])
            print(f"SUCESSO ({len(eval_results)} notas)")
            
            results.append({
                "caso_id": case_id,
                "session_id": session_id,
                "spans": len(case_spans),
                "notas": eval_results
            })
        except Exception as e:
            print(f"ERRO: {e}")
            results.append({"caso_id": case_id, "session_id": session_id,
                            "spans": len(case_spans), "erro": str(e)})

    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    final_output = {
        "tipo": "agentcore_batch_evaluation",
        "captura": str(capture_file),
        "spans": str(spans_file),
        "avaliador_id": evaluator_id,
        "modelo_agente": capture_data.get("modelo_agente"),
        "modelo_avaliador": model,
        "avaliado_em_utc": datetime.now(timezone.utc).isoformat(),
        "resultados_por_caso": results
    }
    
    output_file.write_text(json.dumps(final_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nFinalizado! Resultados consolidados salvos em: {output_file}")
    if any("erro" in result for result in results):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
