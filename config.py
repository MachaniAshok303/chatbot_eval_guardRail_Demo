"""
config.py
---------
Single source of truth for paths, environment variables, and tunable
settings. Nothing in this project should hardcode a file path or an
Amplify credential outside of this module.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# JSON data files (source of truth for chatbot answers and eval inputs)
CHATBOT_RESPONSES_FILE = os.path.join(DATA_DIR, "chatbot_responses.json")
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")

# Amplify LLM Judge configuration
AMPLIFY_API_URL = os.getenv(
    "AMPLIFY_API_URL",
    "https://amplify.planittesting.com/external/api/completion",
)
AMPLIFY_TOKEN = os.getenv("AMPLIFY_TOKEN")

# Evaluation defaults
DEFAULT_METRIC_THRESHOLD = float(os.getenv("DEFAULT_METRIC_THRESHOLD", "0.7"))

# Metrics that "pass" when the score is LOW (inverse metrics)
LOWER_IS_BETTER_METRICS = {"HallucinationMetric", "ToxicityMetric", "BiasMetric"}

# Fuzzy-matching cutoff used when the chatbot looks up a JSON response
# for a user question that doesn't match a stored question exactly.
RESPONSE_MATCH_CUTOFF = float(os.getenv("RESPONSE_MATCH_CUTOFF", "0.6"))

os.makedirs(RESULTS_DIR, exist_ok=True)

GUARDRAIL_RULES_FILE = "data/guardrail_rules.json"
