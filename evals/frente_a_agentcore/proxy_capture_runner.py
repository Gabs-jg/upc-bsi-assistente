"""Captura respostas do Harness via proxy HTTP (sem credenciais AWS locais).

Uso:
  python evals/frente_a_agentcore/proxy_capture_runner.py --dry-run
  python evals/frente_a_agentcore/proxy_capture_runner.py --case GOLD-001
  python evals/frente_a_agentcore/proxy_capture_runner.py --all

Lê UPC_API_URL e UPC_API_TOKEN de .env / .env.proxy.
Produz output/capturas/harness_proxy_TIMESTAMP.json no mesmo formato que
agentcore_eval_runner.py, compatível com run_deepeval_evaluations.py.

Cada caso recebe uma sessão própria. Os turnos do mesmo caso compartilham sessão.
"""

import argparse
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
import os


ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "evals" / "datasets" / "golden_dataset.json"
MODELO_AGENTE = "qwen.qwen3-next-80b-a3b"   # modelo salvo no Harness
TOOL_NAME = "consultar_base_upc"
THROTTLE_SECONDS = 1.2   # aguarda entre turnos para respeitar o limite de 1 req/s


def load_env():
    """Carrega .env e .env.proxy da raiz do repositório."""
    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(ROOT / ".env.proxy", override=False)


def read_config():
    """Retorna (url, token) a partir das variáveis de ambiente."""
    url = os.getenv("UPC_API_URL", "").strip()
    token = os.getenv("UPC_API_TOKEN", "").strip()
    if not url:
        raise SystemExit(
            "UPC_API_URL não encontrada.\n"
            "Adicione ao .env (ou .env.proxy):\n"
            "  UPC_API_URL=https://ID.execute-api.us-east-2.amazonaws.com/perguntar"
        )
    if not token:
        raise SystemExit(
            "UPC_API_TOKEN não encontrado.\n"
            "Execute primeiro: python src/agentcore/criar_token_proxy.py"
        )
    return url, token


def send_turn(url: str, token: str, question: str, session_id: str | None) -> dict:
    payload = {"pergunta": question}
    if session_id:
        payload["session_id"] = session_id
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urlopen(request, timeout=90) as response:
        return json.load(response)


def extract_trechos(fontes: list[str], resposta: str) -> list[dict]:
    """Monta trechos mínimos a partir da lista de fontes retornada pelo proxy."""
    trechos = []
    for fonte in fontes:
        if not isinstance(fonte, str):
            continue
        # A resposta pode citar a fonte; registramos o que temos.
        trechos.append({"fonte": fonte, "texto": ""})
    return trechos


def validate_dataset(data: dict):
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
        raise ValueError("IDs duplicados no dataset")


