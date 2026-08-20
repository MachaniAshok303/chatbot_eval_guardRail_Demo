# AI Chatbot Evaluation Framework

A single Flask project that merges the two previous prototypes:

1. The **AmplifyLLM judge** (formerly `AmplifyJudgeLLM` in a standalone script
   with hardcoded `input=` / `actual_output=` values).
2. The **mock chatbot UI** (formerly a Flask app that used Amplify to both
   *generate and judge* its own answers).

## Architecture

```
chatbot_eval_project/
├── app.py                     # Flask app factory / entry point
├── config.py                  # All paths & env vars in one place
├── run_batch_evaluation.py    # CLI: evaluate every test case in data/test_cases.json
├── requirements.txt
├── .env.example
│
├── data/
│   ├── chatbot_responses.json # Q&A bank the chatbot serves answers from
│   └── test_cases.json        # Evaluation inputs (no hardcoded outputs needed)
│
├── chatbot/
│   └── response_provider.py   # Looks up/matches a user question -> JSON answer
│
├── evaluation/
│   ├── amplify_judge.py       # Amplify wrapped as a DeepEval judge (JUDGE ONLY)
│   ├── metrics.py             # Builds the DeepEval metric set
│   ├── data_loader.py         # JSON -> LLMTestCase objects
│   └── evaluator.py           # Runs metrics, normalizes results to dicts
│
├── routes/
│   ├── chat_routes.py         # "/" and "/chat" - reply + evaluation
│   └── eval_routes.py         # "/evaluate/batch" - runs all test cases
│
├── templates/index.html
└── static/{style.css, chat.js}
```

## Why this fixes the "model judging itself" problem

Previously: `User -> Flask UI -> Amplify (generate) -> Amplify (judge)`.

Now: `User -> Flask UI -> JSON response bank (generate) -> Amplify (judge only)`.

`chatbot/response_provider.py` never imports or calls `evaluation/amplify_judge.py`,
and vice versa. Amplify is wired in as a `DeepEvalBaseLLM` exclusively inside
`evaluation/`, so there's no code path where it can generate the answer it
later scores.

## Why nothing is hardcoded

- `data/chatbot_responses.json` is the single source of truth for chatbot
  answers (plus the `context`/`retrieval_context` DeepEval needs for
  Faithfulness/Hallucination).
- `data/test_cases.json` only needs an `"input"`. `evaluation/data_loader.py`
  automatically resolves the matching `actual_output`/`context` from the
  chatbot's own response bank - so batch evaluation always scores the exact
  same answer a real user would see in the UI.
- A test case can still override `actual_output` directly in JSON (see
  `tc_004`) to deliberately evaluate a wrong/hallucinated answer without
  touching the chatbot's response bank.
- `evaluation/data_loader.py` iterates through **every** entry in
  `test_cases.json` automatically - adding a new test case means adding a
  JSON object, not editing Python.

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in AMPLIFY_TOKEN

# Web UI (chat + live per-message evaluation)
python app.py
# -> http://127.0.0.1:5000

# Batch evaluation over the terminal
python run_batch_evaluation.py

# Batch evaluation over HTTP
curl http://127.0.0.1:5000/evaluate/batch
```

## Extending it

- **New chatbot answer**: add an object to `data/chatbot_responses.json`.
- **New evaluation test case**: add `{"id": "...", "input": "..."}` to
  `data/test_cases.json` (or include `actual_output` to test a specific
  hypothetical answer).
- **New metric**: add it to `METRIC_REGISTRY` in `evaluation/metrics.py`.
- **New judge model**: implement another `DeepEvalBaseLLM` subclass next to
  `AmplifyJudgeLLM` and pass it into `build_metrics(...)`.
