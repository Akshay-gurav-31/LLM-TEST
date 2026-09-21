from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# Environment
# ============================================================

load_dotenv()


# ============================================================
# Configuration
# ============================================================

@dataclass(frozen=True)
class Config:
    api_key: str
    text_model: str = "gpt-5.6"
    image_model: str = "gpt-image-2"
    output_dir: Path = Path("outputs")
    timeout: float = 120.0
    max_retries: int = 3


def load_config() -> Config:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing.\n"
            "Create a .env file containing:\n\n"
            "OPENAI_API_KEY=your_api_key"
        )

    return Config(
        api_key=api_key,
        text_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-5.6"),
        image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"),
        output_dir=Path(
            os.getenv("OPENAI_OUTPUT_DIR", "outputs")
        ),
        timeout=float(
            os.getenv("OPENAI_TIMEOUT", "120")
        ),
        max_retries=int(
            os.getenv("OPENAI_MAX_RETRIES", "3")
        ),
    )


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("openai-demo")


# ============================================================
# Client
# ============================================================

def create_client(config: Config) -> OpenAI:
    return OpenAI(
        api_key=config.api_key,
        timeout=config.timeout,
        max_retries=config.max_retries,
    )


# ============================================================
# Utility
# ============================================================

T = TypeVar("T")


def measure(
    operation: Callable[[], T],
) -> tuple[T, float]:

    start = time.perf_counter()

    result = operation()

    elapsed = time.perf_counter() - start

    return result, elapsed


