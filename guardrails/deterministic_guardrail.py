import re

from guardrails.rules_loader import RulesLoader


class DeterministicGuardrail:
    """Rule-based input validation.
    No LLM is used here.
    """

    def __init__(self):
        self.rules = RulesLoader().get_rules()

    def validate(self, user_input: str) -> dict:

        # Empty input
        result = self.check_empty(user_input)
        if result:
            return result

        # Maximum length
        result = self.check_length(user_input)
        if result:
            return result

        # Malicious keywords
        result = self.check_keywords(user_input)
        if result:
            return result

        # SQL Injection
        result = self.check_sql(user_input)
        if result:
            return result

        # XSS
        result = self.check_xss(user_input)
        if result:
            return result

        # Prompt Injection
        result = self.check_prompt_injection(user_input)
        if result:
            return result

        # Unsupported characters
        result = self.check_invalid_characters(user_input)
        if result:
            return result

        return {
            "passed": True,
            "status": "PASSED",
            "reason": None
        }

    def mask_sensitive_data(self, text: str) -> str:
        """
        Mask sensitive information before sending it
        to the chatbot or LLM.

        Credit cards are masked by showing only the
        last 4 digits.
        """

        patterns = self.rules.get("masking_patterns", {})

        replacements = {
            "cvv": "[MASKED_CVV]",
            "expiry_date": "[MASKED_EXPIRY]",
            "aadhaar": "[MASKED_AADHAAR]",
            "pan": "[MASKED_PAN]",
            "phone": "[MASKED_PHONE]",
            "email": "[MASKED_EMAIL]"
        }

        for key, pattern in patterns.items():

            # Credit Card → XXXXXXXXXXXX1234
            if key == "credit_card":

                def mask_card(match):
                    card = match.group()

                    # Keep only digits
                    digits = re.sub(r"\D", "", card)

                    # Ignore invalid card lengths
                    if len(digits) < 13:
                        return card

                    # Mask all except last 4 digits
                    return "X" * (len(digits) - 4) + digits[-4:]

                text = re.sub(pattern, mask_card, text)

            else:
                text = re.sub(
                    pattern,
                    replacements.get(key, "[MASKED]"),
                    text,
                    flags=re.IGNORECASE
                )

        return text

    def block(self, reason):
        return {
            "passed": False,
            "status": "BLOCKED",
            "reason": reason
        }

    def check_empty(self, text):

        if text is None:
            return self.block("Empty input")

        if text.strip() == "":
            return self.block("Empty input")

        return None

    def check_length(self, text):

        max_len = self.rules["max_input_length"]

        if len(text) > max_len:
            return self.block(
                f"Input exceeds maximum length ({max_len})"
            )

        return None

    def check_keywords(self, text):

        text = text.lower()

        for word in self.rules["blocked_keywords"]:

            if word.lower() in text:
                return self.block(
                    f"Blocked keyword detected: {word}"
                )

        return None

    def check_sql(self, text):

        text = text.lower()

        for pattern in self.rules["sql_patterns"]:

            if pattern.lower() in text:
                return self.block(
                    "SQL Injection Detected"
                )

        return None

    def check_xss(self, text):

        text = text.lower()

        for pattern in self.rules["xss_patterns"]:

            if pattern.lower() in text:
                return self.block(
                    "XSS Detected"
                )

        return None

    def check_prompt_injection(self, text):

        text = text.lower()

        for pattern in self.rules["prompt_injection_patterns"]:

            if pattern.lower() in text:
                return self.block(
                    "Prompt Injection Detected"
                )

        return None

    def check_invalid_characters(self, text):

        allowed = re.fullmatch(
            r"[A-Za-z0-9\s.,?!@#$%^&*()_\-+=:;'\"/\\[\]{}<>|`~]*",
            text
        )

        if not allowed:
            return self.block(
                "Unsupported characters detected"
            )

        return None