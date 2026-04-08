from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import anthropic
import os
import uvicorn

app = FastAPI()

# Initialize Anthropic Client
# Automatically uses the ANTHROPIC_API_KEY environment variable
client = anthropic.Anthropic()

class ChatRequest(BaseModel):
    message: str

# 1. THE FRONTEND UI
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Claude Assistant</title>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

            :root {
                --bg: #0f0f11;
                --surface: #18181c;
                --surface-2: #222228;
                --border: #2e2e38;
                --accent: #d97757;
                --accent-dim: rgba(217, 119, 87, 0.15);
                --text: #e8e8f0;
                --text-dim: #7a7a90;
                --user-bg: #d97757;
                --bot-bg: #222228;
                --radius: 16px;
            }

            body {
                font-family: 'DM Sans', sans-serif;
                background: var(--bg);
                color: var(--text);
                height: 100dvh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 16px;
            }

            #chat-container {
                width: 100%;
                max-width: 680px;
                height: min(780px, calc(100dvh - 32px));
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 24px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 32px 80px rgba(0,0,0,0.6);
            }

            #header {
                padding: 20px 24px;
                border-bottom: 1px solid var(--border);
                display: flex;
                align-items: center;
                gap: 12px;
                background: var(--surface);
            }

            .logo {
                width: 36px;
                height: 36px;
                background: var(--accent);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                flex-shrink: 0;
            }

            .header-text h1 {
                font-size: 0.95rem;
                font-weight: 600;
                letter-spacing: 0.01em;
            }

            .header-text p {
                font-size: 0.75rem;
                color: var(--text-dim);
                font-weight: 400;
            }

            .status-dot {
                width: 7px;
                height: 7px;
                background: #4ade80;
                border-radius: 50%;
                margin-left: auto;
                box-shadow: 0 0 6px #4ade80;
                flex-shrink: 0;
            }

            #messages {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 16px;
                scroll-behavior: smooth;
            }

            #messages::-webkit-scrollbar { width: 4px; }
            #messages::-webkit-scrollbar-track { background: transparent; }
            #messages::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

            .msg-row {
                display: flex;
                gap: 10px;
                animation: fadeUp 0.25s ease forwards;
            }

            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(8px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            .msg-row.user { flex-direction: row-reverse; }

            .avatar {
                width: 30px;
                height: 30px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                flex-shrink: 0;
                margin-top: 2px;
            }

            .avatar.bot { background: var(--accent-dim); color: var(--accent); border: 1px solid var(--border); }
            .avatar.user { background: var(--accent); color: #fff; }

            .msg {
                padding: 12px 16px;
                border-radius: 14px;
                max-width: 78%;
                font-size: 0.9rem;
                line-height: 1.6;
                word-break: break-word;
                white-space: pre-wrap;
            }

            .msg-row.bot .msg {
                background: var(--bot-bg);
                color: var(--text);
                border: 1px solid var(--border);
                border-top-left-radius: 4px;
            }

            .msg-row.user .msg {
                background: var(--user-bg);
                color: #fff;
                border-top-right-radius: 4px;
            }

            #typing-row {
                display: none;
                align-items: center;
                gap: 10px;
                padding: 0 0 4px;
            }

            .typing-bubble {
                background: var(--bot-bg);
                border: 1px solid var(--border);
                border-radius: 14px;
                border-top-left-radius: 4px;
                padding: 12px 16px;
                display: flex;
                gap: 5px;
                align-items: center;
            }

            .dot {
                width: 6px; height: 6px;
                background: var(--text-dim);
                border-radius: 50%;
                animation: bounce 1.2s infinite;
            }
            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }

            @keyframes bounce {
                0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                30% { transform: translateY(-5px); opacity: 1; }
            }

            #input-area {
                padding: 16px 20px;
                background: var(--surface);
                border-top: 1px solid var(--border);
                display: flex;
                gap: 10px;
                align-items: flex-end;
            }

            #user-input {
                flex: 1;
                background: var(--surface-2);
                border: 1px solid var(--border);
                border-radius: 12px;
                color: var(--text);
                font-family: 'DM Sans', sans-serif;
                font-size: 0.9rem;
                padding: 12px 16px;
                resize: none;
                outline: none;
                line-height: 1.5;
                max-height: 120px;
                overflow-y: auto;
                transition: border-color 0.2s;
            }

            #user-input::placeholder { color: var(--text-dim); }
            #user-input:focus { border-color: var(--accent); }

            #send-btn {
                width: 42px;
                height: 42px;
                background: var(--accent);
                border: none;
                border-radius: 12px;
                color: #fff;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                transition: background 0.2s, transform 0.1s;
            }

            #send-btn:hover { background: #c4623e; }
            #send-btn:active { transform: scale(0.94); }

            #send-btn svg { width: 18px; height: 18px; }
        </style>
    </head>
    <body>
        <div id="chat-container">
            <div id="header">
                <div class="logo">✦</div>
                <div class="header-text">
                    <h1>Claude Assistant</h1>
                    <p>Powered by Anthropic</p>
                </div>
                <div class="status-dot"></div>
            </div>

            <div id="messages">
                <div class="msg-row bot">
                    <div class="avatar bot">✦</div>
                    <div class="msg">Hello! I'm Claude, made by Anthropic. How can I help you today?</div>
                </div>
            </div>

            <div id="typing-row">
                <div class="avatar bot" style="margin-left:24px;">✦</div>
                <div class="typing-bubble">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>

            <div id="input-area">
                <textarea id="user-input" placeholder="Message Claude..." rows="1"></textarea>
                <button id="send-btn" onclick="sendMessage()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                </button>
            </div>
        </div>

        <script>
            const input = document.getElementById('user-input');
            const messages = document.getElementById('messages');
            const typingRow = document.getElementById('typing-row');

            // Auto-resize textarea
            input.addEventListener('input', () => {
                input.style.height = 'auto';
                input.style.height = Math.min(input.scrollHeight, 120) + 'px';
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            async function sendMessage() {
                const msg = input.value.trim();
                if (!msg) return;

                addMessage(msg, 'user');
                input.value = '';
                input.style.height = 'auto';

                typingRow.style.display = 'flex';
                messages.scrollTop = messages.scrollHeight;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: msg })
                    });
                    const data = await response.json();
                    typingRow.style.display = 'none';
                    addMessage(data.reply, 'bot');
                } catch (err) {
                    typingRow.style.display = 'none';
                    addMessage('Something went wrong connecting to the server.', 'bot');
                }
            }

            function addMessage(text, role) {
                const row = document.createElement('div');
                row.className = 'msg-row ' + role;

                const avatar = document.createElement('div');
                avatar.className = 'avatar ' + role;
                avatar.textContent = role === 'bot' ? '✦' : '↑';

                const bubble = document.createElement('div');
                bubble.className = 'msg';
                bubble.textContent = text;

                row.appendChild(avatar);
                row.appendChild(bubble);

                messages.insertBefore(row, typingRow);
                messages.scrollTop = messages.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

# 2. THE BACKEND API ENDPOINT
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system="You are a helpful, professional AI assistant. Keep responses clear and engaging.",
            messages=[
                {"role": "user", "content": req.message}
            ]
        )
        return {"reply": response.content[0].text}
    except Exception as e:
        return {"reply": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)