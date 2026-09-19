from openai import OpenAI

client = OpenAI()

prompt = """
A developer wakes up and discovers that every AI model has disappeared.
Write a short creative story about what happens next.
"""

temperatures = [0.2, 0.7, 1.2]

for temperature in temperatures:
    response = client.responses.create(
        model="gpt-5.6",
        input=prompt,
        temperature=temperature
    )

    print(f"\n{'=' * 60}")
    print(f"Temperature: {temperature}")
    print(f"{'=' * 60}")
    print(response.output_text)
