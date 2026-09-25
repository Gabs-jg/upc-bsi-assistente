"""Calibra a conformidade em três casos conhecidos ou cinco casos adicionais.

O conjunto adicional inclui duas respostas sintéticas, sem alterar o agente.
"""

import argparse
import json
import sys
from pathlib import Path

from deepeval.test_case import LLMTestCase

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.frente_b_deepeval.juiz_deepeval import (
    RUBRICA_CONFORMIDADE_VERSAO,
    build_metrics,
)
from evals.frente_b_deepeval.run_deepeval_evaluations import cited_sources_status

CAPTURE = ROOT / "output/capturas/harness_20260924T153740Z.json"
DATASET = ROOT / "evals/datasets/golden_dataset.json"
EXPECTED = {"GOLD-001": True, "GOLD-002": False, "GOLD-014": False}

HOLDOUT = [
    {"id": "HOLD-004", "capture_id": "GOLD-004", "aprovacao_esperada": True},
    {"id": "HOLD-006", "capture_id": "GOLD-006", "aprovacao_esperada": True},
    {"id": "HOLD-012", "capture_id": "GOLD-012", "aprovacao_esperada": True},
    {
        "id": "HOLD-006-ERRO-SINTETICO",
        "capture_id": "GOLD-006",
        "aprovacao_esperada": False,
        "resposta_sintetica": (
            "Sim. Você tem 1.915 horas curriculares e 110 horas complementares, "
            "somando 2.025 horas. Portanto, já cumpre o requisito de 1.920 horas "
            "para TCC I e pode se matricular. Fonte: tcc.md."
        ),
    },
    {
        "id": "HOLD-014-REFERENCIA-SEM-FONTE",
        "capture_id": "GOLD-014",
        "aprovacao_esperada": False,
        "resposta_sintetica": (
            "Não. A transferência externa depende de edital, vagas e classificação, "
            "sem ingresso automático. Fonte: curso_ingresso.md."
        ),
    },
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--holdout", action="store_true", help="Testa casos adicionais e dois erros sintéticos, sem alterar o agente")
    parser.add_argument("--audit-existing", type=Path, help="Revalida fontes de um resultado salvo, sem chamar a AWS")
    args = parser.parse_args()
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in capture["casos"]}
    reference_cases = {
        case["id"]: case
        for case in json.loads(DATASET.read_text(encoding="utf-8"))["casos"]
    }
    results = []
    planned = (
        HOLDOUT if args.holdout else
        [{"id": case_id, "capture_id": case_id, "aprovacao_esperada": expected_pass}
         for case_id, expected_pass in EXPECTED.items()]
    )
    if args.audit_existing:
        saved = json.loads(args.audit_existing.read_text(encoding="utf-8"))
        if saved.get("rubrica") != RUBRICA_CONFORMIDADE_VERSAO:
            raise ValueError("O arquivo salvo pertence a outra versão da rubrica.")
        planned_by_id = {item["id"]: item for item in planned}
        audited = []
        for result in saved["resultados"]:
            item = planned_by_id[result["id"]]
            observed = cases[item["capture_id"]]
            answer = item.get("resposta_sintetica", observed["resposta_final"])
            citation = cited_sources_status(answer, observed)
            combined = bool(result["aprovacao_observada"]) and citation["todas_fontes_validas"]
            updated = dict(result)
            updated.update({
                "fontes_citadas_validas": citation["todas_fontes_validas"],
                "fontes_invalidas": citation["fontes_invalidas"],
                "aprovacao_com_validacao_fontes": combined,
                "acerto_com_validacao_fontes": combined == result["aprovacao_esperada"],
            })
            audited.append(updated)
            print(f"{result['id']}: juiz={result['aprovacao_observada']} "
                  f"fontes_validas={citation['todas_fontes_validas']} conjunto={combined} "
                  f"esperado={result['aprovacao_esperada']}")
        output = args.audit_existing.with_name(args.audit_existing.stem + "_auditado.json")
        output.write_text(json.dumps({**saved, "resultados": audited}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        judge_hits = sum(item["acerto_calibracao"] for item in audited)
        combined_hits = sum(item["acerto_com_validacao_fontes"] for item in audited)
        print(f"Juiz: {judge_hits}/{len(audited)}; conjunto: {combined_hits}/{len(audited)}. Resultado: {output}")
        return 0 if all(item["acerto_com_validacao_fontes"] for item in audited) else 1
    for planned_case in planned:
        case_id = planned_case["id"]
        capture_id = planned_case["capture_id"]
        expected_pass = planned_case["aprovacao_esperada"]
        observed = cases[capture_id]
        context = [
            f"Fonte recuperada: {item.get('fonte') or 'não informada'}\n{item['texto'].strip()}"
            for item in observed["trechos_recuperados"]
            if item.get("texto", "").strip()
        ]
        metric = build_metrics(capture["modelo_agente"], async_mode=False)["geval_conformidade"]
        test_case = LLMTestCase(
            input=observed["turnos"][-1]["pergunta"],
            actual_output=planned_case.get("resposta_sintetica", observed["resposta_final"]),
            expected_output=reference_cases[capture_id]["resposta_esperada_referencia"],
            retrieval_context=context,
        )
        metric.measure(test_case, _show_indicator=False)
        passed = bool(metric.is_successful())
        citation = cited_sources_status(test_case.actual_output, observed)
        combined_pass = passed and citation["todas_fontes_validas"]
        record = {
            "id": case_id,
            "captura_id": capture_id,
            "resposta_sintetica": "resposta_sintetica" in planned_case,
            "aprovacao_esperada": expected_pass,
            "score": metric.score,
            "aprovacao_observada": passed,
            "acerto_calibracao": passed == expected_pass,
            "fontes_citadas_validas": citation["todas_fontes_validas"],
            "fontes_invalidas": citation["fontes_invalidas"],
            "aprovacao_com_validacao_fontes": combined_pass,
            "acerto_com_validacao_fontes": combined_pass == expected_pass,
            "motivo": metric.reason,
        }
        results.append(record)
        print(f"{case_id}: esperado={expected_pass} juiz={passed} score={metric.score} "
              f"fontes_validas={citation['todas_fontes_validas']} conjunto={combined_pass} "
              f"motivo={metric.reason}")
    suffix = "_holdout" if args.holdout else ""
    output = ROOT / "output/calibracao" / f"{RUBRICA_CONFORMIDADE_VERSAO}{suffix}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"rubrica": RUBRICA_CONFORMIDADE_VERSAO, "captura": str(CAPTURE), "resultados": results},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    judge_hits = sum(item["acerto_calibracao"] for item in results)
    combined_hits = sum(item["acerto_com_validacao_fontes"] for item in results)
    print(f"Juiz: {judge_hits}/{len(results)}; conjunto: {combined_hits}/{len(results)}. Resultado: {output}")
    return 0 if all(item["acerto_com_validacao_fontes"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
