"""Cria um token privado local para a API de demonstração da UPC.

Uso, na raiz do projeto: python src/agentcore/criar_token_proxy.py
O arquivo .env.proxy é ignorado pelo Git. Copie apenas o hash exibido para a
variável API_TOKEN_SHA256 da Lambda; não envie o token para chats ou commits.
"""

import hashlib
import secrets
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOKEN_FILE = ROOT / ".env.proxy"


def main():
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    try:
        with TOKEN_FILE.open("x", encoding="utf-8") as output:
            output.write(f"UPC_API_TOKEN={token}\n")
    except FileExistsError:
        raise SystemExit(f"{TOKEN_FILE} já existe; o token atual foi preservado.")
    print(f"Token privado salvo em: {TOKEN_FILE}")
    print(f"API_TOKEN_SHA256={digest}")


if __name__ == "__main__":
    main()
