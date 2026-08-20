import json

from config import GUARDRAIL_RULES_FILE


class RulesLoader:

    def __init__(self):
        self.rules = self.load()

    def load(self):
        with open(GUARDRAIL_RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_rules(self):
        return self.rules