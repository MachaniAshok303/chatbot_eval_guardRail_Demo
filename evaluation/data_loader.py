"""
evaluation/data_loader.py
--------------------------
Turns data/test_cases.json into a list of deepeval LLMTestCase objects.

Nothing here is hardcoded: each test case only needs an "input". The
actual_output/context/retrieval_context are pulled from the chatbot's own
JSON response bank (chatbot/response_provider.py) so evaluation always runs
against the exact same answer the chatbot UI would show a user. A test case
may still supply its own "actual_output" (and optionally "context" /
"retrieval_context") directly in JSON to evaluate a hypothetical/incorrect
answer without touching the chatbot's response bank - see tc_004 in
data/test_cases.json for an example.
"""

import json
from typing import List

from deepeval.test_case import LLMTestCase

from config import TEST_CASES_FILE
from chatbot.response_provider import ChatbotResponseProvider


def load_raw_test_cases(json_path: str = TEST_CASES_FILE) -> list:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"{json_path} must contain a JSON array of test cases")

    return data


def build_test_case(
    raw: dict, response_provider: ChatbotResponseProvider
) -> LLMTestCase:
    user_input = raw["input"]

    if "actual_output" in raw:
        actual_output = raw["actual_output"]
        context = raw.get("context", [])
        retrieval_context = raw.get("retrieval_context", [])
    else:
        entry = response_provider.get_response(user_input)
        actual_output = entry["response"]
        context = entry.get("context", [])
        retrieval_context = entry.get("retrieval_context", [])

    return LLMTestCase(
        input=user_input,
        actual_output=actual_output,
        context=context or None,
        retrieval_context=retrieval_context or None,
        expected_output=raw.get("expected_output"),
    )


def load_test_cases(
    json_path: str = TEST_CASES_FILE,
    response_provider: ChatbotResponseProvider = None,
) -> List[LLMTestCase]:
    """Reads every test case in json_path and iterates through all of them,
    returning ready-to-evaluate LLMTestCase objects."""
    provider = response_provider or ChatbotResponseProvider()
    raw_cases = load_raw_test_cases(json_path)
    return [build_test_case(raw, provider) for raw in raw_cases]
