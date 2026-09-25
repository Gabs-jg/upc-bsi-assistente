"""Verificações locais da proveniência das fontes, sem invocar modelos."""

from evals.frente_b_deepeval.run_deepeval_evaluations import cited_sources_status, deterministic_checks


CAPTURA = {
    "trechos_recuperados": [
        {
            "fonte": "s3://upc/documentos/regras/aproveitamento_estudos.md",
            "texto": "**Fonte canônica:** `04_regras_academicas.md`. Regras de equivalência.",
        }
    ]
}


def test_aceita_uri_e_fonte_canonica_realmente_recuperadas():
    for answer in (
        "Fonte: s3://upc/documentos/regras/aproveitamento_estudos.md",
        "Fonte: `04_regras_academicas.md`",
    ):
        assert cited_sources_status(answer, CAPTURA)["todas_fontes_validas"]


def test_rejeita_fonte_inventada_mesmo_com_outra_fonte_valida():
    answer = "Fontes: `04_regras_academicas.md` e `curso_ingresso.md`"
    status = cited_sources_status(answer, CAPTURA)
    assert not status["todas_fontes_validas"]
    assert status["fontes_invalidas"] == ["curso_ingresso.md"]


def test_rejeita_resposta_sem_fonte_recuperada():
    assert not cited_sources_status("Resposta sem citação.", CAPTURA)["todas_fontes_validas"]


def test_busca_exigida_nao_e_dispensada_por_categoria_fora_de_escopo():
    case = {
        "categoria": "fora_de_escopo",
        "turnos": [{"busca_esperada": True}],
        "documentos_esperados": ["documentos/regras/matricula_percurso.md"],
    }
    capture = {
        "resposta_final": "Não consigo realizar a matrícula.",
        "turnos": [{"chamada_observada": False}],
        "busca_obrigatoria_atendida": True,
        "trechos_recuperados": [],
    }
    checks = deterministic_checks(case, capture)
    assert not checks["busca_obrigatoria_atendida"]
    assert not checks["contexto_recuperado"]
    assert not checks["fonte_citada"]


def test_adversarial_nao_aceita_citacao_de_arquivo_apenas_mencionado():
    case = {
        "categoria": "adversarial",
        "turnos": [{"busca_esperada": True}],
        "documentos_esperados": ["documentos/curso/curso_ingresso.md"],
    }
    capture = {
        "resposta_final": "Transferência depende de edital. Fonte: `01_curso_e_ingresso.md`.",
        "turnos": [{"chamada_observada": True}],
        "trechos_recuperados": [{
            "fonte": "s3://upc/documentos/regras/matricula_percurso.md",
            "texto": "**Fonte canônica:** `04_regras_academicas.md`. Veja `01_curso_e_ingresso.md`.",
        }],
    }
    assert not deterministic_checks(case, capture)["fonte_citada"]


def test_busca_exigida_e_conferida_em_cada_turno():
    case = {
        "categoria": "multi_turno",
        "turnos": [{"busca_esperada": True}, {"busca_esperada": True}],
        "documentos_esperados": [],
    }
    capture = {
        "resposta_final": "Resposta.",
        "turnos": [{"chamada_observada": True}, {"chamada_observada": False}],
        "busca_obrigatoria_atendida": True,
        "trechos_recuperados": [],
    }
    assert not deterministic_checks(case, capture)["busca_obrigatoria_atendida"]


def test_sem_busca_esperada_nem_fatos_nao_exige_citacao():
    case = {
        "categoria": "fora_de_escopo",
        "turnos": [{"busca_esperada": False}],
        "documentos_esperados": [],
    }
    capture = {
        "resposta_final": "Posso ajudar com dúvidas acadêmicas da UPC.",
        "turnos": [{"chamada_observada": False}],
        "trechos_recuperados": [],
    }
    checks = deterministic_checks(case, capture)
    assert checks["busca_obrigatoria_atendida"]
    assert checks["contexto_recuperado"]
    assert checks["fonte_citada"]