def select_cases(data: dict, args) -> list:
    cases = data["casos"]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            raise ValueError(f"Caso não encontrado: {args.case}")
    if args.limit is not None:
        cases = cases[:args.limit]
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case", metavar="ID", help="Captura apenas um caso (ex: GOLD-001)")
    group.add_argument("--limit", type=int, metavar="N", help="Captura os primeiros N casos")
    group.add_argument("--all", action="store_true", help="Captura todos os 15 casos")
    group.add_argument("--dry-run", action="store_true", help="Valida dataset e configuração sem chamar a API")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path, help="Caminho de saída do JSON (opcional)")
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit deve ser positivo")

    load_env()

    dataset_bytes = args.dataset.read_bytes()
    data = json.loads(dataset_bytes)
    validate_dataset(data)
    cases = select_cases(data, args)

    if args.dry_run:
        url, token = read_config()
        print(f"Configuração válida.")
        print(f"  URL: {url}")
        print(f"  Token: {'*' * 8}{token[-4:]}")
        print(f"  Dataset: {len(data['casos'])} casos totais, {len(cases)} selecionados.")
        print("Nenhuma chamada à API foi feita.")
        return

    url, token = read_config()

    output = args.output or (
        ROOT / "output" / "capturas" / f"harness_proxy_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )
    if output.exists():
        raise FileExistsError(f"Recuso sobrescrever captura existente: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "tipo": "harness_capture_real",
        "fonte": "proxy_http",
        "tipo_dataset": data.get("tipo"),
        "capturado_em_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_sha256": hashlib.sha256(dataset_bytes).hexdigest(),
        "proxy_url": re.sub(r"https?://[^/]+", "https://***", url),
        "modelo_agente": MODELO_AGENTE,
        "estado": "em_andamento",
        "total_casos_dataset": len(data["casos"]),
        "casos_selecionados": [c["id"] for c in cases],
        "casos": [],
        "aviso": (
            "Captura via proxy HTTP. Os trechos_recuperados contêm apenas as fontes "
            "retornadas pelo proxy, sem o texto completo dos chunks da KB. "
            "Faithfulness e Contextual Relevancy serão ignoradas pelo avaliador "
            "quando texto estiver vazio."
        ),
    }
    captures = payload["casos"]

    for case in cases:
        session_id = str(uuid.uuid4())
        cumulative_trechos: list[dict] = []
        turns_out = []
        last_error = None

        for turn in case["turnos"]:
            if turns_out:
                time.sleep(THROTTLE_SECONDS)
            try:
                result = send_turn(url, token, turn["pergunta"], session_id)
            except HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.reason}"
                print(f"  ✗ {case['id']} turno «{turn['pergunta'][:50]}»: {last_error}")
                break
            except (URLError, TimeoutError, OSError) as exc:
                last_error = str(exc)
                print(f"  ✗ {case['id']} turno «{turn['pergunta'][:50]}»: {last_error}")
                break

            # O proxy devolve session_id na primeira resposta; reutilizamos.
            session_id = result.get("session_id", session_id)
            resposta = result.get("resposta", "")
            fontes = result.get("fontes_recuperadas") or []
            busca_executada = bool(result.get("busca_executada"))
            trechos = extract_trechos(fontes, resposta)
            cumulative_trechos.extend(trechos)

            turns_out.append({
                "pergunta": turn["pergunta"],
                "busca_esperada": turn["busca_esperada"],
                "resposta": resposta,
                "busca_obrigatoria_atendida": (not turn["busca_esperada"]) or busca_executada,
                "chamada_observada": busca_executada,
                "resultado_observado": busca_executada and bool(fontes),
                "fontes_proxy": fontes,
                "trechos_recuperados": trechos,
            })

        if last_error or len(turns_out) != len(case["turnos"]):
            # Salva o progresso parcial e continua com os próximos casos
            captures.append({
                "id": case["id"],
                "categoria": case["categoria"],
                "session_id": session_id,
                "turnos": turns_out,
                "resposta_final": turns_out[-1]["resposta"] if turns_out else "",
                "trechos_recuperados": cumulative_trechos,
                "busca_obrigatoria_atendida": False,
                "erro": last_error or "turnos incompletos",
            })
            print(f"{case['id']}: FALHA ({last_error or 'turnos incompletos'})")
        else:
            busca_atendida = all(t["busca_obrigatoria_atendida"] for t in turns_out)
            captures.append({
                "id": case["id"],
                "categoria": case["categoria"],
                "session_id": session_id,
                "turnos": turns_out,
                "resposta_final": turns_out[-1]["resposta"],
                "trechos_recuperados": cumulative_trechos,
                "busca_obrigatoria_atendida": busca_atendida,
            })
            print(f"{case['id']}: OK — {len(turns_out)} turno(s), busca atendida: {busca_atendida}")

        # Salva progresso a cada caso para não perder dados em caso de interrupção
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    falhas = sum(1 for c in captures if "erro" in c)
    if falhas == 0:
        payload["estado"] = "concluido"
    else:
        payload["estado"] = f"concluido_com_{falhas}_falhas"

    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nCaptura salva em {output}")
    if falhas:
        print(f"⚠ {falhas} caso(s) com falha. Verifique o arquivo e reexecute com --case para os casos faltantes.")


if __name__ == "__main__":
    main()
