"""
evaluation/amplify_judge.py
----------------------------
Planit Amplify wrapped as a DeepEval-compatible LLM judge.

IMPORTANT: this class is used ONLY to score/evaluate chatbot responses.
It must never be used to generate the chatbot's answers - that responsibility
belongs to chatbot/response_provider.py, which reads from JSON files.
Keeping these two responsibilities in separate modules is what prevents the
"model judging its own output" problem from creeping back in.
"""

import json
import requests

from deepeval.models.base_model import DeepEvalBaseLLM

from config import AMPLIFY_API_URL, AMPLIFY_TOKEN


class AmplifyJudgeLLM(DeepEvalBaseLLM):
    """Thin adapter so DeepEval metrics can call Amplify as their judge."""

    def __init__(self, api_url: str = AMPLIFY_API_URL, token: str = AMPLIFY_TOKEN):
        self.url = api_url
        self.token = token

    def load_model(self):
        return "Amplify"

    def generate(self, prompt: str, *args, **kwargs) -> str:
        """Sends a DeepEval evaluation prompt to Amplify and returns the
        judge's response text."""
        if not self.token:
            raise ValueError("AMPLIFY_TOKEN environment variable is missing")

        headers = {
            "accept": "*/*",
            "Content-Type": "application/json",
            "token": self.token,
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "parameters": {"temperature": 0},
        }

        try:
            response = requests.post(
                self.url, headers=headers, json=payload, timeout=120
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                if "assistant_resp" in data:
                    return data["assistant_resp"]
                if "response" in data:
                    return data["response"]
                if "content" in data:
                    return data["content"]

            return json.dumps(data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Amplify API request failed: {e}")

    async def a_generate(self, prompt: str, *args, **kwargs) -> str:
        return self.generate(prompt, *args, **kwargs)

    def get_model_name(self) -> str:
        return "Amplify"
