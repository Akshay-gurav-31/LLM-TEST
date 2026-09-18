from openai import OpenAI

client = OpenAI()

prompt = """
You are a startup mentor.

Suggest one unique AI startup idea for college students in India.

Include:
1. Startup name
2. Problem it solves
3. How AI is used
4. Target users
5. One unique feature

Keep the answer under 100 words.
"""

temperatures = [0.1, 0.7, 1.2]

for temperature in temperatures:

    print("\n" + "=" * 70)
    print(f"TEMPERATURE: {temperature}")
    print("=" * 70)

    for run in range(3):

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and creative startup mentor."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature
        )

        answer = response.choices[0].message.content

        print(f"\n--- Run {run + 1} ---")
        print(answer)
