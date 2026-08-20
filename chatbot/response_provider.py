"""
chatbot/response_provider.py
-----------------------------
Replaces the old flow of "ask Amplify to generate a reply". The chatbot's
answers now live entirely in a JSON file (data/chatbot_responses.json).

This keeps chatbot response generation and chatbot response *evaluation*
strictly separate: Amplify is only ever used as the judge (see
evaluation/amplify_judge.py), never as the thing being judged.
"""


import json
import difflib
from typing import Optional, TypedDict

from config import CHATBOT_RESPONSES_FILE, RESPONSE_MATCH_CUTOFF



class ChatbotEntry(TypedDict, total=False):
    question: str
    response: str
    responses: list[str]
    context: list
    retrieval_context: list


class ChatbotResponseProvider:
    """Loads Q&A pairs from JSON and resolves a user message to an answer."""

    def __init__(self, json_path: str = CHATBOT_RESPONSES_FILE):
        self.json_path = json_path
        self._entries: list[ChatbotEntry] = []
        self._by_question: dict[str, ChatbotEntry] = {}
        self._response_index = {}
        self.reload()

    def reload(self) -> None:
        """Re-read the JSON file from disk. Call this if the file changes
        without restarting the Flask app."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(
                f"{self.json_path} must contain a JSON array of Q&A objects"
            )

        self._entries = data
        self._by_question = {
            entry["question"].strip().lower(): entry
            for entry in data
            if "question" in entry and (
            "response" in entry or "responses" in entry
            )
        }

    def find_entry(self, user_message: str) -> Optional[ChatbotEntry]:

        key = user_message.strip().lower()

        if key in self._by_question:
            entry = self._by_question[key]
            return self._select_response(entry)

        close = difflib.get_close_matches(
        key,
        self._by_question.keys(),
        n=1,
        cutoff=RESPONSE_MATCH_CUTOFF
        )

        if close:
            entry = self._by_question[close[0]]
            return self._select_response(entry)

        return None

    def _select_response(self, entry: ChatbotEntry) -> ChatbotEntry:

        if "responses" not in entry:
            return entry

        responses = entry["responses"]

        if not responses:
            return entry

        question = entry["question"].strip().lower()

        index = self._response_index.get(question, 0)

        selected = responses[index]

        self._response_index[question] = (index + 1) % len( responses)

        new_entry = dict(entry)
        new_entry["response"] = selected

        return new_entry

    def get_response(self, user_message: str) -> ChatbotEntry:
        """Always returns a ChatbotEntry. Falls back to a canned
        'no answer on file' entry (no context/retrieval_context) so the
        rest of the pipeline never has to special-case a missing match."""
        entry = self.find_entry(user_message)
        if entry is not None:
            return entry

        return {
            "question": user_message,
            "response": (
                "I don't have an answer for that in my knowledge base yet."
            ),
            "context": [],
            "retrieval_context": [],
        }

    def all_entries(self) -> list[ChatbotEntry]:
        return list(self._entries)
