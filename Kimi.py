
from openai import OpenAI

API_KEY = "MOONSHOT_API_KEY"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.moonshot.ai/v1"
)

print("Testing Kimi LLM...\n")

try:
    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {
                "role": "system",
                "content": "You are an intelligent AI assistant."
            },
            {
                "role": "user",
                "content": "Hello Kimi! Introduce yourself and explain what you can do."
            }
        ],
        temperature=0.6
    )

    print("KIMI RESPONSE:")
    print(response.choices[0].message.content)

    print("\nTOKEN USAGE:")
    print(response.usage)

except Exception as e:
    print("Error:", e)
