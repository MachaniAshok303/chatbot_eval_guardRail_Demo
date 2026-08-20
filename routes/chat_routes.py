"""
routes/chat_routes.py
-----------------------
User
    │
    ▼
Deterministic Guardrail
    │
    ├── BLOCKED
    │       ▼
    │   Return blocked response
    │
    ▼
Sensitive Action Detector
    │
    ├── Sensitive Request
    │       ▼
    │   WAITING_FOR_CONFIRMATION
    │
    ▼
JSON Knowledge Base
    │
    ▼
Amplify Judge
    │
    ▼
DeepEval Metrics
"""

from uuid import uuid4
import time

from flask import Blueprint, jsonify, render_template, request
from deepeval.test_case import LLMTestCase

from chatbot.response_provider import ChatbotResponseProvider
from evaluation.amplify_judge import AmplifyJudgeLLM
from evaluation.evaluator import evaluate_test_case
from evaluation.metrics import build_metrics
from evaluation.html_report import generate_html_report

from guardrails.approval_manager import HumanApprovalManager
from guardrails.deterministic_guardrail import DeterministicGuardrail
from guardrails.sensitive_detector import SensitiveActionDetector


chat_bp = Blueprint("chat", __name__)

# ----------------------------------------------------
# Shared Components
# ----------------------------------------------------

response_provider = ChatbotResponseProvider()
judge = AmplifyJudgeLLM()
guardrail = DeterministicGuardrail()
sensitive_detector = SensitiveActionDetector()
approval_manager = HumanApprovalManager()


@chat_bp.route("/")
def index():
    return render_template("index.html")


@chat_bp.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "").strip()

    # ----------------------------------------------------
    # Step 1 : Deterministic Guardrail
    # ----------------------------------------------------

    guardrail_result = guardrail.validate(user_message)

    if not guardrail_result["passed"]:
        return jsonify({
            "guardrail_status": guardrail_result["status"],
            "blocked_reason": guardrail_result["reason"],
            "reply": (
                "Your request has been blocked because it "
                "violates the application's safety policy."
            )
        })

    masked_message = guardrail.mask_sensitive_data(user_message)

    if masked_message != user_message:
        return jsonify({
            "guardrail_status": "MASKED",
            "blocked_reason": "Sensitive data detected and masked.",
            "reply": (
                "I can't store or expose sensitive information.\n\n"
                f"Your input has been masked:\n\n{masked_message}\n\n"
                "Please remove sensitive information and try again."
            )
        })

    # ----------------------------------------------------
    # Step 2 : Sensitive Action Detection
    # ----------------------------------------------------

    if sensitive_detector.requires_approval(user_message):

        request_id = str(uuid4())

        approval_manager.start(request_id, user_message)

        return jsonify({
            "guardrail_status": "WAITING_FOR_CONFIRMATION",
            "blocked_reason": None,
            "request_id": request_id,
            "requires_confirmation": True,
            "reply": (
                "This request involves a sensitive operation.\n\n"
                "Do you want to continue?"
            )
        })

    # ----------------------------------------------------
    # Step 3 : JSON Knowledge Base
    # ----------------------------------------------------

    entry = response_provider.find_entry(user_message)

    if entry is None:
        return jsonify({
            "guardrail_status": None,
            "blocked_reason": None,
            "reply": (
                "I don't have an answer for that "
                "in my knowledge base yet."
            )
        })

    # ----------------------------------------------------
    # Step 4 : Build Test Case
    # ----------------------------------------------------

    reply = entry["response"]

    test_case = LLMTestCase(
        input=user_message,
        actual_output=reply,
        context=entry.get("context") or None,
        retrieval_context=entry.get("retrieval_context") or None,
    )

    # ----------------------------------------------------
    # Step 5 : Evaluation
    # ----------------------------------------------------

    metrics = build_metrics(judge)

    start = time.perf_counter()

    evaluation = evaluate_test_case(test_case, metrics)

    evaluation_time = round((time.perf_counter() - start) * 1000, 2)

    # Generate HTML report
    generate_html_report(
        question=user_message,
        response=reply,
        evaluation=evaluation,
        evaluation_time=evaluation_time
    )

    # ----------------------------------------------------
    # Step 6 : Return ONLY chatbot response
    # ----------------------------------------------------

    return jsonify({
        "guardrail_status": "PASSED",
        "blocked_reason": None,
        "reply": reply
    })


@chat_bp.route("/chat/confirm", methods=["POST"])
def confirm_request():

    data = request.get_json(silent=True) or {}

    request_id = data.get("request_id")
    approved = data.get("approved")

    if not request_id:
        return jsonify({
            "error": "request_id is required"
        }), 400

    if approved is None:
        return jsonify({
            "error": "approved is required"
        }), 400

    if not approved:

        approval_manager.reject(request_id)

        return jsonify({
            "guardrail_status": "CANCELLED_BY_USER",
            "blocked_reason": "User declined sensitive operation.",
            "reply": "The requested operation has been cancelled."
        })

    approval_manager.approve(request_id)

    user_message = approval_manager.get_message(request_id)

    if not user_message:
        return jsonify({
            "error": "Request not found"
        }), 404

    entry = response_provider.find_entry(user_message)

    if entry is None:
        return jsonify({
            "guardrail_status": None,
            "blocked_reason": None,
            "reply": (
                "I don't have an answer for that "
                "in my knowledge base yet."
            )
        })

    reply = entry["response"]

    test_case = LLMTestCase(
        input=user_message,
        actual_output=reply,
        context=entry.get("context") or None,
        retrieval_context=entry.get("retrieval_context") or None,
    )

    metrics = build_metrics(judge)

    start = time.perf_counter()

    evaluation = evaluate_test_case(test_case, metrics)

    evaluation_time = round((time.perf_counter() - start) * 1000, 2)

    generate_html_report(
        question=user_message,
        response=reply,
        evaluation=evaluation,
        evaluation_time=evaluation_time
    )

    return jsonify({
        "guardrail_status": "PASSED",
        "blocked_reason": None,
        "reply": reply
    })