"""Configuração predefinida dos juízes DeepEval da UPC.

Instalar DeepEval e confirmar acesso ao modelo na conta AWS antes de executar.
As credenciais podem vir da cadeia padrão da AWS (por exemplo, CloudShell).
"""

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.models import AmazonBedrockModel


JUDGE = AmazonBedrockModel(
    model="qwen.qwen3-next-80b-a3b",
    region="us-east-2",
    generation_kwargs={"temperature": 0, "maxTokens": 1024},
)


def build_metrics():
    """Aplicar Faithfulness/Contextual Relevancy só com retrieval_context real."""
    return {
        "faithfulness": FaithfulnessMetric(threshold=0.85, model=JUDGE),
        "answer_relevancy": AnswerRelevancyMetric(threshold=0.80, model=JUDGE),
        "contextual_relevancy": ContextualRelevancyMetric(
            threshold=0.70, model=JUDGE
        ),
    }
