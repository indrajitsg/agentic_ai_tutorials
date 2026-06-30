"""Generate an SVG Image"""
import os
import json
import sqlite3
import base64
from io import BytesIO
from PIL import Image
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from revealer import reveal
from IPython.display import Markdown, display

# Load environment variables
load_dotenv(override=True)
openai_api_key     = os.getenv('OPENAI_API_KEY')
anthropic_api_key  = os.getenv('ANTHROPIC_API_KEY')
google_api_key     = os.getenv('GOOGLE_API_KEY')
router_api_key     = os.getenv('OPENROUTER_API_KEY')
ollama_api_key     = "ollama"

# Set models
OPENAI_MODEL = "gpt-5-mini"
IMAGE_MODEL  = "gpt-image-1-mini" # "dall-e-3"
CLAUDE_MODEL = "claude-sonnet-4-6"
OLLAMA_MODEL = "llama3.2:latest" # "qwen3.5:2b" #
ROUTER_MODEL = "deepseek/deepseek-v3.2"

# Set URLs
anthropic_url  = "https://api.anthropic.com/v1/"
gemini_url     = "https://generativelanguage.googleapis.com/v1beta/openai/"
ollama_url     = "http://localhost:11434/v1"
router_url     = "https://openrouter.ai/api/v1"

# Connect to OpenAI
openai   = OpenAI()
claude   = OpenAI(api_key=anthropic_api_key, base_url=anthropic_url)
gemini   = OpenAI(api_key=google_api_key, base_url=gemini_url)
ollama   = OpenAI(api_key=ollama_api_key, base_url=ollama_url)
router   = OpenAI(api_key=router_api_key, base_url=router_url)

challenge = "a panda rollerblading to work"
prompt = f"Generate an SVG of {challenge}. Respond with the SVG only, no code blocks."
messages = [{"role": "user", "content": prompt}]


def artist(model, effort=None):
    try:
        start = datetime.now()
        response = router.chat.completions.create(model=model, messages=messages, reasoning_effort=effort)
        result = response.choices[0].message.content
        end = datetime.now()
        elapsed = (end - start).total_seconds()
        heading = f"### {model}\n**Time:** {elapsed // 60:.0f} min {elapsed % 60:.0f} s\n\n"
    except Exception as e:
        print(f"Model {model} failed: {e}")
        heading = f"### {model}\n**Error:** {e}\n\n"
        return heading, None
    return heading, result


if __name__ == "__main__":
    output_dir = "week02/svg_outputs"
    os.makedirs(output_dir, exist_ok=True)

    results = [
        artist("openai/gpt-oss-120b"),
        artist("openai/gpt-5-nano", effort="low"),
        artist("deepseek/deepseek-v3.2"),
        artist("moonshotai/kimi-k2-thinking"),
        artist("x-ai/grok-4.1-fast"),
        artist("anthropic/claude-opus-4.5"),
        artist("openai/gpt-5.2", effort="high"),
        artist("google/gemini-3-pro-preview"),
        artist("google/gemini-3.1-flash-image")
    ]

    for i, result in enumerate(results, start=1):
        heading, svg = result

        print(heading)

        if not svg:
            print("No SVG returned.\n")
            continue
        
        # Save SVG file
        filename = os.path.join(output_dir, f"result_{i}.svg")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)

        print(f"Saved: {filename}\n")

        # Save animated SVG file
        animated_svg = reveal(svg)
        filename = os.path.join(output_dir, f"animated_result_{i}.svg")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(animated_svg or svg)