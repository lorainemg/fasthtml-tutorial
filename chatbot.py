from fasthtml.common import *

app = FastHTML()

messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assitant", "content": "Hi, how can I assist you?"}
]

def get_chat_message(msg):
    return Div(
        Div(msg["role"], cls="chat-header"),
        Div(msg["content"], cls=f"chat-bubble chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"),
        cls=f"chat chat-{'end' if msg['role'] == 'user' else 'start'}"
    )

@app.route("/")
def home():
    headers = (Script(src="https://cdn.tailwindcss.com"),
           Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))
    return headers, Div(*[get_chat_message(msg) for msg in messages], cls="chat-box", id="chatlist")

serve()