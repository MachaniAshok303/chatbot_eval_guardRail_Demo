"""
evaluation/evaluator.py
------------------------
Runs a set of DeepEval metrics against one or many LLMTestCase objects and
returns plain dicts/lists (JSON-serializable), so this module is equally
usable from a Flask route, a CLI script, or a unit test.
"""

from deepeval.test_case import LLMTestCase

from config import LOWER_IS_BETTER_METRICS


def is_metric_passed(metric) -> bool:
    """Some DeepEval metrics (Hallucination, Toxicity, Bias) pass when the
    score is LOW rather than high."""
    metric_name = metric.__class__.__name__
    if metric_name in LOWER_IS_BETTER_METRICS:
        return metric.score <= metric.threshold
    return metric.score >= metric.threshold


def evaluate_test_case(test_case: LLMTestCase, metrics: list) -> dict:
    """Runs every metric against a single test case."""
    metric_results = []

    for metric in metrics:
        try:
            metric.measure(test_case)
            metric_results.append(
                {
                    "metric": metric.__class__.__name__,
                    "score": metric.score,
                    "threshold": metric.threshold,
                    "passed": is_metric_passed(metric),
                    "reason": metric.reason,
                    "error": None,
                }
            )
        except Exception as error:  # noqa: BLE001 - surfaced in the result, not swallowed
            metric_results.append(
                {
                    "metric": metric.__class__.__name__,
                    "score": None,
                    "threshold": metric.threshold,
                    "passed": False,
                    "reason": None,
                    "error": str(error),
                }
            )

    return {
        "input": test_case.input,
        "actual_output": test_case.actual_output,
        "metrics": metric_results,
        "overall_passed": all(m["passed"] for m in metric_results),
    }


def evaluate_all(test_cases: list, metrics: list) -> list:
    """Iterates through every test case and evaluates each automatically."""
    return [evaluate_test_case(tc, metrics) for tc in test_cases]
