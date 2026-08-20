"""
evaluation/metrics.py
----------------------
Builds the list of DeepEval metrics used to score a chatbot response,
all pointed at the same Amplify judge. Centralizing this means adding or
removing a metric is a one-line change here rather than a change scattered
across route handlers or CLI scripts.
"""

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ToxicityMetric,
    BiasMetric,
)
from deepeval.models.base_model import DeepEvalBaseLLM

from config import DEFAULT_METRIC_THRESHOLD

# Registry of metric name -> class, so callers (routes, CLI, tests) can
# request a subset by name instead of always running everything.
METRIC_REGISTRY = {
    "answer_relevancy": AnswerRelevancyMetric,
    "faithfulness": FaithfulnessMetric,
    "hallucination": HallucinationMetric,
    "toxicity": ToxicityMetric,
    "bias": BiasMetric,
}

DEFAULT_METRIC_NAMES = list(METRIC_REGISTRY.keys())


def build_metrics(
    judge: DeepEvalBaseLLM,
    metric_names: list[str] = None,
    threshold: float = DEFAULT_METRIC_THRESHOLD,
) -> list:
    """Instantiate the requested metrics (default: all of them) against the
    given judge model."""
    names = metric_names or DEFAULT_METRIC_NAMES

    metrics = []
    for name in names:
        metric_cls = METRIC_REGISTRY.get(name)
        if metric_cls is None:
            raise ValueError(f"Unknown metric: {name}")
        metrics.append(metric_cls(threshold=threshold, model=judge))

    return metrics
