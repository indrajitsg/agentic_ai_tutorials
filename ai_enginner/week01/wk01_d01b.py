"""Web Scraping and Summarizing with GPT & Ollama"""
import os
from dotenv import load_dotenv
from scraper import fetch_website_contents
from IPython.display import Markdown, display
from openai import OpenAI


load_dotenv(override=True)
openai_api_key  = os.getenv('OPENAI_API_KEY')
ollama_api_key  = "ollama"

OPENAI_MODEL = "gpt-5-mini"
OLLAMA_MODEL = "deepseek-r1:1.5b" #"gemma3:270m"

ollama_url     = "http://localhost:11434/v1"

def check_api_key():
    # Check the key
    if not openai_api_key:
        print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
    elif not openai_api_key.startswith("sk-proj-"):
        print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
    elif openai_api_key.strip() != openai_api_key:
        print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
    else:
        print("API key found and looks good so far!")

# Connect to OpenAI
openai   = OpenAI()
ollama   = OpenAI(api_key=ollama_api_key, base_url=ollama_url)

system_prompt = """
You are a helpful assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.

"""

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website}
    ]


def summarize(url):
    website = fetch_website_contents(url)
    response = ollama.chat.completions.create(
        model = OLLAMA_MODEL,
        messages = messages_for(website)
    )
    return response.choices[0].message.content


def display_summary(url):
    summary = summarize(url)
    # display(Markdown(summary))
    print(summary)



if __name__ == "__main__":
    check_api_key()
    # display_summary("https://edwarddonner.com")
    display_summary("https://www.twz.com")

    
