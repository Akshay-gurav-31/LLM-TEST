import time
from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    response: str
    latency: float


def llm_test(model, model_name="LLM"):
    tests = {
        "Reasoning": """
A farmer has 17 sheep. All but 9 die.
How many sheep are left?
Answer with the number and a one-line explanation.
""",

        "Coding": """
Write a Python function that returns the first non-repeating
character in a string. Include time complexity.
""",

        "Concept": """
Explain recursion in exactly one sentence.
""",

        "Logic": """
If all roses are flowers and some flowers fade quickly,
can we conclude that some roses fade quickly?
Answer Yes or No and explain briefly.
""",

        "Structured": """
Return JSON only:
{
  "language": "Python",
  "type": "programming",
  "difficulty": "easy"
}
"""
    }

    results = []

    for test_name, prompt in tests.items():
        start = time.perf_counter()

        try:
            response = model.generate(prompt)
            latency = time.perf_counter() - start

            results.append(
                TestResult(
                    name=test_name,
                    response=str(response),
                    latency=latency
                )
            )

        except Exception as e:
            results.append(
                TestResult(
                    name=test_name,
                    response=f"ERROR: {e}",
                    latency=0
                )
            )

    print(f"\n{'=' * 60}")
    print(f"MODEL: {model_name}")
    print(f"{'=' * 60}")

    for result in results:
        print(f"\n[{result.name}]")
        print(f"Latency: {result.latency:.2f}s")
        print(result.response)

    avg_latency = (
        sum(r.latency for r in results) / len(results)
    )

    print(f"\nAverage latency: {avg_latency:.2f}s")

    return results


# Example
llm_test(model, "DeepSeek R1")
