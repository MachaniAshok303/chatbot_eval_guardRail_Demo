from guardrails.rules_loader import RulesLoader


class SensitiveActionDetector:

    def __init__(self):

        self.rules = RulesLoader().get_rules()

        self.sensitive_actions = self.rules["approval_required"]

    def requires_approval(self, user_input):

        text = user_input.lower()

        for action in self.sensitive_actions:

            if action.lower() in text:

                return True

        return False

    def category(self, user_input):

        text = user_input.lower()

        for action in self.sensitive_actions:

            if action.lower() in text:

                return action

        return None