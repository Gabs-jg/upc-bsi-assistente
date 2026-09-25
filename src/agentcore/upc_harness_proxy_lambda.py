"""Endpoint HTTP autenticado para o Harness da UPC.

Pode servir como autorizador Lambda e integração da rota POST /perguntar de uma
HTTP API. O token é comparado novamente na integração antes de invocar o
Harness, mesmo se a rota for configurada sem autorizador por engano.
"""

import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import uuid


SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{32,99}\Z")
MAX_BODY_BYTES = 4096
MAX_QUESTION_CHARS = 1500


def http_response(status, body):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json; charset=utf-8", "cache-control": "no-store"},
        "body": json.dumps(body, ensure_ascii=False),
    }


def jwt_subject(event):
    claims = (event.get("requestContext", {}).get("authorizer", {})
              .get("jwt", {}).get("claims", {}))
    subject = claims.get("sub") if isinstance(claims, dict) else None
    return subject if isinstance(subject, str) and subject.strip() else None


def bearer_subject(event):
    """Valida o token de demonstração sem armazená-lo em texto claro na AWS."""
    expected_hash = os.environ.get("API_TOKEN_SHA256", "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        return None
    headers = event.get("headers") or {}
    if not isinstance(headers, dict):
        return None
    authorization = next((value for key, value in headers.items()
                          if isinstance(key, str) and key.lower() == "authorization"), None)
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    if not 32 <= len(token) <= 256:
        return None
    actual_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return "aluno-demo-upc" if hmac.compare_digest(actual_hash, expected_hash) else None


def authenticated_subject(event):
    return jwt_subject(event) or bearer_subject(event)


def request_json(event):
    raw = event.get("body", "")
    if not isinstance(raw, str):
        raise ValueError("Corpo JSON inválido")
    if event.get("isBase64Encoded"):
        try:
            payload = base64.b64decode(raw, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("Corpo base64 inválido") from error
    else:
        payload = raw.encode("utf-8")
    if len(payload) > MAX_BODY_BYTES:
        raise ValueError("A solicitação é muito longa")
    try:
        data = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Corpo JSON inválido") from error
    if not isinstance(data, dict):
        raise ValueError("Envie um objeto JSON")
    question = data.get("pergunta")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Informe a pergunta")
    question = question.strip()
    if len(question) > MAX_QUESTION_CHARS:
        raise ValueError("A pergunta é muito longa")
    session_id = data.get("session_id")
    if session_id is None:
        session_id = str(uuid.uuid4())
    if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
        raise ValueError("session_id inválido")
    return question, session_id


def unpack_results(value):
    """Encontra resultados do Gateway em conteúdo JSON ou texto JSON aninhado."""
    if isinstance(value, str):
        try:
            return unpack_results(json.loads(value))
        except json.JSONDecodeError:
            return []
    if isinstance(value, dict):
        if isinstance(value.get("resultados"), list):
            return value["resultados"]
        for child in value.values():
            found = unpack_results(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = unpack_results(child)
            if found:
                return found
        # O Harness pode dividir um único JSON de resultado em vários deltas
        # de texto. Cada fragmento isolado não é um documento JSON válido.
        text_parts = [child["text"] for child in value
                      if isinstance(child, dict) and isinstance(child.get("text"), str)]
        if text_parts:
            return unpack_results("".join(text_parts))
    return []


def read_harness_stream(stream):
    """Lê resposta final, chamadas reais e fontes de eventos InvokeHarness."""
    role = None
    blocks = {}
    answers = []
    tool_calls = set()
    tool_results = []
    for event in stream:
        if "messageStart" in event:
            role = event["messageStart"].get("role")
            blocks = {}
        elif "contentBlockStart" in event:
            payload = event["contentBlockStart"]
            start = payload.get("start", {})
            blocks[payload["contentBlockIndex"]] = {
                "type": next(iter(start), "text"), "start": start, "parts": []}
        elif "contentBlockDelta" in event:
            payload = event["contentBlockDelta"]
            block = blocks.setdefault(payload["contentBlockIndex"],
                                      {"type": "text", "start": {}, "parts": []})
            delta = payload.get("delta", {})
            if block["type"] == "text" and "text" in delta:
                block["parts"].append(delta["text"])
            elif block["type"] == "toolResult" and "toolResult" in delta:
                block["parts"].extend(delta["toolResult"])
        elif "contentBlockStop" in event:
            block = blocks.get(event["contentBlockStop"]["contentBlockIndex"], {})
            if block.get("type") == "toolUse":
                tool = block["start"]["toolUse"]
                if "consultar_base_upc" in tool.get("name", ""):
                    tool_calls.add(tool.get("toolUseId"))
            elif block.get("type") == "toolResult":
                result = block["start"]["toolResult"]
                # A API permite omitir status; somente "error" indica falha.
                if result.get("status") != "error":
                    tool_results.append((result.get("toolUseId"), unpack_results(block["parts"])))
        elif "messageStop" in event:
            if role == "assistant":
                answer = "\n".join("".join(block["parts"]) for block in blocks.values()
                                   if block["type"] == "text").strip()
                if answer:
                    answers.append(answer)
            role = None
            blocks = {}
        elif any(key in event for key in ("runtimeClientError", "validationException", "internalServerException")):
            raise RuntimeError("Falha no fluxo do Harness")
    if not answers:
        raise RuntimeError("Harness sem resposta textual")
    sources = []
    for tool_id, results in tool_results:
        if tool_id not in tool_calls:
            continue
        for item in results:
            if isinstance(item, dict) and isinstance(item.get("fonte"), str):
                source = item["fonte"]
                if source and source not in sources:
                    sources.append(source)
    return answers[-1], bool(tool_calls), sources


def invoke(client, harness_arn, subject, session_id, question):
    actor_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"upc-actor:{subject}"))
    runtime_session = str(uuid.uuid5(uuid.NAMESPACE_URL, f"upc-session:{subject}:{session_id}"))
    response = client.invoke_harness(
        harnessArn=harness_arn,
        runtimeSessionId=runtime_session,
        actorId=actor_id,
        messages=[{"role": "user", "content": [{"text": question}]}],
    )
    return read_harness_stream(response["stream"])


def lambda_handler(event, context):
    if not isinstance(event, dict):
        return http_response(400, {"erro": "Solicitação inválida"})
    if event.get("version") == "2.0" and event.get("type") == "REQUEST":
        subject = bearer_subject(event)
        if subject:
            return {"isAuthorized": True, "context": {"sub": subject}}
        return {"isAuthorized": False}
    if event.get("requestContext", {}).get("http", {}).get("method") != "POST":
        return http_response(405, {"erro": "Use POST"})
    subject = authenticated_subject(event)
    if not subject:
        return http_response(401, {"erro": "Autenticação necessária"})
    try:
        question, session_id = request_json(event)
    except ValueError as error:
        return http_response(400, {"erro": str(error)})
    harness_arn = os.environ.get("HARNESS_ARN", "").strip()
    if not harness_arn:
        return http_response(503, {"erro": "Assistente não configurado"})
    try:
        import boto3

        client = boto3.client("bedrock-agentcore", region_name="us-east-2")
        answer, tool_called, sources = invoke(client, harness_arn, subject, session_id, question)
    except Exception as error:
        print(json.dumps({"evento": "erro_proxy_upc", "tipo": type(error).__name__}))
        return http_response(502, {"erro": "Não foi possível consultar o assistente agora"})
    return http_response(200, {"session_id": session_id, "resposta": answer,
                               "busca_executada": tool_called, "fontes_recuperadas": sources})
