"""Monta o ZIP da Lambda com o SDK Boto3 instalado no ambiente virtual.

Uso, na raiz do projeto: python src/agentcore/build_proxy_zip.py
"""

import importlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output" / "deploy" / "upc-bsi-harness-proxy-v1.zip"
MODULES = ("boto3", "botocore", "s3transfer", "jmespath", "dateutil", "urllib3")


def add_package(archive, module_name):
    module = importlib.import_module(module_name)
    directory = Path(module.__file__).resolve().parent
    for path in directory.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
            continue
        archive.write(path, (Path(module_name) / path.relative_to(directory)).as_posix())
    return getattr(module, "__version__", "sem versão declarada")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    versions = {}
    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(Path(__file__).with_name("upc_harness_proxy_lambda.py"),
                      "upc_harness_proxy_lambda.py")
        for name in MODULES:
            versions[name] = add_package(archive, name)
        six = importlib.import_module("six")
        versions["six"] = six.__version__
        archive.write(Path(six.__file__).resolve(), "six.py")
        archive.writestr("VERSOES_SDK.json", json.dumps(versions, indent=2))
    size_mb = OUTPUT.stat().st_size / 1024 / 1024
    if size_mb > 50:
        raise RuntimeError(f"ZIP de {size_mb:.1f} MB excede o limite de upload direto de 50 MB")
    with ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP com arquivo corrompido")
        assert "upc_harness_proxy_lambda.py" in archive.namelist()
    print(f"ZIP criado: {OUTPUT} ({size_mb:.1f} MB); Boto3 {versions['boto3']}")


if __name__ == "__main__":
    main()
