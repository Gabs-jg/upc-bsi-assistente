"""Configuração predefinida dos juízes e métricas DeepEval da UPC (Frente B).

Limites fixados antes da avaliação:
- Answer Relevancy >= 0.70
- Faithfulness >= 0.80
- Contextual Relevancy >= 0.70 nos casos com busca
- G-Eval de conformidade UPC >= 0.80

Pode ser executado com AWS Bedrock (Qwen3 Next, Claude ou outro juiz)
ou adaptado para outros provedores LLM. As credenciais são carregadas do ambiente
(cadeia padrão AWS, CloudShell ou arquivo .env).
"""

import os
from typing import Dict
from dotenv import load_dotenv

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    GEval,
)
from deepeval.models import AmazonBedrockModel
from deepeval.metrics.g_eval.utils import Rubric
from deepeval.test_case import SingleTurnParams

# Carrega variáveis de ambiente de um eventual .env
load_dotenv(override=True)

BEDROCK_REGION = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-2"))


def get_judge_model(agent_model_id: str):
    """Instancia o modelo juiz do Amazon Bedrock com as credenciais disponíveis."""
    model_id = os.getenv("BEDROCK_JUDGE_MODEL", "qwen.qwen3-next-80b-a3b").strip()
    allow_same = os.getenv("ALLOW_SAME_JUDGE", "true").strip().lower() in ("1", "true", "yes")
    if not model_id:
        raise ValueError("Defina BEDROCK_JUDGE_MODEL com o modelo juiz desejado.")
    if model_id.casefold() == agent_model_id.casefold() and not allow_same:
        raise ValueError("O juiz não pode usar o mesmo modelo do agente nesta avaliação sem ALLOW_SAME_JUDGE=1.")
    kwargs = {"temperature": 0, "maxTokens": 4096}
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")

    if aws_access_key and aws_secret_key:
        return AmazonBedrockModel(
            model=model_id,
            region=BEDROCK_REGION,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
            generation_kwargs=kwargs,
        )
    return AmazonBedrockModel(
        model=model_id,
        region=BEDROCK_REGION,
        generation_kwargs=kwargs,
    )


RUBRICA_CONFORMIDADE_VERSAO = "upc_conformidade_v4_referencia"

CRITERIO_RELEVANCIA_DOMINIO = (
    "Avalie se a resposta atende à intenção da pergunta atual. Uma recusa educada "
    "é pertinente quando o pedido está fora do escopo acadêmico da UPC, exige "
    "inventar dados, ignorar documentos ou executar uma ação indisponível ao assistente. "
    "Nesses casos, não penalize a recusa apenas por não fornecer o dado ou realizar a ação. "
    "IMPORTANTE: Citações de URIs completas (ex: s3://...) ou nomes de arquivos que constem "
    "no contexto recuperado (RETRIEVAL_CONTEXT) são referências legítimas e NÃO devem ser "
    "consideradas informações inventadas ou fabricação de dados. "
    "Penalize desvios, respostas a perguntas antigas ou recusa que não enfrenta o pedido. "
    "Esta é uma medida de pertinência; a exatidão factual é avaliada separadamente."
)

CRITERIO_FUNDAMENTACAO_LOGICA = (
    "Avalie se cada afirmação material é sustentada pelos trechos realmente recuperados. "
    "Permita deduções matemáticas e lógicas elementares, como concluir que 1.915 horas "
    "não satisfazem um mínimo de 1.920 horas. Confira também a relação entre regra e "
    "procedimento: números verdadeiros sobre equivalência de disciplinas não provam "
    "requisitos de ingresso por transferência. "
    "REGRA CRÍTICA SOBRE FONTES: cada trecho recuperado possui dois identificadores "
    "igualmente válidos: (1) o nome do arquivo RAG, visível na URI recuperada "
    "(por exemplo `ementa_cco33.md`), e (2) a 'Fonte canônica' declarada dentro do "
    "próprio texto do trecho (por exemplo `08_ementas.md`). Ambos se referem ao mesmo "
    "documento. Não penalize a resposta por citar qualquer um deles. "
    "Penalize apenas contradições factuais diretas, fatos sem nenhum suporte nos trechos "
    "e aplicação de uma regra a um processo que a fonte não descreve."
)

