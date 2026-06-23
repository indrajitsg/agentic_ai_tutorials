"""Using OpenAI API"""
import os
from dotenv import load_dotenv
from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI


load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

OPENAI_MODEL = "gpt-5-nano"

def check_api_key():
    # Check the key
    if not api_key:
        print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
    elif not api_key.startswith("sk-proj-"):
        print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
    elif api_key.strip() != api_key:
        print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
    else:
        print("API key found and looks good so far!")

# Connect to OpenAI
openai = OpenAI()

system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""


def get_response(model, messages):
    response = openai.chat.completions.create(model=model, messages=messages)
    print(response.choices[0].message.content)


if __name__ == "__main__":
    check_api_key()

    messages = [
        {"role": "system", "content": "You are a snarky assistant"},
        {"role": "user", "content": "What is 2 + 2?"}
    ]

    get_response(model=OPENAI_MODEL, messages=messages)
