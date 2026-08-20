"""
run_batch_evaluation.py
-------------------------
CLI replacement for the old workingCode.py. Everything that used to be a
hardcoded `input=` / `actual_output=` in that script now comes from
data/test_cases.json (and, for the chatbot's own answers, from
data/chatbot_responses.json). Run:

    python run_batch_evaluation.py
"""

from chatbot.response_provider import ChatbotResponseProvider
from evaluation.amplify_judge import AmplifyJudgeLLM
from evaluation.metrics import build_metrics
from evaluation.data_loader import load_test_cases
from evaluation.evaluator import evaluate_test_case

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_result(result: dict) -> None:
    print("\n" + "=" * 70)
    print(f"{BOLD}{BLUE}Test case:{RESET} {result['input']}")
    print(f"{BOLD}{BLUE}Actual output:{RESET} {result['actual_output']}")
    print("=" * 70)

    for m in result["metrics"]:
        print(f"\n{BOLD}📊 {m['metric']}{RESET}")
        if m["error"]:
            print(f"{RED}❌ ERROR: {m['error']}{RESET}")
            continue

        print(f"{CYAN}Score :{RESET} {m['score']:.2f} (threshold {m['threshold']})")
        status = f"{GREEN}✅ PASSED{RESET}" if m["passed"] else f"{RED}❌ FAILED{RESET}"
        print(f"Status : {status}")
        print(f"{YELLOW}Reason:{RESET} {m['reason']}")

    overall = f"{GREEN}PASSED{RESET}" if result["overall_passed"] else f"{RED}FAILED{RESET}"
    print(f"\n{BOLD}Overall: {overall}{RESET}")


def main() -> None:
    judge = AmplifyJudgeLLM()
    response_provider = ChatbotResponseProvider()

    test_cases = load_test_cases(response_provider=response_provider)
    metrics_factory = lambda: build_metrics(judge)  # noqa: E731 - fresh metric instances per test case

    print(f"Loaded {len(test_cases)} test case(s) from data/test_cases.json\n")

    all_passed = 0
    for test_case in test_cases:
        result = evaluate_test_case(test_case, metrics_factory())
        print_result(result)
        all_passed += int(result["overall_passed"])

    print("\n" + "=" * 70)
    print(f"{BOLD}Summary: {all_passed}/{len(test_cases)} test cases passed{RESET}")
    print("=" * 70)


if __name__ == "__main__":
    main()
