"""Conversa com o proxy HTTPS da UPC sem usar credenciais AWS locais.

Uso: python src/agentcore/cliente_http_proxy.py --url https://.../perguntar
Lê UPC_API_TOKEN de .env.proxy, criado por criar_token_proxy.py.
"""

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]


def read_token():
    token_file = ROOT / ".env.proxy"
    try:
        lines = token_file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit("Token local ausente. Execute criar_token_proxy.py primeiro.")
    for line in lines:
        if line.startswith("UPC_API_TOKEN="):
            return line.partition("=")[2].strip()
    raise SystemExit("UPC_API_TOKEN não encontrado em .env.proxy")


def send_question(url, token, question, session_id=None):
    payload = {"pergunta": question}
    if session_id:
        payload["session_id"] = session_id
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urlopen(request, timeout=70) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description="Cliente local do assistente UPC")
    parser.add_argument("--url", required=True, help="URL HTTPS da rota POST /perguntar")
    arguments = parser.parse_args()
    parsed = urlparse(arguments.url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path != "/perguntar":
        parser.error("Informe a URL HTTPS completa terminada em /perguntar")
    token = read_token()
    session_id = None
    print("Digite uma pergunta por vez. Enter vazio encerra a conversa.")
    while True:
        question = input("Você: ").strip()
        if not question:
            break
        try:
            result = send_question(arguments.url, token, question, session_id)
        except HTTPError as error:
            print(f"HTTP {error.code}: não foi possível obter uma resposta.")
            continue
        except (URLError, TimeoutError) as error:
            print(f"Falha de conexão: {error.reason if isinstance(error, URLError) else error}")
            continue
        session_id = result.get("session_id", session_id)
        print("Assistente:", result.get("resposta", result.get("erro", "Resposta vazia")))
        print("Busca executada:", result.get("busca_executada"))
        if result.get("fontes_recuperadas"):
            print("Fontes recuperadas:", ", ".join(result["fontes_recuperadas"]))


if __name__ == "__main__":
    main()
