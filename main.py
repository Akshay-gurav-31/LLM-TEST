import os
import json
from google import genai

# ============================================================
# CONFIG
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in your environment.")

client = genai.Client(api_key=GEMINI_API_KEY)

JUDGE_MODEL = "gemini-3.8-flash"


# ============================================================
# TEST QUESTION
# ============================================================

QUESTION = """
A company has 3 AI models.

Model A costs $10 per million input tokens and $50 per million
output tokens.

Model B costs $5 per million input tokens and $25 per million
output tokens.

Model C costs $1 per million input tokens and $5 per million
output tokens.

A workload uses 2 million input tokens and 200,000 output tokens.

Calculate the total cost for each model and determine which model
is the cheapest.

Then explain the reasoning step by step and verify the calculations.
"""


# ============================================================
# PUT ASTRA AND FABLE ANSWERS HERE
# ============================================================

astra_answer = """
PASTE ASTRA'S ANSWER HERE
"""

fable_answer = """
PASTE FABLE'S ANSWER HERE
"""


# ============================================================
# GEMINI JUDGE PROMPT
# ============================================================

judge_prompt = f"""
You are an independent AI reasoning evaluator.

Your task is to compare two AI model responses to the EXACT same
reasoning problem.

Do NOT judge based on writing style, verbosity, or which model you
personally prefer.

Evaluate the actual quality of reasoning.

QUESTION:
{QUESTION}

========================
ASTRA RESPONSE
========================

{astra_answer}

========================
FABLE RESPONSE
========================

{fable_answer}

========================
EVALUATION RUBRIC
========================

Score each model from 0 to 100.

Use these weights:

1. Correctness of final answer: 30 points
2. Mathematical/logical reasoning: 25 points
3. Depth and completeness: 20 points
4. Detection and handling of assumptions: 10 points
5. Verification/self-checking: 10 points
6. Clarity of reasoning: 5 points

IMPORTANT:

- Do not reward longer answers automatically.
- Penalize incorrect reasoning even if the final answer happens
  to be correct.
- Penalize unsupported claims.
- Check every calculation yourself.
- If both answers are equally correct, give them equal scores.
- Do not invent information that is not present in the responses.
- The winner must be based only on the rubric.

Return ONLY valid JSON in this exact structure:

{{
    "astra": {{
        "correctness": 0,
        "reasoning": 0,
        "depth": 0,
        "assumptions": 0,
        "verification": 0,
        "clarity": 0,
        "total": 0,
        "strengths": [],
        "weaknesses": []
    }},
    "fable": {{
        "correctness": 0,
        "reasoning": 0,
        "depth": 0,
        "assumptions": 0,
        "verification": 0,
        "clarity": 0,
        "total": 0,
        "strengths": [],
        "weaknesses": []
    }},
    "winner": "Astra or Fable or Tie",
    "margin": 0,
    "reason": "Short factual explanation of why."
}}
"""


# ============================================================
# RUN GEMINI JUDGE
# ============================================================

response = client.models.generate_content(
    model=JUDGE_MODEL,
    contents=judge_prompt
)

result_text = response.text.strip()


# ============================================================
# PARSE JSON
# ============================================================

try:
    result = json.loads(result_text)
except json.JSONDecodeError:
    print("Gemini returned invalid JSON:")
    print(result_text)
    raise


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n" + "=" * 60)
print("ASTRA vs FABLE REASONING EVALUATION")
print("=" * 60)

print(f"\nAstra Score : {result['astra']['total']}/100")
print(f"Fable Score : {result['fable']['total']}/100")

print(f"\nWinner      : {result['winner']}")
print(f"Score Margin: {result['margin']} points")

print("\n" + "-" * 60)
print("ASTRA")
print("-" * 60)

print("Correctness :", result["astra"]["correctness"])
print("Reasoning   :", result["astra"]["reasoning"])
print("Depth       :", result["astra"]["depth"])
print("Assumptions :", result["astra"]["assumptions"])
print("Verification:", result["astra"]["verification"])
print("Clarity     :", result["astra"]["clarity"])

print("\nStrengths:")
for item in result["astra"]["strengths"]:
    print(f"- {item}")

print("\nWeaknesses:")
for item in result["astra"]["weaknesses"]:
    print(f"- {item}")


print("\n" + "-" * 60)
print("FABLE")
print("-" * 60)

print("Correctness :", result["fable"]["correctness"])
print("Reasoning   :", result["fable"]["reasoning"])
print("Depth       :", result["fable"]["depth"])
print("Assumptions :", result["fable"]["assumptions"])
print("Verification:", result["fable"]["verification"])
print("Clarity     :", result["fable"]["clarity"])

print("\nStrengths:")
for item in result["fable"]["strengths"]:
    print(f"- {item}")

print("\nWeaknesses:")
for item in result["fable"]["weaknesses"]:
    print(f"- {item}")


print("\n" + "=" * 60)
print("FINAL VERDICT")
print("=" * 60)

print(result["reason"])