def save_json(
    path: Path,
    data: dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


# ============================================================
# Text Generation
# ============================================================

def generate_rag_explanation(
    client: OpenAI,
    config: Config,
    custom_prompt: str | None = None,
) -> dict[str, Any]:

    prompt = custom_prompt or """
Explain Retrieval-Augmented Generation (RAG).

Return a structured explanation with:

1. definition
2. why_it_is_used
3. workflow
4. practical_example
5. advantages
6. limitations

Keep the explanation beginner-friendly.

Use valid JSON with exactly these keys:

{
  "definition": "...",
  "why_it_is_used": "...",
  "workflow": [
    "...",
    "...",
    "..."
  ],
  "practical_example": "...",
  "advantages": [
    "..."
  ],
  "limitations": [
    "..."
  ]
}
"""

    logger.info(
        "Generating text with %s",
        config.text_model,
    )

    def request():

        return client.responses.create(
            model=config.text_model,
            input=prompt,
        )

    response, elapsed = measure(request)

    text = response.output_text.strip()

    result: dict[str, Any] = {
        "model": config.text_model,
        "elapsed_seconds": round(elapsed, 3),
        "response": text,
    }

    # --------------------------------------------------------
    # Usage
    # --------------------------------------------------------

    if getattr(response, "usage", None):

        usage = response.usage

        result["usage"] = {
            "input_tokens": getattr(
                usage,
                "input_tokens",
                None,
            ),
            "output_tokens": getattr(
                usage,
                "output_tokens",
                None,
            ),
            "total_tokens": getattr(
                usage,
                "total_tokens",
                None,
            ),
        }

    return result


# ============================================================
# Image Generation
# ============================================================

def generate_image(
    client: OpenAI,
    config: Config,
    custom_prompt: str | None = None,
) -> dict[str, Any]:

    prompt = custom_prompt or """
Create a photorealistic futuristic AI laboratory.

Main subject:
A professional software engineer working at a high-end
computer workstation.

Environment:
- futuristic AI research laboratory
- holographic neural networks
- floating data visualizations
- advanced computing equipment
- subtle blue ambient lighting
- realistic materials
- cinematic depth of field

Style:
- photorealistic
- cinematic
- premium technology aesthetic
- highly detailed
- professional
- realistic human proportions

Composition:
- 16:9 cinematic feeling inside a square frame
- developer as the visual focus
- neural network visualization in the background
- balanced composition

Do not include:
- text
- logos
- watermarks
- UI screenshots
- distorted hands
- duplicate people
"""

    logger.info(
        "Generating image with %s",
        config.image_model,
    )

    def request():

        return client.images.generate(
            model=config.image_model,
            prompt=prompt,
            size="1024x1024",
        )

    response, elapsed = measure(request)

    if not response.data:
        raise RuntimeError(
            "Image API returned no image data."
        )

    image = response.data[0]

    image_base64 = getattr(
        image,
        "b64_json",
        None,
    )

    if not image_base64:
        raise RuntimeError(
            "Image response did not contain b64_json."
        )

    config.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path = (
        config.output_dir /
        "ai_laboratory.png"
    )

    image_bytes = base64.b64decode(
        image_base64
    )

    image_path.write_bytes(
        image_bytes
    )

    return {
        "model": config.image_model,
        "elapsed_seconds": round(
            elapsed,
            3,
        ),
        "file": str(
            image_path.resolve()
        ),
        "size_bytes": len(image_bytes),
    }


# ============================================================
# API Health Check
# ============================================================

def health_check(
    client: OpenAI,
    config: Config,
) -> bool:

    logger.info("Running API health check...")

    try:

        response = client.responses.create(
            model=config.text_model,
            input="Reply with exactly: OK",
        )

        result = response.output_text.strip()

        if result.upper() == "OK":
            logger.info(
                "API health check: OK"
            )
            return True

        logger.warning(
            "API responded, but unexpected output: %s",
            result,
        )

        return True

    except Exception as error:

        logger.error(
            "API health check failed: %s",
            error,
        )

        return False


# ============================================================
# CLI
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="Advanced OpenAI API demo"
    )

    parser.add_argument(
        "--text",
        action="store_true",
        help="Run text generation",
    )

    parser.add_argument(
        "--image",
        action="store_true",
        help="Run image generation",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests",
    )

    parser.add_argument(
        "--health",
        action="store_true",
        help="Run API health check",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        help="Custom text/image prompt",
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================

def main() -> int:

    try:

        config = load_config()

        client = create_client(
            config
        )

    except Exception as error:

        logger.error(
            "Initialization failed: %s",
            error,
        )

        return 1

    args = parse_args()

    # --------------------------------------------------------
    # Default behavior
    # --------------------------------------------------------

    if not any(
        [
            args.text,
            args.image,
            args.all,
            args.health,
        ]
    ):
        args.all = True

    # --------------------------------------------------------
    # Health Check
    # --------------------------------------------------------

    if args.health:

        if not health_check(
            client,
            config,
        ):
            return 1

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    if args.text or args.all:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "TEXT GENERATION"
        )

        print(
            "=" * 70
        )

        try:

            result = generate_rag_explanation(
                client,
                config,
                args.prompt,
            )

            print(
                "\n"
                + result["response"]
            )

            print(
                "\n"
                f"Time: "
                f"{result['elapsed_seconds']}s"
            )

            if "usage" in result:

                print(
                    "Usage:",
                    result["usage"],
                )

            save_json(
                config.output_dir /
                "text_result.json",
                result,
            )

            print(
                "\nSaved:"
                " outputs/text_result.json"
            )

        except Exception as error:

            logger.error(
                "Text generation failed: %s",
                error,
            )

    # --------------------------------------------------------
    # Image
    # --------------------------------------------------------

    if args.image or args.all:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "IMAGE GENERATION"
        )

        print(
            "=" * 70
        )

        try:

            result = generate_image(
                client,
                config,
                args.prompt,
            )

            print(
                "\nImage generated successfully."
            )

            print(
                f"File: {result['file']}"
            )

            print(
                f"Size: "
                f"{result['size_bytes']:,} bytes"
            )

            print(
                f"Time: "
                f"{result['elapsed_seconds']}s"
            )

            save_json(
                config.output_dir /
                "image_result.json",
                result,
            )

        except Exception as error:

            logger.error(
                "Image generation failed: %s",
                error,
            )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "DONE"
    )

    print(
        "=" * 70
    )

    return 0


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    sys.exit(main())
