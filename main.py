from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import uvicorn

app = FastAPI()

# Initialize OpenAI Client 9uses modern >=1.0.0 syntax)
# It automatically looks for the OPENAI_API_KEY environment variable
cleint = OpenAI()

class ChatRequest(BaseModel):
    message: str

#1. THE FRONTEND UI
@app.get("/", response_class=HTMLResponse)
async def get_ui():
return """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ai assistant Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        #chat-container {
            width: 100%;
            max-width: 450px;
            height: 80vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        #header {
            background: #0078D4;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
        }

        #messages {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #fafafa;
        }

        .msg {
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 75%;
            word-wrap: break-word;
            font-size: 0.95rem;
            line-height: 1.4;
        }

        .user-msg {
            background: #0078D4;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .bot-msg {
            background: #e4e6eb;
            color: #1c1e21;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        #input-area {
            display: flex;
            padding: 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }

        input {
            flex-grow: 1;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 24px;
            outline: none;
            font-size: 0.95rem;
            padding-left: 15px;
            transition: border 0.3s;
        }

        input:focus {
            border-color: #0078D4;
        }

        button {
            background: #0078D4;
            color: white;
            border: none;
            padding: 0 20px;
            margin-left: 10px;
            border-radius: 24px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }

        button:hover {
            background: #005a9e;
        }

        .typing {
            align-self: flex-start;
            color: #888;
            font-size: 0.85rem;
            margin-top: -5px;
            display: none;
        }
    </style>
</head>

<body>
    <div id="chat-container">
        <div id="header">AI Assistant Demo</div>
        <div id="messages">
            <div class="msg bot-msg">Hello! I'm online and ready to help. What's on your mind?</div>
        </div>
        <div id="typing-indicator" class="typing">AI is typing...</div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;

            // Add user message to UI
            addMessage(msg, 'user-msg');
            input.value = '';

            // Show typing indicator
            const typing = document.getElementById('typing-indicator');
            typing.style.display = 'block';

            try {
                // Call the FastAPI backend
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg })
                });
                const data = await response.json();

                typing.style.display = 'none';
                addMessage(data.reply, 'bot-msg');
            } catch (error) {
                typing.style.display = 'none';
                addMessage("Error connecting to the server.", 'bot-msg');
            }
        }

        function addMessage(text, className) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'msg ' + className;
            div.innerText = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight; // Auto-scroll to bottom
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }
    </script>

</body>

</html>
"""

# 2. THE BACKEND API ENDPOINT

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
try:
# Using gpt-4o-mini to keep costs practically zero while being highly capable
response = client.chat.completions.create(
model="gpt-4o-mini",
messages=[
{"role": "system", "content": "You are a helpful, professional AI assistant. Keep responses clear and engaging."},
{"role": "user", "content": req.message}
]
)
return {"reply": response.choices[0].message.content}
except Exception as e:
return {"reply": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
port = int(os.environ.get("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)