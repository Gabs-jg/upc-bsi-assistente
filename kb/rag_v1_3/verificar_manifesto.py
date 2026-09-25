"""Confere se o manifesto descreve exatamente os arquivos que serão enviados ao S3."""

import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent


def verificar():
    linhas = BASE.joinpath("manifesto.jsonl").read_text(encoding="utf-8").splitlines()
    entradas = [json.loads(linha) for linha in linhas if linha.strip()]
    caminhos = [entrada["path"] for entrada in entradas]
    if len(caminhos) != len(set(caminhos)):
        raise ValueError("O manifesto contém caminhos duplicados")
    arquivos = {path.relative_to(BASE).as_posix() for path in BASE.joinpath("documentos").rglob("*.md")}
    if set(caminhos) != arquivos:
        faltam = sorted(arquivos - set(caminhos))
        sobram = sorted(set(caminhos) - arquivos)
        raise ValueError(f"Manifesto diferente da pasta documentos: faltam={faltam}; sobram={sobram}")
    for entrada in entradas:
        path = BASE / entrada["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entrada["sha256"]:
            raise ValueError(f"SHA-256 divergente: {entrada['path']}")
    return len(entradas)


if __name__ == "__main__":
    print(f"Manifesto íntegro: {verificar()} documentos.")
