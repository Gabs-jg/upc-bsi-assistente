"""Captura uma rodada real do Harness, inclusive buscas, sem chamar um juiz.

Exemplos:
  python evals/frente_a_agentcore/agentcore_eval_runner.py --dry-run
  python evals/frente_a_agentcore/agentcore_eval_runner.py --case GOLD-001
  python evals/frente_a_agentcore/agentcore_eval_runner.py --all

Cada caso recebe uma sessão própria. Os turnos do mesmo caso compartilham sessão.
"""

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "evals" / "datasets" / "golden_dataset.json"
HARNESS_ARN = (
    "arn:aws:bedrock-agentcore:us-east-2:276996007591:"
    "harness/upc_bsi_assistente_v13-xWH7Nkzzk1"
)
TOOL_NAME = "consultar_base_upc"


def decode_payload(value):
    """Desembrulha o JSON retornado pelo Gateway quando possível."""
    for _ in range(3):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return value
        elif isinstance(value, dict) and "content" in value and isinstance(value["content"], list):
            value = [decode_payload(x.get("text", x.get("json", x))) for x in value["content"]]
        else:
            break
    return value


def find_results(value):
    value = decode_payload(value)
    if isinstance(value, dict):
        if isinstance(value.get("resultados"), list):
            return value["resultados"]
        for child in value.values():
            found = find_results(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_results(child)
            if found:
                return found
        # O EventStream pode repartir um único JSON da ferramenta entre vários
        # deltas de texto. Nenhum fragmento isolado é JSON válido nesse caso.
        text_parts = [child if isinstance(child, str) else child.get("text")
                      for child in value
                      if isinstance(child, str) or
                      (isinstance(child, dict) and isinstance(child.get("text"), str))]
        if text_parts:
            return find_results("".join(text_parts))
    return []


def parse_stream(stream):
    """Extrai a última resposta e as chamadas/resultados do EventStream oficial."""
    role = None
    blocks = {}
    answers = []
    tool_calls = []
    tool_results = []
    usage = []
    for event in stream:
        if "messageStart" in event:
            role = event["messageStart"].get("role")
            blocks = {}
        elif "contentBlockStart" in event:
            payload = event["contentBlockStart"]
            idx = payload["contentBlockIndex"]
            start = payload.get("start", {})
            blocks[idx] = {"kind": next(iter(start), "text"), "start": start, "parts": []}
        elif "contentBlockDelta" in event:
            payload = event["contentBlockDelta"]
            idx = payload["contentBlockIndex"]
            block = blocks.setdefault(idx, {"kind": "text", "start": {}, "parts": []})
            delta = payload.get("delta", {})
            if block["kind"] == "toolUse" and "toolUse" in delta:
                block["parts"].append(delta["toolUse"].get("input", ""))
            elif block["kind"] == "toolResult" and "toolResult" in delta:
                block["parts"].extend(delta["toolResult"])
            elif block["kind"] == "text" and "text" in delta:
                block["parts"].append(delta["text"])
        elif "contentBlockStop" in event:
            idx = event["contentBlockStop"]["contentBlockIndex"]
            block = blocks.get(idx, {})
            kind = block.get("kind")
            if kind == "toolUse":
                start = block.get("start", {}).get("toolUse", {})
                raw = "".join(block.get("parts", []))
                tool_calls.append({"nome": start.get("name"), "id": start.get("toolUseId"),
                                   "entrada": decode_payload(raw)})
            elif kind == "toolResult":
                start = block.get("start", {}).get("toolResult", {})
                parts = [decode_payload(x.get("text", x.get("json", x))) for x in block.get("parts", [])]
                tool_results.append({"id": start.get("toolUseId"), "status": start.get("status"),
                                     "conteudo": parts, "resultados": find_results(block.get("parts", []))})
        elif "messageStop" in event:
            if role == "assistant":
                message = "\n".join("".join(b["parts"]) for b in blocks.values() if b["kind"] == "text").strip()
                if message:
                    answers.append(message)
            role = None
            blocks = {}
        elif "metadata" in event:
            usage.append(event["metadata"].get("usage", {}))
        elif "runtimeClientError" in event or "validationException" in event or "internalServerException" in event:
            raise RuntimeError(str(event))
    return {"resposta": answers[-1] if answers else "", "chamadas": tool_calls,
            "resultados_ferramenta": tool_results, "uso_tokens": usage}


def check_turn(turn, trace, prior_results):
    calls = [x for x in trace["chamadas"] if TOOL_NAME in str(x.get("nome", ""))]
    matched = [result for result in trace["resultados_ferramenta"]
               if result.get("status") != "error"
               and result.get("id") in {call.get("id") for call in calls}]
    results = [item for result in matched for item in result["resultados"]]
    all_results = prior_results + results
    return {
        "busca_obrigatoria_atendida": not turn["busca_esperada"] or bool(matched),
        "chamada_observada": bool(calls),
        "resultado_observado": bool(matched),
        "evidencia_acumulada": all_results,
    }


def select_cases(data, args):
    cases = data["casos"]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            raise ValueError(f"Caso não encontrado: {args.case}")
    if args.limit is not None:
        cases = cases[:args.limit]
    return cases


def validate_dataset(data):
    cases = data.get("casos")
    if not isinstance(cases, list) or not cases:
        raise ValueError("O dataset precisa conter uma lista não vazia de casos")
    ids = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("Caso sem ID válido")
        ids.append(case["id"])
        turns = case.get("turnos")
        if not isinstance(turns, list) or not turns:
            raise ValueError(f"Caso sem turnos: {case['id']}")
        for turn in turns:
            if not isinstance(turn, dict) or not isinstance(turn.get("pergunta"), str) or not turn["pergunta"].strip():
                raise ValueError(f"Pergunta vazia em {case['id']}")
            if not isinstance(turn.get("busca_esperada"), bool):
                raise ValueError(f"busca_esperada precisa ser booleana em {case['id']}")
    if len(ids) != len(set(ids)):
        raise ValueError("IDs de caso duplicados no dataset")


def repair_capture(capture):
    """Reconstitui trechos já presentes no JSON, sem nova chamada ao Harness."""
    if capture.get("tipo") != "harness_capture_real" or not isinstance(capture.get("casos"), list):
        raise ValueError("Arquivo não é uma captura real do Harness")
    for case in capture["casos"]:
        cumulative = []
        for turn in case["turnos"]:
            for result in turn.get("resultados_ferramenta", []):
                recovered = find_results(result.get("conteudo", []))
                if recovered:
                    result["resultados"] = recovered
            checked = check_turn(turn, turn, cumulative)
            cumulative = checked.pop("evidencia_acumulada")
            turn.update(checked)
        case["trechos_recuperados"] = cumulative
        case["busca_obrigatoria_atendida"] = all(
            turn["busca_obrigatoria_atendida"] for turn in case["turnos"]
        )
    return capture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case")
    group.add_argument("--limit", type=int)
    group.add_argument("--all", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--repair-capture", type=Path)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--system-prompt-file", type=Path,
                        help="Testa um prompt local apenas nesta execução, sem editar o Harness salvo")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit deve ser positivo")

    if args.repair_capture:
        output = args.output or args.repair_capture.with_name(
            args.repair_capture.stem + "_reparada.json"
        )
        if output.exists():
            raise FileExistsError(f"Recuso sobrescrever captura: {output}")
        capture = json.loads(args.repair_capture.read_text(encoding="utf-8"))
        repair_capture(capture)
        capture["reparada_de"] = str(args.repair_capture)
        capture["reparada_em_utc"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(capture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Captura reparada salva em {output}")
        for case in capture["casos"]:
            print(f"{case['id']}: {len(case['trechos_recuperados'])} trecho(s) recuperado(s)")
        return

    dataset_bytes = args.dataset.read_bytes()
    data = json.loads(dataset_bytes)
    validate_dataset(data)
    cases = select_cases(data, args)
    prompt_override = None
    if args.system_prompt_file:
        prompt_override = args.system_prompt_file.read_text(encoding="utf-8").strip()
        if not prompt_override:
            parser.error("O arquivo de prompt está vazio")
    if args.dry_run:
        suffix = "; prompt local válido" if prompt_override else ""
        print(f"Dataset válido: {len(cases)} casos{suffix}; nenhuma chamada à AWS.")
        return

    output = args.output or ROOT / "output" / "capturas" / (
        f"harness_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{uuid.uuid4().hex[:8]}.json"
    )
    if output.exists():
        raise FileExistsError(f"Recuso sobrescrever captura: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    import boto3

    region = "us-east-2"
    harness_id = HARNESS_ARN.rsplit("/", 1)[-1]
    config = boto3.client("bedrock-agentcore-control", region_name=region).get_harness(harnessId=harness_id)["harness"]
    if config.get("status") != "READY":
        raise RuntimeError(f"Harness não está pronto: {config.get('status')}")
    model_config = config.get("model", {})
    provider_config = next(iter(model_config.values()), {})
    model_id = provider_config.get("modelId")
    if not model_id:
        raise RuntimeError("Não foi possível confirmar o modelo salvo no Harness.")
    client = boto3.client("bedrock-agentcore", region_name=region)
    payload = {"tipo": "harness_capture_real", "tipo_dataset": data.get("tipo"),
               "capturado_em_utc": datetime.now(timezone.utc).isoformat(),
               "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(), "harness_arn": HARNESS_ARN,
               "harness_version": config.get("harnessVersion"), "modelo_agente": model_id,
               "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True, default=str).encode()).hexdigest(),
               "estado": "em_andamento", "total_casos_dataset": len(data["casos"]),
               "casos_selecionados": [case["id"] for case in cases], "casos": []}
    if prompt_override:
        payload["system_prompt_override_sha256"] = hashlib.sha256(
            prompt_override.encode("utf-8")
        ).hexdigest()
        payload["system_prompt_override_file"] = str(args.system_prompt_file)
    captures = payload["casos"]
    for case in cases:
        session = str(uuid.uuid4())
        cumulative = []
        turns = []
        for turn in case["turnos"]:
            request = {
                "harnessArn": HARNESS_ARN,
                "runtimeSessionId": session,
                "actorId": session,
                "messages": [{"role": "user", "content": [{"text": turn["pergunta"]}]}],
            }
            if prompt_override:
                request["systemPrompt"] = [{"text": prompt_override}]
            response = client.invoke_harness(**request)
            trace = parse_stream(response["stream"])
            checked = check_turn(turn, trace, cumulative)
            cumulative = checked.pop("evidencia_acumulada")
            turns.append({"pergunta": turn["pergunta"], "busca_esperada": turn["busca_esperada"],
                          **trace, **checked})
        captures.append({"id": case["id"], "categoria": case["categoria"],
                         "session_id": session, "turnos": turns,
                         "resposta_final": turns[-1]["resposta"],
                         "trechos_recuperados": cumulative,
                         "busca_obrigatoria_atendida": all(t["busca_obrigatoria_atendida"] for t in turns)})
        print(f"{case['id']}: {len(turns)} turno(s), busca obrigatória: {captures[-1]['busca_obrigatoria_atendida']}")
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload["estado"] = "concluido"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Captura salva em {output}")


if __name__ == "__main__":
    main()
