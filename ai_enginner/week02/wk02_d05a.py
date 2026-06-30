"""Airline AI Assistant"""
import os
import json
import sqlite3
import base64
from io import BytesIO
from PIL import Image
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
IMAGE_MODEL  = "gpt-image-1-mini" # "dall-e-3"
SPEECH_MODEL = "gpt-4o-mini-tts"
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


def check_env(api_key):
    """Check if OPENAI API key exists"""
    if api_key:
        print(f"OpenAI API Key exists and begins {api_key[:8]}")
    else:
        print("OpenAI API Key not set")


def get_ticket_price(city):
    print(f"DATABASE TOOL CALLED: Getting price for {city}", flush=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM prices WHERE city = ?', (city.lower(),))
        result = cursor.fetchone()
        return f"Ticket price to {city} is ${result[0]}" if result else "No price data available for this city"


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

tools = [{"type": "function", "function": price_function}]


def handle_tool_calls_and_return_cities(message):
    responses = []
    cities = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_ticket_price":
            arguments = json.loads(tool_call.function.arguments)
            city = arguments.get('destination_city')
            cities.append(city)
            price_details = get_ticket_price(city)
            responses.append({
                "role": "tool",
                "content": price_details,
                "tool_call_id": tool_call.id
            })
    return responses, cities


def artist(city):
    image_response = openai.images.generate(
            model= IMAGE_MODEL, #,
            prompt=f"An image representing a vacation in {city}, showing tourist spots and everything unique about {city}, in a vibrant pop-art style",
            size="1024x1024",
            n=1,
            # response_format="b64_json",
        )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_data))


def talker(message):
    response = openai.audio.speech.create(
      model = SPEECH_MODEL,
      voice = "onyx",    # Also, try replacing onyx with alloy or coral
      input = message
    )
    return response.content


def chat(history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history
    response = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages, tools=tools)
    cities = []
    image = None

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses, cities = handle_tool_calls_and_return_cities(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages, tools=tools)

    reply = response.choices[0].message.content
    history += [{"role":"assistant", "content":reply}]

    voice = talker(reply)

    if cities:
        image = artist(cities[0])
    
    return history, voice, image


# Create gradio UI
def put_message_in_chatbot(message, history):
        return "", history + [{"role":"user", "content":message}]

# UI definition
with gr.Blocks() as ui:
    with gr.Row():
        chatbot = gr.Chatbot(height=500, type="messages")
        image_output = gr.Image(height=500, interactive=False)
    with gr.Row():
        audio_output = gr.Audio(autoplay=True)
    with gr.Row():
        message = gr.Textbox(label="Chat with our AI Assistant:")

    # Hooking up events to callbacks

    message.submit(put_message_in_chatbot, inputs=[message, chatbot], outputs=[message, chatbot]).then(
        chat, inputs=chatbot, outputs=[chatbot, audio_output, image_output]
    )



if __name__ == "__main__":
    check_env(api_key=openai_api_key)
    ui.launch(inbrowser=True, auth=("indra", "welcome"))

