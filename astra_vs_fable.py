"""
Astra vs Fable LLM Benchmark
-----------------------------
Give the SAME task to Astra and Fable, score both answers, and declare
a winner based on the total score.

Set the API keys/endpoints below according to your providers.

Install:
    pip install openai

Run:
    python astra_vs_fable.py
"""

import os
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

# If both providers use OpenAI-compatible APIs, set these values.
ASTRA_API_KEY = os.getenv("ASTRA_API_KEY", "YOUR_ASTRA_API_KEY")
ASTRA_BASE_URL = os.getenv("ASTRA_BASE_URL", "YOUR_ASTRA_BASE_URL")
ASTRA_MODEL = os.getenv("ASTRA_MODEL", "YOUR_ASTRA_MODEL")

FABLE_API_KEY = os.getenv("FABLE_API_KEY", "YOUR_FABLE_API_KEY")
FABLE_BASE_URL = os.getenv("FABLE_BASE_URL", "YOUR_FABLE_BASE_URL")
FABLE_MODEL = os.getenv("FABLE_MODEL", "YOUR_FABLE_MODEL")

# =========================
# COMMON BENCHMARK TASK
# =========================

TASK = """
You are given a messy product requirement from a startup founder:

"We need a small SaaS dashboard for founders. Users upload a CSV containing
sales data. The app should automatically clean obvious data issues, calculate
monthly revenue, identify the top 5 products, detect unusual sales drops,
and generate a short natural-language summary. The dashboard should be fast,
simple, and easy for a non-technical founder to understand.

Explain:
1. How you would design the system.
2. Which parts should use deterministic code and which parts could use an LLM.
3. A practical backend/API architecture.
4. How you would handle bad CSV data.
5. Three important security/privacy considerations.
6. A simple testing strategy.

Keep the answer practical and concise. Do not invent requirements.
"""

SYSTEM_PROMPT = """
You are participating in a controlled LLM benchmark.
Answer the user's task directly.
Do not mention this benchmark, scoring, Astra, or Fable.
Prioritize correctness, practical engineering judgment, clarity,
security, and avoiding unsupported assumptions.
"""

# =========================
# SCORING RUBRIC
# =========================

RUBRIC = {
    "technical_correctness": 25,
    "practicality": 20,
    "requirements_coverage": 20,
    "security_and_privacy": 15,
    "clarity": 10,
    "handling_of_edge_cases": 10,
}

JUDGE_PROMPT = """
You are a strict, neutral evaluator.

Compare two answers to the SAME engineering task.

Score each answer from 0 up to the maximum points for every criterion.
Do not give points merely for length. Reward concrete, correct, useful content.

Criteria:
- Technical correctness: 25
- Practicality: 20
- Requirements coverage: 20
- Security and privacy: 15
- Clarity: 10
- Handling of edge cases: 10

Return ONLY valid JSON in this exact structure:
{
  "astra": {
    "technical_correctness": 0,
    "practicality": 0,
    "requirements_coverage": 0,
    "security_and_privacy": 0,
    "clarity": 0,
    "handling_of_edge_cases": 0,
    "total": 0,
    "reason": "short reason"
  },
  "fable": {
    "technical_correctness": 0,
    "practicality": 0,
    "requirements_coverage": 0,
    "security_and_privacy": 0,
    "clarity": 0,
    "handling_of_edge_cases": 0,
    "total": 0,
    "reason": "short reason"
  },
  "winner": "Astra or Fable or Tie",
  "summary": "short neutral comparison"
}

Do not use criteria outside the rubric.
"""

def ask_model(name, api_key, base_url, model):
    if "YOUR_" in api_key or "YOUR_" in base_url or "YOUR_" in model:
        raise ValueError(
            f"{name} configuration is incomplete. Set its API key, base URL, and model."
        )

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": TASK},
        ],
    )

    return response.choices[0].message.content.strip()


def judge_answers(astra_answer, fable_answer):
    # Use Fable as the judge only if you explicitly want a model judge.
    # For a stronger benchmark, replace this with a separate independent
    # judge model/provider.
    if "YOUR_" in FABLE_API_KEY or "YOUR_" in FABLE_BASE_URL or "YOUR_" in FABLE_MODEL:
        raise ValueError("Fable configuration is incomplete.")

    judge_client = OpenAI(api_key=FABLE_API_KEY, base_url=FABLE_BASE_URL)

    prompt = (
        JUDGE_PROMPT
        + "\n\nTASK:\n"
        + TASK
        + "\n\nASTRA ANSWER:\n"
        + astra_answer
        + "\n\nFABLE ANSWER:\n"
        + fable_answer
    )

    response = judge_client.chat.completions.create(
        model=FABLE_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a neutral benchmark judge."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


def main():
    print("=" * 70)
    print("ASTRA vs FABLE LLM BENCHMARK")
    print("=" * 70)

    print("\nRunning Astra...")
    astra_answer = ask_model(
        "Astra", ASTRA_API_KEY, ASTRA_BASE_URL, ASTRA_MODEL
    )

    print("Running Fable...")
    fable_answer = ask_model(
        "Fable", FABLE_API_KEY, FABLE_BASE_URL, FABLE_MODEL
    )

    print("\n" + "=" * 70)
    print("ASTRA ANSWER")
    print("=" * 70)
    print(astra_answer)

    print("\n" + "=" * 70)
    print("FABLE ANSWER")
    print("=" * 70)
    print(fable_answer)

    print("\n" + "=" * 70)
    print("SCORING")
    print("=" * 70)

    result = judge_answers(astra_answer, fable_answer)
    print(result)

    with open("benchmark_results.txt", "w", encoding="utf-8") as f:
        f.write("ASTRA vs FABLE LLM BENCHMARK\n\n")
        f.write("TASK:\n" + TASK + "\n\n")
        f.write("ASTRA ANSWER:\n" + astra_answer + "\n\n")
        f.write("FABLE ANSWER:\n" + fable_answer + "\n\n")
        f.write("SCORING:\n" + result + "\n")

    print("\nSaved results to benchmark_results.txt")


if __name__ == "__main__":
    main()
