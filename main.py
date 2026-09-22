import os
from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# ============================================================
# CONFIG
# ============================================================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

JUDGE_MODEL = "gemini-3.8-flash"


# ============================================================
# INPUT
# ============================================================

question = """
Solve this problem:

A train travels 240 km in 3 hours.
It travels the first 120 km at 40 km/h.

What speed must it travel for the remaining 120 km
so that the total journey takes exactly 3 hours?

Explain your reasoning and verify the answer.
"""


astra = """
The first 120 km takes:

120 / 40 = 3 hours.

Since the total journey must take 3 hours, there is
no time remaining for the second 120 km.

Therefore, it is impossible for the train to complete
the journey in exactly 3 hours.
"""


fable = """
The first half takes:

120 / 40 = 3 hours.

The total allowed time is also 3 hours.

Therefore, the remaining 120 km must be completed
in 0 hours, which is impossible.

So there is no finite speed that satisfies the
conditions.
"""


# ============================================================
# EVALUATION SCHEMA
# ============================================================

class ModelScore(BaseModel):
    correctness: int = Field(ge=0, le=30)
    reasoning: int = Field(ge=0, le=25)
    depth: int = Field(ge=0, le=15)
    verification: int = Field(ge=0, le=10)
    robustness: int = Field(ge=0, le=10)
    instruction_following: int = Field(ge=0, le=10)

    strengths: list[str]
    weaknesses: list[str]

    total: int = Field(ge=0, le=100)


class Evaluation(BaseModel):
    astra: ModelScore
    fable: ModelScore

    winner: Literal["Astra", "Fable", "Tie"]
    margin: int = Field(ge=0, le=100)

    confidence: int = Field(ge=0, le=100)

    reason: str


# ============================================================
# JUDGE
# ============================================================

prompt = f"""
You are an independent reasoning benchmark judge.

Compare Astra and Fable on the EXACT same problem.

Do not judge based on:
- writing style
- response length
- model reputation
- personal preference

Judge only the actual quality of the answer.

QUESTION:
{question}

ASTRA:
{astra}

FABLE:
{fable}


SCORING:

Correctness: 30 points
- Is the final answer correct?
- Are calculations logically correct?

Reasoning: 25 points
- Is the reasoning logically valid?
- Are intermediate steps correct?

Depth: 15 points
- Does the response handle the problem completely?
- Does it identify important implications?

Verification: 10 points
- Does it check or validate its conclusion?

Robustness: 10 points
- Does it avoid unsupported assumptions?
- Does it handle edge cases correctly?

Instruction following: 10 points
- Did it actually follow the requested format/task?


IMPORTANT:

1. Calculate the total score yourself.
2. The total must equal the sum of all six categories.
3. Do not reward verbosity.
4. A short answer can receive 100/100 if it is completely correct.
5. Penalize incorrect reasoning even if the final answer is correct.
6. If both models are genuinely equivalent, return Tie.
7. Margin = absolute difference between total scores.
8. Confidence represents how certain you are about the comparison.
"""


# ============================================================
# GEMINI CALL
# ============================================================

response = client.models.generate_content(
    model=JUDGE_MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json",
        response_schema=Evaluation,
    ),
)


# ============================================================
# PARSE STRUCTURED RESPONSE
# ============================================================

result = Evaluation.model_validate_json(response.text)


# ============================================================
# VALIDATE SCORES
# ============================================================

def validate_score(name: str, score: ModelScore):
    calculated = (
        score.correctness
        + score.reasoning
        + score.depth
        + score.verification
        + score.robustness
        + score.instruction_following
    )

    if calculated != score.total:
        raise ValueError(
            f"{name} score mismatch: "
            f"categories={calculated}, total={score.total}"
        )


validate_score("Astra", result.astra)
validate_score("Fable", result.fable)


# ============================================================
# VALIDATE WINNER
# ============================================================

actual_margin = abs(
    result.astra.total - result.fable.total
)

if result.margin != actual_margin:
    raise ValueError(
        f"Invalid margin: Gemini={result.margin}, "
        f"calculated={actual_margin}"
    )


expected_winner = (
    "Astra"
    if result.astra.total > result.fable.total
    else "Fable"
    if result.fable.total > result.astra.total
    else "Tie"
)

if result.winner != expected_winner:
    raise ValueError(
        f"Invalid winner: Gemini={result.winner}, "
        f"calculated={expected_winner}"
    )


# ============================================================
# OUTPUT
# ============================================================

def print_model(name: str, score: ModelScore):

    print(f"\n{name}")
    print("-" * 40)

    print(f"Correctness          : {score.correctness}/30")
    print(f"Reasoning            : {score.reasoning}/25")
    print(f"Depth                : {score.depth}/15")
    print(f"Verification         : {score.verification}/10")
    print(f"Robustness           : {score.robustness}/10")
    print(f"Instruction Following: {score.instruction_following}/10")
    print(f"TOTAL                : {score.total}/100")

    print("\nStrengths:")
    for item in score.strengths:
        print(f"  + {item}")

    print("\nWeaknesses:")
    for item in score.weaknesses:
        print(f"  - {item}")


print("\n" + "=" * 60)
print("ASTRA vs FABLE")
print("=" * 60)

print_model("ASTRA", result.astra)
print_model("FABLE", result.fable)

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

print(f"Winner     : {result.winner}")
print(f"Margin     : {result.margin}/100")
print(f"Confidence : {result.confidence}%")
print(f"\nReason:\n{result.reason}")
