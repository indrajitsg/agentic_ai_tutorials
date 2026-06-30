"""Gradio"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

# Connect to OpenAI, Anthropic & Google
openai = OpenAI()

anthropic_url = "https://api.anthropic.com/v1/"
gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

anthropic = OpenAI(api_key=anthropic_api_key, base_url=anthropic_url)
gemini = OpenAI(api_key=google_api_key, base_url=gemini_url)

# Call to GPT-5-mini in a simple function
system_message = "You are a helpful assistant"


def message_gpt(prompt):
    messages = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
    response = openai.chat.completions.create(model="gpt-5-mini", messages=messages)
    return response.choices[0].message.content


# here's a simple function
def shout(text):
    print(f"Shout has been called with input {text}")
    return text.upper()

    
force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

# Adding a little more:
message_input1 = gr.Textbox(label="Your message:", info="Enter a message to be shouted", lines=7)
message_output1 = gr.Textbox(label="Response:", info="The response will appear here", lines=7)
view1 = gr.Interface(
    fn=shout,
    title="Shout", 
    inputs=[message_input1], 
    outputs=[message_output1], 
    examples=["hello", "howdy"], 
    flagging_mode="never"
)

# Change the function from `shout` to `message_gpt`
message_input2 = gr.Textbox(label="Your message:", info="Enter a message for GPT-5-mini", lines=7)
message_output2 = gr.Textbox(label="Response:", info="The response will appear here", lines=7)
view2 = gr.Interface(
    fn=message_gpt,
    title="GPT-5", 
    inputs=[message_input2], 
    outputs=[message_output2], 
    examples=["hello", "howdy"], 
    flagging_mode="never"
)

# Let's use Markdown
system_message2 = "You are a helpful assistant that responds in markdown without code blocks"
def message_gpt2(prompt):
    messages = [{"role": "system", "content": system_message2}, {"role": "user", "content": prompt}]
    response = openai.chat.completions.create(model="gpt-5-mini", messages=messages)
    return response.choices[0].message.content


message_input3= gr.Textbox(label="Your message:", info="Enter a message for GPT-5-mini", lines=7)
message_output3 = gr.Markdown(label="Response:")
view3 = gr.Interface(
    fn=message_gpt2,
    title="GPT", 
    inputs=[message_input3], 
    outputs=[message_output3], 
    examples=[
        "Explain the Transformer architecture to a layperson",
        "Explain the Transformer architecture to an aspiring AI engineer",
        ], 
    flagging_mode="never"
    )


# Using HTML
system_message3 = """
You are a helpful assistant.
Return valid HTML only.
Do not use markdown.
Do not use ``` code fences.
Use simple HTML tags such as <p>, <h2>, <ul>, <li>, <strong>, <code>, and <pre>.
"""
def message_gpt3(prompt):
    messages = [{"role": "system", "content": system_message3}, {"role": "user", "content": prompt}]
    response = openai.chat.completions.create(model="gpt-5-mini", messages=messages)
    return response.choices[0].message.content

message_input4 = gr.Textbox(label="Your message:", info="Enter a message for GPT-5-mini", lines=7)
message_output4 = gr.HTML(label="Response:")
view4 = gr.Interface(
    fn=message_gpt3,
    title="GPT",
    inputs=[message_input4],
    outputs=[message_output4],
    examples=[
        "Explain the Transformer architecture to a layperson",
        "Explain the Transformer architecture to an aspiring AI engineer",
    ],
    flagging_mode="never"
)


# Let's create a call that streams back results
def stream_gpt(prompt):
    messages = [
        {"role": "system", "content": system_message3},
        {"role": "user", "content": prompt}
      ]
    stream = openai.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


view5 = gr.Interface(
    fn=stream_gpt,
    title="GPT", 
    inputs=[message_input4], 
    outputs=[message_output4], 
    examples=[
        "Explain the Transformer architecture to a layperson",
        "Explain the Transformer architecture to an aspiring AI engineer",
        ], 
    flagging_mode="never"
)


def stream_claude(prompt):
    messages = [
        {"role": "system", "content": system_message3},
        {"role": "user", "content": prompt}
      ]
    stream = anthropic.chat.completions.create(
        model='claude-sonnet-4-6',
        messages=messages,
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


def stream_model(prompt, model):
    if model=="GPT":
        result = stream_gpt(prompt)
    elif model=="Claude":
        result = stream_claude(prompt)
    else:
        raise ValueError("Unknown model")
    yield from result


message_input5 = gr.Textbox(label="Your message:", info="Enter a message for the LLM", lines=7)
model_selector5 = gr.Dropdown(["GPT", "Claude"], label="Select model", value="GPT")
message_output5 = gr.HTML(label="Response:")

view6 = gr.Interface(
    fn=stream_model,
    title="LLMs", 
    inputs=[message_input5, model_selector5], 
    outputs=[message_output5], 
    examples=[
            ["Explain the Transformer architecture to a layperson", "GPT"],
            ["Explain the Transformer architecture to an aspiring AI engineer", "Claude"]
        ], 
    flagging_mode="never"
)

if __name__ == "__main__":
    # print(message_gpt("What is today's date?"))
    # A simple interface with input and output
    # gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never").launch()

    # Interface with authentication
    # gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never").launch(
    #     inbrowser=True, auth=("indra", "welcome")
    # )

    # Host publicly on Huggingface
    # gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never").launch(share=True)

    # Forcing dark mode
    # gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never", js=force_dark_mode).launch()

    # Adding custom labels
    # view1.launch()

    # Launch message_gpt
    # view2.launch()
    # view3.launch()
    # view4.launch()
    # view5.launch()
    view6.launch()


