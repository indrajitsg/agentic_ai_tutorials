"""Airline AI Assistant"""
import os
import json
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
OLLAMA_MODEL = "llama3.2:latest" # "qwen3.5:2b" #

# Set URLs
anthropic_url  = "https://api.anthropic.com/v1/"
gemini_url     = "https://generativelanguage.googleapis.com/v1beta/openai/"
ollama_url     = "http://localhost:11434/v1"

# Connect to OpenAI
openai   = OpenAI()
claude   = OpenAI(api_key=anthropic_api_key, base_url=anthropic_url)
gemini   = OpenAI(api_key=google_api_key, base_url=gemini_url)
ollama   = OpenAI(api_key=ollama_api_key, base_url=ollama_url)

system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

# Defining tools
ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

def get_ticket_price(destination_city):
    print(f"Tool called for city {destination_city}")
    price = ticket_prices.get(destination_city.lower(), "Unknown ticket price")
    return f"The price of a ticket to {destination_city} is {price}"

# Dictionary for our function
price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

# And this is included in a list of tools:
tools = [{"type": "function", "function": price_function}]


def handle_tool_call(message):
    """Handle a single tool call.
    """
    tool_call = message.tool_calls[0]
    if tool_call.function.name == "get_ticket_price":
        arguments = json.loads(tool_call.function.arguments)
        city = arguments.get('destination_city')
        price_details = get_ticket_price(city)
        response = {
            "role": "tool",
            "content": price_details,
            "tool_call_id": tool_call.id
        }
    return response


def chat(message, history):
    """Chat function for Gradio. Supports only a single location search.
    """
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages, tools=tools)

    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        response = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages)
    
    return response.choices[0].message.content


view = gr.ChatInterface(fn=chat, type="messages")

if __name__ == "__main__":
    view.launch()
