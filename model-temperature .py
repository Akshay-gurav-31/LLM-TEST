for temperature in [0.1, 1.0]:

    print(f"\n========== TEMP {temperature} ==========")

    for i in range(5):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Give me one creative startup idea for students in India."
                }
            ],
            temperature=temperature
        )

        print(f"\nRun {i+1}:")
        print(response.choices[0].message.content)
