"""Cria uma cópia do avaliador UPC usando um juiz independente calibrado.

Não atualiza nem exclui o avaliador Qwen histórico. Execute só depois de revisar
o modelo e o custo: python .../criar_juiz_independente.py --calibration ... --name ...
"""

import argparse
import json
from pathlib import Path


TEMPLATE = Path(__file__).with_name("juiz_agentcore_fundamentacao.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
    if calibration.get("tipo") != "calibracao_juiz_independente" or not calibration.get("aprovada"):
        parser.error("Calibração independente aprovada é obrigatória")
    if calibration.get("modelo_juiz", "").casefold() == calibration.get("modelo_agente_declarado", "").casefold():
        parser.error("Juiz e agente precisam usar modelos diferentes")
    config = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    model_config = config["llmAsAJudge"]["modelConfig"]["bedrockEvaluatorModelConfig"]
    model_config["modelId"] = calibration["modelo_juiz"]
    if args.dry_run:
        print(json.dumps({"evaluatorName": args.name, "level": "TRACE",
                          "evaluatorConfig": config}, ensure_ascii=False, indent=2))
        return
    import boto3

    client = boto3.client("bedrock-agentcore-control", region_name="us-east-2")
    result = client.create_evaluator(evaluatorName=args.name,
                                     evaluatorConfig=config, level="TRACE")
    print(json.dumps({"evaluatorId": result["evaluatorId"],
                      "evaluatorArn": result["evaluatorArn"],
                      "status": result["status"],
                      "modelo_juiz": calibration["modelo_juiz"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
