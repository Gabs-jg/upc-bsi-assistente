"""Testes locais do proxy HTTP; nenhum deles chama a AWS."""

import json
import hashlib
from unittest.mock import Mock

from src.agentcore.upc_harness_proxy_lambda import invoke, lambda_handler, read_harness_stream


def event(body, subject="aluno-1", method="POST"):
    return {"requestContext": {"http": {"method": method},
                               "authorizer": {"jwt": {"claims": {"sub": subject}}}},
            "body": json.dumps(body)}


def harness_events():
    return [
        {"messageStart": {"role": "assistant"}},
        {"contentBlockStart": {"contentBlockIndex": 0, "start": {"toolUse": {
            "name": "BuscaUPC___consultar_base_upc", "toolUseId": "u1"}}}},
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {"messageStop": {"stopReason": "tool_use"}},
        {"messageStart": {"role": "assistant"}},
        {"contentBlockStart": {"contentBlockIndex": 0, "start": {"toolResult": {
            "toolUseId": "u1", "status": "success"}}}},
        {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"toolResult": [{
            "text": json.dumps({"resultados": [{"texto": "VII é referência",
                                            "fonte": "s3://bucket/documentos/percurso/tcc.md"}]})}]}}},
        {"contentBlockStop": {"contentBlockIndex": 0}},
        {"contentBlockStart": {"contentBlockIndex": 1, "start": {}}},
        {"contentBlockDelta": {"contentBlockIndex": 1, "delta": {"text": "Pode cursar depois."}}},
        {"contentBlockStop": {"contentBlockIndex": 1}},
        {"messageStop": {"stopReason": "end_turn"}},
    ]


def test_resposta_e_fontes_sao_extraidas_do_fluxo():
    answer, called, sources = read_harness_stream(harness_events())
    assert answer == "Pode cursar depois."
    assert called
    assert sources == ["s3://bucket/documentos/percurso/tcc.md"]


def test_fontes_de_resultado_json_fragmentado():
    events = harness_events()
    delta = events[6]["contentBlockDelta"]["delta"]
    whole = delta["toolResult"][0]["text"]
    midpoint = len(whole) // 2
    delta["toolResult"] = [{"text": whole[:midpoint]}]
    events.insert(7, {"contentBlockDelta": {"contentBlockIndex": 0,
                                              "delta": {"toolResult": [{"text": whole[midpoint:]}]}}})
    answer, called, sources = read_harness_stream(events)
    assert answer == "Pode cursar depois."
    assert called
    assert sources == ["s3://bucket/documentos/percurso/tcc.md"]


def test_fontes_quando_status_do_resultado_e_omitido():
    events = harness_events()
    del events[5]["contentBlockStart"]["start"]["toolResult"]["status"]
    _, called, sources = read_harness_stream(events)
    assert called
    assert sources == ["s3://bucket/documentos/percurso/tcc.md"]


def test_sessoes_sao_isoladas_por_usuario():
    client = Mock()
    client.invoke_harness.side_effect = lambda **kwargs: {"stream": harness_events()}
    invoke(client, "arn:harness", "aluno-1", "12345678-1234-1234-1234-123456789012", "TCC?")
    invoke(client, "arn:harness", "aluno-2", "12345678-1234-1234-1234-123456789012", "TCC?")
    first, second = [call.kwargs for call in client.invoke_harness.call_args_list]
    assert first["runtimeSessionId"] != second["runtimeSessionId"]
    assert first["actorId"] != second["actorId"]


def test_rejeita_chamada_sem_jwt_antes_de_invocar(monkeypatch):
    monkeypatch.setenv("HARNESS_ARN", "arn:harness")
    monkeypatch.delenv("API_TOKEN_SHA256", raising=False)
    unauthorized = event({"pergunta": "TCC?"})
    unauthorized["requestContext"].pop("authorizer")
    assert lambda_handler(unauthorized, None)["statusCode"] == 401


def test_autorizador_valida_token_privado(monkeypatch):
    token = "a" * 43
    monkeypatch.setenv("API_TOKEN_SHA256", hashlib.sha256(token.encode()).hexdigest())
    request = {"version": "2.0", "type": "REQUEST", "routeArn": "arn:api",
               "headers": {"authorization": f"Bearer {token}"}}
    assert lambda_handler(request, None) == {
        "isAuthorized": True, "context": {"sub": "aluno-demo-upc"}}
    request["headers"]["authorization"] = "Bearer " + "b" * 43
    assert lambda_handler(request, None) == {"isAuthorized": False}


def test_integracao_confere_token_mesmo_sem_autorizador(monkeypatch):
    token = "a" * 43
    monkeypatch.setenv("API_TOKEN_SHA256", hashlib.sha256(token.encode()).hexdigest())
    monkeypatch.setenv("HARNESS_ARN", "arn:harness")
    request = event({"pergunta": "TCC?"})
    request["requestContext"].pop("authorizer")
    request["headers"] = {"Authorization": f"Bearer {token}"}
    client = Mock()
    client.invoke_harness.return_value = {"stream": harness_events()}
    import boto3
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: client)
    assert lambda_handler(request, None)["statusCode"] == 200
    request["headers"]["Authorization"] = "Bearer " + "b" * 43
    assert lambda_handler(request, None)["statusCode"] == 401


def test_rejeita_sessao_invalida(monkeypatch):
    monkeypatch.setenv("HARNESS_ARN", "arn:harness")
    assert lambda_handler(event({"pergunta": "TCC?", "session_id": "curta"}), None)["statusCode"] == 400


def test_rejeita_metodo_incorreto():
    assert lambda_handler(event({"pergunta": "TCC?"}, method="GET"), None)["statusCode"] == 405


def test_chamada_valida_retorna_resposta(monkeypatch):
    import boto3

    monkeypatch.setenv("HARNESS_ARN", "arn:harness")
    client = Mock()
    client.invoke_harness.return_value = {"stream": harness_events()}
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: client)
    response = lambda_handler(event({"pergunta": "TCC?"}), None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body["resposta"] == "Pode cursar depois."
    assert body["busca_executada"]
    assert len(body["session_id"]) >= 33
