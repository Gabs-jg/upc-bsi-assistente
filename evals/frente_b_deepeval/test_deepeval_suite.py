r"""Avalia capturas reais do Harness com as três métricas pedidas no Desafio 2.

No PowerShell, opcionalmente selecione a captura antes de executar:
  $env:UPC_DEEPEVAL_CAPTURE = 'output/capturas/harness_....json'
  .\.venv\Scripts\deepeval.exe test run evals/frente_b_deepeval/test_deepeval_suite.py

Sem a variável, usa a captura direta mais recente que contenha os 15 casos do
Golden Dataset. As capturas do proxy não incluem os textos recuperados e não
servem como retrieval_context de Faithfulness.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=False)
load_dotenv(ROOT / ".env.proxy", override=False)

from deepeval.test_case import LLMTestCase
from evals.frente_b_deepeval.juiz_deepeval import (
    RUBRICA_CONFORMIDADE_VERSAO,
    build_diagnostic_metrics,
    build_metrics,
    build_scope_metric,
)
from evals.frente_b_deepeval.run_deepeval_evaluations import deterministic_checks

DATASET_PATH = ROOT / "evals" / "datasets" / "golden_dataset.json"
DATASET_BYTES = DATASET_PATH.read_bytes()
DATASET = json.loads(DATASET_BYTES)["casos"]
EXPECTED_IDS = {case["id"] for case in DATASET}
RUN_ID = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{uuid4().hex[:8]}"


def _read_valid_capture(path):
    capture = json.loads(path.read_text(encoding="utf-8"))
    if capture.get("tipo") != "harness_capture_real" or capture.get("estado") != "concluido":
        raise ValueError(f"Captura inválida ou incompleta: {path}")
    if capture.get("dataset_sha256") != hashlib.sha256(DATASET_BYTES).hexdigest():
        raise ValueError(f"Captura de outra versão do Golden Dataset: {path}")
    cases = capture.get("casos", [])
    if len(cases) != len(EXPECTED_IDS) or {case.get("id") for case in cases} != EXPECTED_IDS:
        raise ValueError(f"A captura deve conter exatamente os 15 casos GOLD: {path}")
    if not capture.get("modelo_agente"):
        raise ValueError(f"Modelo do agente não registrado: {path}")
    for case in cases:
        for item in case.get("trechos_recuperados", []):
            if not isinstance(item, dict) or not item.get("texto", "").strip():
                raise ValueError(f"Trecho recuperado sem texto em {case['id']}: {path}")
    return capture


def select_capture():
    candidates = sorted(
        (path for path in (ROOT / "output" / "capturas").glob("harness_*.json")
         if not path.name.startswith("harness_proxy_")),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    selected = os.getenv("UPC_DEEPEVAL_CAPTURE")
    if selected:
        path = Path(selected)
        if not path.is_absolute():
            path = ROOT / path
        capture = _read_valid_capture(path)
        if os.getenv("UPC_DEEPEVAL_ALLOW_OLD_CAPTURE", "0").lower() not in ("1", "true", "yes"):
            for candidate in candidates:
                if candidate.stat().st_mtime <= path.stat().st_mtime:
                    break
                try:
                    _read_valid_capture(candidate)
                except ValueError:
                    continue
                raise ValueError(
                    f"UPC_DEEPEVAL_CAPTURE aponta para captura antiga: {path}. "
                    f"Existe uma captura completa mais recente: {candidate}. "
                    "Atualize UPC_DEEPEVAL_CAPTURE ou remova a variável. "
                    "Para uma comparação histórica intencional, defina "
                    "UPC_DEEPEVAL_ALLOW_OLD_CAPTURE=1."
                )
        return path, capture
    for path in candidates:
        try:
            return path, _read_valid_capture(path)
        except ValueError:
            continue
    raise FileNotFoundError("Nenhuma captura direta e completa do Golden Dataset foi encontrada.")


CAPTURE_PATH, CAPTURE = select_capture()
CAPTURE_MAP = {case["id"]: case for case in CAPTURE["casos"]}


def safe_print(message=""):
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        print(str(message).encode("ascii", errors="replace").decode("ascii"), flush=True)


def _case_input(case, observed):
    history = [
        f"Estudante: {turn['pergunta']}\nAssistente: {turn['resposta']}"
        for turn in observed.get("turnos", [])[:-1]
    ]
    return "Histórico da conversa:\n" + "\n".join(history) + "\nPergunta atual: " + case["input"] if history else case["input"]


def _retrieval_context(observed):
    """Entrega ao juiz o texto e a URI que a ferramenta realmente retornou."""
    return [
        f"Fonte recuperada: {item.get('fonte') or 'não informada'}\n{item['texto'].strip()}"
        for item in observed.get("trechos_recuperados", [])
        if item.get("texto", "").strip()
    ]


@pytest.mark.parametrize("case", DATASET, ids=lambda case: case["id"])
def test_upc_assistente(case):
    observed = CAPTURE_MAP[case["id"]]
    answer = observed.get("resposta_final", "")
    context = _retrieval_context(observed)
    checks = deterministic_checks(case, observed)
    has_required_search = checks["busca_obrigatoria_atendida"]
    has_required_context = checks["contexto_recuperado"]
    cited_source = checks["fonte_citada"]
    if not answer.strip():
        pytest.fail(f"Resposta ausente na captura: {case['id']}")

    test_case = LLMTestCase(
        input=_case_input(case, observed),
        actual_output=answer,
        expected_output=case.get("resposta_esperada_referencia"),
        retrieval_context=context if context else [],
    )
    all_metrics = build_metrics(agent_model_id=CAPTURE["modelo_agente"], async_mode=False)
    selected_metrics = {"Answer Relevancy": all_metrics["answer_relevancy"]}
    if context:
        selected_metrics["Faithfulness"] = all_metrics["faithfulness"]
        selected_metrics["Conformidade UPC"] = all_metrics["geval_conformidade"]
    else:
        selected_metrics["Conformidade UPC sem contexto"] = build_scope_metric(
            agent_model_id=CAPTURE["modelo_agente"], async_mode=False
        )
    required_names = tuple(selected_metrics)
    if os.getenv("UPC_DEEPEVAL_DIAGNOSTICOS", "0").strip().lower() in ("1", "true", "yes"):
        diagnostics = build_diagnostic_metrics(CAPTURE["modelo_agente"], async_mode=False)
        selected_metrics["Relevância de domínio (diagnóstico)"] = diagnostics["Relevância de domínio (diagnóstico)"]
        if context:
            selected_metrics["Fundamentação lógica (diagnóstico)"] = diagnostics["Fundamentação lógica (diagnóstico)"]

    safe_print("\n" + "=" * 80)
    safe_print(f"ID: {case['id']}")
    safe_print(f"Categoria: {case['categoria'].replace('_', ' ').capitalize()}")
    safe_print(f"Input: {case['input']}")
    safe_print(f"Resposta: {answer}")
    safe_print(f"Contexto: {len(context)} trecho(s) realmente recuperado(s)")
    for index, item in enumerate(observed.get("trechos_recuperados", []), start=1):
        preview = " ".join(item["texto"].split())
        if len(preview) > 450:
            preview = preview[:447].rstrip() + "..."
        safe_print(f"  [{index}] {preview}")
        safe_print(f"      Fonte: {item.get('fonte') or 'não informada'}")
    safe_print("Os trechos completos estão no arquivo de captura indicado abaixo.")
    safe_print(f"Captura: {CAPTURE_PATH}")

    scores = {}
    evaluation_error = None

    # Avalia cada métrica em sequência. Uma métrica nativa pode fazer várias
    # chamadas ao juiz durante measure(); não presumir custo de uma chamada.
    for name, metric in selected_metrics.items():
        safe_print(f"\n--- Avaliando: {name} ---")
        try:
            metric.measure(test_case)
        except Exception as error:
            evaluation_error = evaluation_error or error

        try:
            success = metric.is_successful() if metric.score is not None else False
        except Exception:
            success = False

        scores[name] = {
            "score": metric.score,
            "reason": metric.reason,
            "success": success,
            "threshold": metric.threshold,
            "classe": type(metric).__name__,
            "erro": str(metric.error) if metric.error else None,
        }
        safe_print(f"MÉTRICA: {name}")
        safe_print(f"Score: {metric.score if metric.score is not None else 'indisponível'}")
        safe_print(f"Reason: {metric.reason or 'Não gerado.'}")
        safe_print(f"Success: {success}")
        if metric.error:
            safe_print(f"Erro: {metric.error}")

        result_path = ROOT / "output" / "avaliacoes" / f"deepeval_suite_{RUN_ID}.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result = {"tipo": "deepeval_suite_captura_real", "captura": str(CAPTURE_PATH),
                  "capture_sha256": hashlib.sha256(CAPTURE_PATH.read_bytes()).hexdigest(),
                  "dataset_sha256": hashlib.sha256(DATASET_BYTES).hexdigest(),
                  "modelo_agente": CAPTURE["modelo_agente"],
                  "modelo_juiz": os.getenv("BEDROCK_JUDGE_MODEL", "qwen.qwen3-next-80b-a3b").strip(),
                  "formato_contexto": "uri_fonte_mais_texto_recuperado_v2",
                  "rubrica_conformidade": RUBRICA_CONFORMIDADE_VERSAO, "casos": {}}
        if result_path.exists():
            result = json.loads(result_path.read_text(encoding="utf-8"))
        result["casos"][case["id"]] = {
            "id": case["id"], "categoria": case["categoria"], "input": case["input"],
            "resposta": answer, "trechos_recuperados": len(context),
            "busca_obrigatoria_atendida": bool(has_required_search),
            "contexto_obrigatorio_presente": bool(has_required_context),
            "fonte_citada": bool(cited_source),
            "metricas": scores, "erro": str(evaluation_error) if evaluation_error else None,
        }
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if evaluation_error:
        pytest.fail(f"Erro na avaliação DeepEval: {type(evaluation_error).__name__}: {evaluation_error}")
    missing_scores = [name for name in required_names if selected_metrics[name].score is None]
    if missing_scores:
        pytest.fail(f"Métricas sem pontuação: {', '.join(missing_scores)}")
    failed_metrics = [name for name in required_names if not selected_metrics[name].is_successful()]
    assert not failed_metrics, f"Métricas abaixo do limiar: {', '.join(failed_metrics)}"
    assert has_required_search, f"Busca obrigatória não executada em {case['id']}"
    assert has_required_context, f"Contexto obrigatório ausente em {case['id']}"
    assert cited_source, f"Fonte recuperada não citada na resposta: {case['id']}"