PASSOS_CONFORMIDADE_UPC = [
    "Identifique exatamente a pergunta atual e se ela pede um fato, um cálculo, uma decisão administrativa ou uma ação que o assistente não pode executar. Use o histórico apenas para resolver referências.",
    "Leia Expected Output como resposta de referência do Golden Dataset para identificar a regra ou distinção esperada. Não a trate como documento recuperado. REGRA ABSOLUTA: Você está ESTRITAMENTE PROIBIDO de penalizar a ausência de uma fonte (ex: ementa_mat10.md) só porque ela aparece no Expected Output, se essa fonte NÃO constar explicitamente na lista de trechos do Retrieval Context. Apenas avalie se a informação factual está correta baseada no Retrieval Context disponível.",
    "Compare cada afirmação material da resposta com os trechos recuperados. Verifique números e relações aritméticas explicitamente; por exemplo, 1.915 é menor que 1.920. Não substitua o texto recuperado por uma regra presumida da universidade.",
    "Separe os procedimentos da pergunta dos procedimentos encontrados nas fontes e compare essa distinção com Expected Output. Um trecho intitulado 'Aproveitamento de estudos' descreve equivalência de disciplinas já cursadas; números como 75% de correspondência e limite de 50% do curso só sustentam essa equivalência. Eles não demonstram que transferência externa, um processo de ingresso, exige equivalência. Se a referência aponta edital, vagas e classificação para transferência, não aceite a inferência de que equivalência é o único mecanismo relevante. Confira também as justificativas introduzidas por 'pois', 'exige' ou 'além disso': uma recusa correta com motivo administrativo não sustentado continua materialmente incorreta.",
    "Confira período letivo, tipo de pedido e condição administrativa. Não extrapole uma data de 2027 para 2028 nem garanta deferimento ou vaga quando houver análise ou disponibilidade. Uma recusa fundamentada de inventar data ou executar matrícula é adequada; aprovação por nota e frequência, quando definida nos trechos, pode ser afirmada diretamente.",
    "Verifique a procedência das citações. Cada trecho recuperado possui dois identificadores igualmente válidos: o nome do arquivo RAG visível na URI recuperada (por exemplo `ementa_cco33.md` ou `avaliacao_frequencia.md`) e a 'Fonte canônica' declarada dentro do próprio texto do trecho (por exemplo `08_ementas.md` ou `04_regras_academicas.md`). Ambos identificam o mesmo documento. Aceite qualquer um deles como citação válida. REGRA ABSOLUTA: Não deduza pontos nem considere 'imprecisão' o uso da fonte canônica em vez do nome RAG. Penalize apenas nomes, links ou documentos completamente inventados que não correspondam a nenhum item recuperado.",
    "Para pedido fora do escopo ou instrução para ignorar a base, valorize a recusa ou a resposta limitada aos fatos sustentados. Dê nota alta apenas se a resposta enfrentar a pergunta sem erro material de fato, aplicação da regra, período ou fonte.",
]

FAIXAS_CONFORMIDADE_UPC = [
    Rubric(score_range=(0, 4), expected_outcome="Há erro material de fato, cálculo, procedimento, período ou fonte inventada; ou a resposta garante decisão sem respaldo. Inclui apresentar condições de um procedimento (como aproveitamento de disciplinas) como exigências de outro (como ingresso por transferência). Acertar 'não há garantia' não compensa uma justificativa administrativa falsa ou não sustentada."),
    Rubric(score_range=(5, 7), expected_outcome="A conclusão principal é segura, mas falta informação relevante, há imprecisão menor ou a fonte é identificada de modo incompleto, sem erro material que mude a orientação."),
    Rubric(score_range=(8, 10), expected_outcome="A resposta atende à pergunta, aplica a regra ao mesmo procedimento que a fonte descreve, preserva números e períodos e sustenta todas as afirmações materiais, inclusive as justificativas, nos trechos e fontes recuperados; uma abstenção justificada também pode receber esta faixa."),
]

def build_scope_metric(agent_model_id: str, async_mode: bool = False):
    """Conformidade para casos sem trechos recuperados, sem contexto artificial."""
    return GEval(
        name="Conformidade UPC sem contexto",
        criteria=(
            "Avalie se a resposta respeita o escopo do assistente acadêmico da UPC. "
            "Sem documentos recuperados, deve pedir esclarecimento quando falta referente, "
            "recusar pedidos fora do escopo ou abster-se de afirmar fatos sobre a UPC. "
            "Não invente fonte, data, regra ou ação administrativa."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        threshold=0.80,
        model=get_judge_model(agent_model_id),
        async_mode=async_mode,
    )


def build_metrics(agent_model_id: str, async_mode: bool = False) -> Dict[str, object]:
    """Retorna as três métricas exigidas e a relevância contextual opcional."""
    judge = get_judge_model(agent_model_id)

    return {
        "answer_relevancy": AnswerRelevancyMetric(
            threshold=0.70,
            model=judge,
            async_mode=async_mode,
        ),
        "faithfulness": FaithfulnessMetric(
            threshold=0.80,
            model=judge,
            async_mode=async_mode,
        ),
        "geval_conformidade": GEval(
            name="Conformidade Regras UPC",
            evaluation_steps=PASSOS_CONFORMIDADE_UPC,
            rubric=FAIXAS_CONFORMIDADE_UPC,
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.EXPECTED_OUTPUT,
                SingleTurnParams.RETRIEVAL_CONTEXT,
            ],
            threshold=0.80,
            model=judge,
            async_mode=async_mode,
        ),
        "contextual_relevancy": ContextualRelevancyMetric(
            threshold=0.70,
            model=judge,
            async_mode=async_mode,
        ),
    }


def build_diagnostic_metrics(agent_model_id: str, async_mode: bool = False) -> Dict[str, object]:
    """G-Evals opcionais; não substituem as métricas nativas exigidas."""
    judge = get_judge_model(agent_model_id)
    return {
        "Relevância de domínio (diagnóstico)": GEval(
            name="Relevância de domínio",
            criteria=CRITERIO_RELEVANCIA_DOMINIO,
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            threshold=0.70,
            model=judge,
            async_mode=async_mode,
        ),
        "Fundamentação lógica (diagnóstico)": GEval(
            name="Fundamentação lógica",
            criteria=CRITERIO_FUNDAMENTACAO_LOGICA,
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.RETRIEVAL_CONTEXT,
            ],
            threshold=0.80,
            model=judge,
            async_mode=async_mode,
        ),
    }
