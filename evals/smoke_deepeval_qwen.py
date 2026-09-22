"""Teste mínimo de integração DeepEval + Qwen3 Next via Bedrock em Ohio."""

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.models import AmazonBedrockModel
from deepeval.test_case import LLMTestCase


judge = AmazonBedrockModel(
    model="qwen.qwen3-next-80b-a3b",
    region="us-east-2",
    generation_kwargs={"temperature": 0, "maxTokens": 1024},
)

case = LLMTestCase(
    input="Qual é o prazo para solicitar trancamento em 2027.1?",
    actual_output=(
        "O prazo para solicitar trancamento total em 2027.1 é "
        "27/04/2027. Fonte: calendario_2027_1.md."
    ),
    retrieval_context=[
        "Calendário acadêmico 2027.1 da UPC: o prazo para solicitar "
        "cancelamento de disciplina ou trancamento total é 27/04/2027 "
        "(50º dia letivo). Fonte: calendario_2027_1.md."
    ],
)

metrics = [
    FaithfulnessMetric(threshold=0.85, model=judge, async_mode=False),
    AnswerRelevancyMetric(threshold=0.80, model=judge, async_mode=False),
    ContextualRelevancyMetric(threshold=0.70, model=judge, async_mode=False),
]

for metric in metrics:
    print(f"Iniciando {metric.__class__.__name__}...", flush=True)
    try:
        metric.measure(case)
    except Exception as exc:
        print(f"ERRO em {metric.__class__.__name__}: {type(exc).__name__}: {exc}")
        continue
    print(
        f"{metric.__class__.__name__}: score={metric.score}, "
        f"passou={metric.score is not None and metric.score >= metric.threshold}, "
        f"motivo={metric.reason}",
        flush=True,
    )
