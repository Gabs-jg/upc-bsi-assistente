"""Avalia respostas realmente capturadas no Harness, sem simulação de scores.

Uso: python evals/frente_b_deepeval/run_deepeval_evaluations.py \
  --capture output/capturas/harness_....json \
  --calibration output/calibracao/juiz_....json

Não declara aprovação final: falhas graves exigem revisão humana separada.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATASET = ROOT / "evals" / "datasets" / "golden_dataset.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_inputs(dataset_path, capture_path, calibration_path, allow_same_judge: bool = False):
    dataset_bytes = dataset_path.read_bytes()
    dataset = json.loads(dataset_bytes)
    capture = load_json(capture_path)
    calibration = load_json(calibration_path)
    if dataset.get("tipo") != "golden_independente_sem_respostas_do_agente":
        raise ValueError("O dataset precisa ser o golden independente v2.")
    if capture.get("tipo") != "harness_capture_real":
        raise ValueError("A captura precisa vir do Harness real; arquivos antigos ou mocks são recusados.")
    estado = capture.get("estado", "")
    if not (estado == "concluido" or estado.startswith("concluido_com_")):
        raise ValueError("A captura está incompleta; preserve-a e repita os casos faltantes.")
    if capture.get("dataset_sha256") != hashlib.sha256(dataset_bytes).hexdigest():
        raise ValueError("A captura pertence a outra versão do dataset.")
    TIPOS_CALIBRACAO = ("calibracao_juiz_independente", "calibracao_juiz_qwen_self")
    if calibration.get("tipo") not in TIPOS_CALIBRACAO or not calibration.get("aprovada"):
        raise ValueError(f"Calibração aprovada é obrigatória (tipos aceitos: {TIPOS_CALIBRACAO}).")
    agent_model = capture.get("modelo_agente", "")
    judge_model = calibration.get("modelo_juiz", "")
    if not agent_model or not judge_model:
        raise ValueError("modelo_agente na captura ou modelo_juiz na calibração ausente.")
    same_model = agent_model.casefold() == judge_model.casefold()
    if same_model and not allow_same_judge:
        raise ValueError(
            "Juiz igual ao modelo do agente. Use --allow-same-judge para aceitar "
            "avaliação com juiz homogêneo (Qwen3 self-eval) e declare a limitação no relatório."
        )
    if calibration.get("modelo_agente_declarado", "").casefold() != agent_model.casefold():
        raise ValueError("A calibração foi feita para outra configuração de modelo do agente.")
    return dataset, capture, calibration, agent_model, judge_model


def retrieved_texts(case_capture):
    return [str(item["texto"]) for item in case_capture.get("trechos_recuperados", [])
            if isinstance(item, dict) and item.get("texto")]


def retrieved_context(case_capture):
    """Mantém texto e URI que a ferramenta retornou para o juiz."""
    return [
        f"Fonte recuperada: {item.get('fonte') or 'não informada'}\n{str(item['texto']).strip()}"
        for item in case_capture.get("trechos_recuperados", [])
        if isinstance(item, dict) and str(item.get("texto", "")).strip()
    ]


def cited_sources_status(answer, case_capture):
    """Confere cada arquivo .md citado contra as fontes realmente recuperadas."""
    items = [item for item in case_capture.get("trechos_recuperados", []) if isinstance(item, dict)]
    valid_uris = {str(item.get("fonte", "")) for item in items if item.get("fonte")}
    valid_names = {Path(uri).name for uri in valid_uris}
    for item in items:
        valid_names.update(
            re.findall(r"Fonte canônica:\*\*\s*`([^`]+)`", str(item.get("texto", "")))
        )
    tokens = re.findall(
        r"s3://[A-Za-z0-9_./\\-]+\.md\b|(?<![A-Za-z0-9_])[A-Za-z0-9_./\\-]+\.md\b",
        answer,
    )
    cited = [token.replace("\\_", "_") for token in tokens]
    invalid = [
        token for token in cited
        if (token not in valid_uris if token.startswith("s3://") else Path(token).name not in valid_names)
    ]
    return {"alguma_fonte_valida": bool(cited) and len(invalid) < len(cited),
            "fontes_invalidas": invalid,
            "todas_fontes_validas": bool(cited) and not invalid}


def required_search_status(case, case_capture):
    """Confere a chamada observada em cada turno que exige busca no dataset."""
    expected_turns = case.get("turnos", [])
    observed_turns = case_capture.get("turnos", [])
    if len(expected_turns) != len(observed_turns):
        return False
    return all(
        not expected.get("busca_esperada") or bool(observed.get("chamada_observada"))
        for expected, observed in zip(expected_turns, observed_turns)
    )


def deterministic_checks(case, case_capture):
    texts = retrieved_texts(case_capture)
    answer = case_capture.get("resposta_final", "")
    factual = bool(case["documentos_esperados"])
    citation = cited_sources_status(answer, case_capture)
    return {
        "resposta_presente": bool(answer.strip()),
        "busca_obrigatoria_atendida": required_search_status(case, case_capture),
        "sem_busca_fora_escopo": (
            case["categoria"] != "fora_de_escopo"
            or any(turn["busca_esperada"] for turn in case["turnos"])
            or not any(turn.get("chamada_observada") for turn in case_capture.get("turnos", []))
        ),
        "contexto_recuperado": not factual or bool(texts),
        "fonte_citada": not citation["fontes_invalidas"] and (not factual or citation["todas_fontes_validas"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--calibration", required=True, type=Path)
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--case")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--validate-only", action="store_true", help="Confere arquivos sem chamar o juiz")
    parser.add_argument(
        "--allow-same-judge", action="store_true",
        help=(
            "Aceita calibração com juiz homogêneo (mesmo modelo do agente). "
            "Declare esta limitação explicitamente no relatório final."
        ),
    )
    args = parser.parse_args()
    dataset, capture, calibration, agent_model, judge_model = verify_inputs(
        args.dataset, args.capture, args.calibration, allow_same_judge=args.allow_same_judge)
    by_id = {c["id"]: c for c in capture["casos"]}
    if len(by_id) != len(capture["casos"]):
        parser.error("A captura contém IDs de caso duplicados")
    expected_ids = {c["id"] for c in dataset["casos"]}
    if not args.case and args.limit is None and set(by_id) != expected_ids:
        parser.error("A avaliação completa exige captura de todos os casos do golden. Use --case ou --limit para uma amostra.")
    cases = [c for c in dataset["casos"] if c["id"] in by_id]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            parser.error("Caso não encontrado na captura")
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit deve ser positivo")
        cases = cases[:args.limit]
    if not cases:
        parser.error("Captura sem casos do dataset")
    if args.validate_only:
        failed = []
        for case in cases:
            checks = deterministic_checks(case, by_id[case["id"]])
            problems = [name for name, passed in checks.items() if not passed]
            if problems:
                failed.append(case["id"])
                print(f"{case['id']}: revisar {', '.join(problems)}")
            else:
                print(f"{case['id']}: verificações objetivas atendidas")
        print(f"Captura real: {len(cases)} casos; {len(failed)} com pendências objetivas; "
              f"agente={agent_model}; juiz={judge_model}. Nenhum modelo foi chamado.")
        if failed:
            raise SystemExit(1)
        return

    os.environ["BEDROCK_JUDGE_MODEL"] = judge_model
    from deepeval.test_case import LLMTestCase
    from evals.frente_b_deepeval.juiz_deepeval import (
        RUBRICA_CONFORMIDADE_VERSAO,
        build_metrics,
        build_scope_metric,
    )

    metrics = build_metrics(agent_model_id=agent_model, async_mode=False)
    results = []
    for case in cases:
        observed = by_id[case["id"]]
        checks = deterministic_checks(case, observed)
        context = retrieved_context(observed)
        history = []
        for turn in observed["turnos"][:-1]:
            history.append(f"Estudante: {turn['pergunta']}\nAssistente: {turn['resposta']}")
        current_input = ("Histórico da conversa:\n" + "\n".join(history) + "\nPergunta atual: " + case["input"]
                         if history else case["input"])
        test_case = LLMTestCase(
            input=current_input,
            actual_output=observed["resposta_final"],
            expected_output=case["resposta_esperada_referencia"],
            retrieval_context=context if context else [],
        )
        case_metrics = dict(metrics)
        if not context:
            case_metrics["geval_conformidade"] = build_scope_metric(
                agent_model_id=agent_model, async_mode=False
            )
        scores = {}
        reasons = {}
        for name, metric in case_metrics.items():
            if name in ("faithfulness", "contextual_relevancy") and not context:
                scores[name] = None
                reasons[name] = "Não aplicável: a captura não contém contexto recuperado."
                continue
            try:
                metric.measure(test_case)
                scores[name] = metric.score
                reasons[name] = metric.reason
            except Exception as error:
                scores[name] = None
                reasons[name] = f"Erro em {type(error).__name__}: {error}"
        passed = all(checks.values()) and all(
            scores[name] is not None and scores[name] >= metric.threshold
            for name, metric in case_metrics.items()
            if not (name in ("faithfulness", "contextual_relevancy") and not context)
        )
        results.append({"id": case["id"], "categoria": case["categoria"],
                        "resposta": observed["resposta_final"], "verificacoes": checks,
                        "scores": scores, "motivos": reasons, "passou_metricas_e_verificacoes": passed,
                        "revisao_humana": "pendente"})
        print(f"{case['id']}: {'passou métricas' if passed else 'revisar'}")

    output = args.output or ROOT / "output" / "avaliacoes" / f"deepeval_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    if output.exists():
        raise FileExistsError(f"Recuso sobrescrever avaliação: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"tipo": "deepeval_real_pendente_revisao_humana",
               "avaliado_em_utc": datetime.now(timezone.utc).isoformat(),
               "dataset_sha256": capture["dataset_sha256"],
               "capture_sha256": hashlib.sha256(args.capture.read_bytes()).hexdigest(),
               "modelo_agente": agent_model, "modelo_juiz": judge_model,
               "rubrica_conformidade": RUBRICA_CONFORMIDADE_VERSAO,
               "formato_contexto": "uri_fonte_mais_texto_recuperado_v2",
               "calibracao": str(args.calibration), "limiares": {k: v.threshold for k, v in metrics.items()},
               "casos": results, "aprovacao_final": "não_determinada"}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Resultado salvo em {output}. Revise manualmente todos os casos críticos.")


if __name__ == "__main__":
    main()
