import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------
# 1. Text Generation Test
# -----------------------------

text_prompt = """
Explain what Retrieval-Augmented Generation (RAG) is.
Give the explanation in simple English with one practical example.
"""

text_response = client.responses.create(
    model="gpt-5.6",
    input=text_prompt
)

print("\n=== TEXT GENERATION ===")
print(text_response.output_text)


# -----------------------------
# 2. Image Generation Test
# -----------------------------

image_prompt = """
Create a realistic futuristic AI laboratory.
Show a software developer working on a computer,
with holographic neural network visualizations in the background.
Professional, cinematic lighting, highly detailed.
"""

image_response = client.images.generate(
    model="gpt-image-1",
    prompt=image_prompt,
    size="1024x1024"
)

print("\n=== IMAGE GENERATION ===")
print("Image generation completed.")

# Save the generated image
image_bytes = image_response.data[0].b64_json

import base64

with open("generated_image.png", "wb") as file:
    file.write(base64.b64decode(image_bytes))

print("Image saved as generated_image.png")
