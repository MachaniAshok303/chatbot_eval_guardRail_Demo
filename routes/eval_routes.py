"""
routes/eval_routes.py
-----------------------
Exposes the batch evaluator (data/test_cases.json -> DeepEval metrics via
Amplify) as an HTTP endpoint, in addition to the standalone CLI script
(run_batch_evaluation.py) that does the same thing from the terminal.
"""

from flask import Blueprint, jsonify

from chatbot.response_provider import ChatbotResponseProvider
from evaluation.amplify_judge import AmplifyJudgeLLM
from evaluation.metrics import build_metrics
from evaluation.data_loader import load_test_cases
from evaluation.evaluator import evaluate_all

eval_bp = Blueprint("evaluation", __name__)

judge = AmplifyJudgeLLM()
response_provider = ChatbotResponseProvider()


@eval_bp.route("/evaluate/batch", methods=["GET"])
def run_batch_evaluation():
    test_cases = load_test_cases(response_provider=response_provider)
    metrics = build_metrics(judge)
    results = evaluate_all(test_cases, metrics)

    return jsonify(
        {
            "total": len(results),
            "passed": sum(1 for r in results if r["overall_passed"]),
            "failed": sum(1 for r in results if not r["overall_passed"]),
            "results": results,
        }
    )
