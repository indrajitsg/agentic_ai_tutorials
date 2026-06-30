"""Airline AI Assistant using SQLite DB"""
import os
import json
import sqlite3
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

# Set DB file
DB_FILE = "week02/prices.db"

system_message = """
You are a helpful assistant for an Airline called FlightAI.
Give short, courteous answers, no more than 1 sentence.
Always be accurate. If you don't know the answer, say so.
"""

def create_sqldb():
    """Create SQLite Database"""
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS prices (city TEXT PRIMARY KEY, price REAL)")
        conn.commit()


def get_ticket_price(city):
    print(f"DATABASE TOOL CALLED: Getting price for {city}", flush=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM prices WHERE city = ?', (city.lower(),))
        result = cursor.fetchone()
        return f"Ticket price to {city} is ${result[0]}" if result else "No price data available for this city"


def set_ticket_price(city, price):
    print(f"Setting ticket price for {city}, {price}")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prices (city, price) VALUES (?, ?) ON CONFLICT(city) DO UPDATE SET price = ?', (city.lower(), price, price))
        conn.commit()


def update_db_table():
    ticket_prices = {"london":799, "paris": 899, "tokyo": 1420, "sydney": 2999}
    for city, price in ticket_prices.items():
        set_ticket_price(city, price)


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

add_ticket_function = {
    "name": "set_ticket_price",
    "description": "Insert new price of a ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to insert the ticket price for",
            },
            "ticket_price": {
                "type": "number",
                "description": "Price of the ticket"
            },
        },
        "required": ["destination_city", "ticket_price"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": price_function},
    {"type": "function", "function": add_ticket_function}
]


def handle_tool_calls(message):
    """Handle multiple tool calls.
    """
    print(f"Received message: {message}")
    responses = []
    for tool_call in message.tool_calls:
        arguments = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "get_ticket_price":
            city = arguments.get("destination_city")
            result = get_ticket_price(city)
        elif tool_call.function.name == "set_ticket_price":
            city = arguments.get("destination_city")
            price = arguments.get("ticket_price")
            set_ticket_price(city, price)
            result = f"Ticket price to {city} has been set to ${price}"
        else:
            result = f"Unknown tool call: {tool_call.function.name}"

        responses.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tool_call.id
        })
    return responses


def chat(message, history):
    """Chat function for Gradio. Supports multiple location searches.
    """
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = claude.chat.completions.create(model=CLAUDE_MODEL, messages=messages, tools=tools)
    
    return response.choices[0].message.content


view = gr.ChatInterface(fn=chat, type="messages")

if __name__ == "__main__":
    # Create DB
    print("Creating database")
    create_sqldb()
    update_db_table()
    print("Finished creating database. Data loaded")
    view.launch()
