import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
Generate a high-quality image of a futuristic AI laboratory.
Show a developer working on a computer with holographic screens,
neural networks, and modern technology in the background.
Cinematic lighting, realistic details, professional composition.
"""

# Generate the image
response = client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
    size="1024x1024"
)

# Get the generated image
image_data = response.data[0]

print("Image generation completed.")
print(image_data)
