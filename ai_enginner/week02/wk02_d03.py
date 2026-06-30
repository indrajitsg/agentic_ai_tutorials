"""Conversational AI - aka Chatbot"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Load environment variables
load_dotenv(override=True)
openai_api_key    = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key    = os.getenv('GOOGLE_API_KEY')
ollama_api_key    = "ollama"

# Set models
OPENAI_MODEL = "gpt-5-mini"
CLAUDE_MODEL = "claude-sonnet-4-6"
OLLAMA_MODEL = "qwen3.5:2b"

# Set URLs
anthropic_url  = "https://api.anthropic.com/v1/"
gemini_url     = "https://generativelanguage.googleapis.com/v1beta/openai/"
ollama_url     = "http://localhost:11434/v1"

# Connect to OpenAI
openai   = OpenAI()
claude   = OpenAI(api_key=anthropic_api_key, base_url=anthropic_url)
gemini   = OpenAI(api_key=google_api_key, base_url=gemini_url)
ollama   = OpenAI(api_key=ollama_api_key, base_url=ollama_url)

# Set system prompt
# system_message = "You are a helpful assistant"

system_message = """You are a helpful assistant in a clothes store. You should try to gently encourage \
the customer to try items that are on sale. Hats are 60% off, and most other items are 50% off. \
For example, if the customer says 'I'm looking to buy a hat', \
you could reply something like, 'Wonderful - we have lots of hats - including several that are part of our sales event.'\
Encourage the customer to buy hats if they are unsure what to get."""

system_message += "\nIf the customer asks for shoes, you should respond that shoes are not on sale today, \
but remind the customer to look at hats!"


# Callback function for gradio
def chat(message, history):
    relevant_system_message = system_message
    if 'belt' in message.lower():
        relevant_system_message += """ The store does not sell belts; if you are asked for belts,
        be sure to point out other items on sale."""
    
    history = [
        {
            "role": h["role"],
            "content": h["content"]
        } for h in history
    ]
    messages = [{"role": "system", "content": relevant_system_message}] + history + \
        [{"role": "user", "content": message}]
    
    # Regular response
    # response = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages)
    # return response.choices[0].message.content

    # Stream response
    stream = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages, stream=True)
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ""
        yield response



# Gradio chat interface
view = gr.ChatInterface(fn=chat, type="messages")


if __name__ == "__main__":
    view.launch()
