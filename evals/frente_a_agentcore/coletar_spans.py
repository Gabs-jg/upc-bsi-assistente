"""Coleta spans reais de uma sessão do Harness no CloudWatch Logs.

Use somente depois de habilitar Transaction Search e invocar novamente o
Harness. O arquivo resultante pode ser passado a avaliar_spans.py.
"""

import argparse
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_LOG_GROUP = (
    "/aws/bedrock-agentcore/runtimes/"
    "harness_upc_bsi_assistente_v13-N4kvaA87rO-DEFAULT"
)


def select_case(capture, case_id):
    if capture.get("tipo") != "harness_capture_real":
        raise ValueError("A captura deve vir do Harness real")
    cases = capture.get("casos", [])
    if case_id:
        matches = [case for case in cases if case.get("id") == case_id]
        if len(matches) != 1:
            raise ValueError(f"Caso não encontrado uma única vez: {case_id}")
        return matches[0]
    if len(cases) != 1:
        raise ValueError("Informe --case para uma captura com vários casos")
    return cases[0]


def query_group(client, log_group, session_id, start_epoch, end_epoch, timeout_seconds):
    query = (
        "fields @timestamp, @message "
        "| filter ispresent(scope.name) and ispresent(attributes.session.id) "
        f'| filter attributes.session.id = "{session_id}" '
        "| sort @timestamp asc"
    )
    try:
        query_id = client.start_query(
            logGroupName=log_group,
            startTime=start_epoch,
            endTime=end_epoch,
            queryString=query,
            limit=1000,
        )["queryId"]
    except client.exceptions.ResourceNotFoundException:
        return []

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = client.get_query_results(queryId=query_id)
        status = result["status"]
        if status == "Complete":
            return result.get("results", [])
        if status in ("Failed", "Cancelled", "Timeout", "Unknown"):
            raise RuntimeError(f"Consulta CloudWatch em {log_group}: {status}")
        time.sleep(2)
    client.stop_query(queryId=query_id)
    raise TimeoutError(f"Consulta CloudWatch em {log_group} excedeu {timeout_seconds} s")


def extract_spans(rows):
    spans = []
    for row in rows:
        messages = [field["value"] for field in row if field.get("field") == "@message"]
        for message in messages:
            try:
                record = json.loads(message)
                if isinstance(record, str):
                    record = json.loads(record)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                spans.append(record)
    return spans


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--case")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--runtime-log-group", default=RUNTIME_LOG_GROUP)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    args = parser.parse_args()

    capture = json.loads(args.capture.read_text(encoding="utf-8"))
    case = select_case(capture, args.case)
    session_id = case.get("session_id")
    if not session_id:
        parser.error("O caso não contém session_id")
    # Uma sessão do golden pode ter vários turnos, mas Evaluate aceita uma sessão
    # por chamada. A consulta cobre todos os turnos dessa sessão.
    captured_at = datetime.fromisoformat(capture["capturado_em_utc"].replace("Z", "+00:00"))
    start_epoch = int((captured_at - timedelta(minutes=5)).timestamp())
    end_epoch = int((datetime.now(timezone.utc) + timedelta(minutes=1)).timestamp())
    if end_epoch <= start_epoch:
        parser.error("A captura está no futuro em relação ao relógio local")

    import boto3

    client = boto3.client("logs", region_name=args.region)
    groups = [args.runtime_log_group, "aws/spans"]
    all_spans = []
    used_groups = []
    seen = set()
    for group in groups:
        rows = query_group(client, group, session_id, start_epoch, end_epoch, args.timeout_seconds)
        spans = extract_spans(rows)
        print(f"{group}: {len(spans)} span(s) da sessão")
        if spans:
            used_groups.append(group)
        for span in spans:
            key = json.dumps(span, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                all_spans.append(span)
    if not all_spans:
        raise RuntimeError(
            "Nenhum span encontrado. Confirme Transaction Search ACTIVE, "
            "aguarde 2–5 minutos após a invocação e use uma captura feita após a ativação."
        )

    output = args.output or ROOT / "output" / "spans" / (
        f"spans_{case['id'].lower()}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )
    if output.exists():
        raise FileExistsError(f"Recuso sobrescrever spans: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "tipo": "agentcore_session_spans_reais",
        "caso": case["id"],
        "session_id": session_id,
        "capture_sha256": hashlib.sha256(args.capture.read_bytes()).hexdigest(),
        "regiao": args.region,
        "log_groups": used_groups,
        "coletado_em_utc": datetime.now(timezone.utc).isoformat(),
        "sessionSpans": all_spans,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(all_spans)} span(s) salvo(s) em {output}")


if __name__ == "__main__":
    main()
