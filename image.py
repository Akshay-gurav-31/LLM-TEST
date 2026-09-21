"""
OpenAI API Test
---------------
Tests:
1. Text generation using Responses API
2. Image generation using Images API

Setup:
    pip install -U openai python-dotenv

Create a .env file:
    OPENAI_API_KEY=your_api_key_here

Run:
    python main.py
"""

import os
import base64
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# Configuration
# ============================================================

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

TEXT_MODEL = "gpt-5.6"
IMAGE_MODEL = "gpt-image-1"

OUTPUT_DIR = Path("outputs")
IMAGE_FILE = OUTPUT_DIR / "generated_image.png"


# ============================================================
# Client Setup
# ============================================================

def create_client() -> OpenAI:
    """Create and validate the OpenAI client."""

    if not API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing.\n"
            "Add it to your .env file:\n\n"
            "OPENAI_API_KEY=your_api_key_here"
        )

    return OpenAI(api_key=API_KEY)


# ============================================================
# Text Generation
# ============================================================

def generate_text(client: OpenAI) -> str:
    """Generate a simple explanation of RAG."""

    prompt = """
Explain Retrieval-Augmented Generation (RAG).

Requirements:
- Use simple English.
- Explain what RAG is.
- Explain how it works in 3-4 simple steps.
- Give one practical real-world example.
- Keep the explanation concise.
- Avoid unnecessary technical jargon.
"""

    response = client.responses.create(
        model=TEXT_MODEL,
        input=prompt,
    )

    if not response.output_text:
        raise RuntimeError("The API returned an empty text response.")

    return response.output_text.strip()


# ============================================================
# Image Generation
# ============================================================

def generate_image(client: OpenAI) -> Path:
    """Generate an AI laboratory image and save it locally."""

    prompt = """
Create a realistic futuristic AI laboratory.

Scene:
- A professional software developer working at a computer.
- Multiple holographic neural-network visualizations in the background.
- Advanced AI research environment.
- Modern computers and subtle futuristic technology.
- Realistic human proportions.
- Cinematic professional lighting.
- Highly detailed.
- Premium technology aesthetic.
- Photorealistic style.
- Clean composition.
- No text.
- No logos.
- No watermark.
- No UI overlays.
"""

    response = client.images.generate(
        model=IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
    )

    if not response.data:
        raise RuntimeError("The API returned no image data.")

    image_base64 = response.data[0].b64_json

    if not image_base64:
        raise RuntimeError(
            "The API response does not contain base64 image data."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with IMAGE_FILE.open("wb") as file:
        file.write(base64.b64decode(image_base64))

    return IMAGE_FILE


# ============================================================
# Text Test
# ============================================================

def run_text_test(client: OpenAI) -> None:
    """Run the text generation test."""

    print("\n" + "=" * 60)
    print("TEXT GENERATION")
    print("=" * 60)

    start_time = time.perf_counter()

    try:
        result = generate_text(client)

        elapsed = time.perf_counter() - start_time

        print("\nResponse:\n")
        print(result)

        print(f"\nTime: {elapsed:.2f}s")
        print("Status: SUCCESS")

    except Exception as error:
        print("\nStatus: FAILED")
        print(f"Error: {error}")


# ============================================================
# Image Test
# ============================================================

def run_image_test(client: OpenAI) -> None:
    """Run the image generation test."""

    print("\n" + "=" * 60)
    print("IMAGE GENERATION")
    print("=" * 60)

    start_time = time.perf_counter()

    try:
        image_path = generate_image(client)

        elapsed = time.perf_counter() - start_time

        print("\nImage generated successfully.")
        print(f"Saved to: {image_path.resolve()}")
        print(f"Time: {elapsed:.2f}s")
        print("Status: SUCCESS")

    except Exception as error:
        print("\nStatus: FAILED")
        print(f"Error: {error}")


# ============================================================
# Main
# ============================================================

def main():
    """Run all API tests."""

    print("\n" + "=" * 60)
    print("OPENAI API TEST")
    print("=" * 60)

    print(f"Text model : {TEXT_MODEL}")
    print(f"Image model: {IMAGE_MODEL}")

    try:
        client = create_client()

    except Exception as error:
        print("\nClient initialization failed.")
        print(f"Error: {error}")
        return

    # Run text generation
    run_text_test(client)

    # Run image generation
    run_image_test(client)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
