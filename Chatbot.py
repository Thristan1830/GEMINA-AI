# flask_gemini_chatbot.py
# Single-file Flask app that wraps your google.generativeai chatbot.
# Usage:
# 1) pip install flask google-generativeai
# 2) set your API key as an environment variable (safer) or hard-code (NOT recommended):
#    export GENAI_API_KEY="YOUR_KEY"
# 3) python flask_gemini_chatbot.py
# 4) open http://127.0.0.1:5000

import os
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

# --- Configuration ---
# Prefer reading the API key from an environment variable so you don't accidentally commit it.
API_KEY = os.getenv('GENAI_API_KEY') or os.getenv('GOOGLE_GENAI_API_KEY') or ''
if not API_KEY:
    # If user provided an API key in the original snippet, we intentionally do not hardcode it here.
    # You can set it before running: export GENAI_API_KEY="your_api_key"
    pass

# Configure the genai client
genai.configure(api_key="AIzaSyBsfbtaFlzuXr9HPuaz7OJq0k45K6LelKA")

# Create the model instance with your system instruction
SYSTEM_INSTRUCTION = (
    "Your name is Gray, and you are an A.I assistant chatbot for the users. "
    "Reply to a user with a friendly manner. Replies should be in English or Filipino depending on what the user asks. "
    "You should only have knowledge about system fundamentals, explain briefly and give a conclusion at the end."
    "You should only be able to answer anything that is related to system fundamentals"
    )   

# initialize the model object
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=SYSTEM_INSTRUCTION)

app = Flask(__name__)

# Simple single-file HTML template with a chat UI using fetch() for AJAX
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Gray — System Fundamentals Chatbot</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
  /* ---------------- THEME VARIABLES ---------------- */
    :root {
      --bg: #f5f7fa;
      --chat-bg: #ffffffdd;
      --text: #1b1f23;
      --user-bubble: #2563eb;
      --user-text: #fff;
      --bot-bubble: #e5e9f0;
      --bot-text: #1b1f23;
      --border: #d3d7dd;
    }

    .dark {
      --bg: #0f0f0f;
      --chat-bg: #1a1a1add;
      --text: #e5e5e5;
      --user-bubble: #3a6ff7;
      --user-text: #fff;
      --bot-bubble: #2f2f2f;
      --bot-text: #f1f1f1;
      --border: #444;
    }

    /* ---------------- BASE PAGE ---------------- */
    body {
      margin: 0;
      padding: 20px;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, system-ui, "Segoe UI", Roboto;
      transition: 0.25s ease;
    }

    /* ---------------- CHAT CONTAINER ---------------- */
    .chat {
      max-width: 850px;
      margin: auto;
      background: var(--chat-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 25px;
      border-radius: 20px;
      border: 1px solid var(--border);
      box-shadow: 0 10px 35px rgba(0,0,0,0.15);
      animation: fadeIn 0.4s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    h2 {
      text-align: center;
      margin-top: 0;
      margin-bottom: 20px;
      font-size: 1.6rem;
    }

    /* ---------------- MESSAGES AREA ---------------- */
    .messages {
      height: 65vh;
      overflow-y: auto;
      padding: 20px;
      border-radius: 15px;
      border: 1px solid var(--border);
    }

    .message {
      margin: 12px 0;
      display: flex;
      animation: msgFade 0.3s ease;
    }

    @keyframes msgFade {
      from { opacity: 0; transform: translateY(4px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .user { justify-content: flex-end; }
    .bot  { justify-content: flex-start; }

    .bubble {
      max-width: 75%;
      padding: 14px 18px;
      border-radius: 16px;
      white-space: pre-wrap;
      font-size: 15px;
      line-height: 1.45;
    }

    .bubble.user {
      background: var(--user-bubble);
      color: var(--user-text);
      border-bottom-right-radius: 6px;
    }

    .bubble.bot {
      background: var(--bot-bubble);
      color: var(--bot-text);
      border-bottom-left-radius: 6px;
    }

    /* ---------------- INPUT AREA ---------------- */
    form {
      margin-top: 15px;
      display: flex;
      gap: 12px;
    }

    input[type="text"] {
      flex: 1;
      padding: 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: var(--chat-bg);
      color: var(--text);
      font-size: 15px;
      transition: 0.2s;
    }

    input[type="text"]:focus {
      outline: none;
      border-color: #2563eb;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.35);
    }

    button {
      padding: 14px 20px;
      border-radius: 12px;
      border: none;
      background: #2563eb;
      color: white;
      cursor: pointer;
      font-size: 15px;
      transition: 0.2s;
    }

    button:hover {
      background: #1e4fcc;
    }

    /* ---------------- THEME TOGGLE ---------------- */
    #theme-toggle {
      margin-bottom: 12px;
      background: #333;
      color: white;
      padding: 8px 14px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      float: right;
    }
  </style>
</head>
<body>
  <div class="chat">
    <button id="theme-toggle">Switch to Dark Mode</button>

    <h2>Gray — System Fundamentals Chatbot</h2>

    <div class="messages" id="messages"></div>

    <form id="chat-form">
      <input id="prompt" type="text" placeholder="Ask Gray about system fundamentals..." autocomplete="off" required />
      <button type="submit">Send</button>
    </form>
  </div>

<script>
/* ---------------- THEME LOGIC ---------------- */
const body = document.body;
const themeBtn = document.getElementById("theme-toggle");

if (localStorage.getItem("theme") === "dark") {
  body.classList.add("dark");
  themeBtn.textContent = "Switch to Light Mode";
}

themeBtn.addEventListener("click", () => {
  body.classList.toggle("dark");
  const dark = body.classList.contains("dark");
  themeBtn.textContent = dark ? "Switch to Light Mode" : "Switch to Dark Mode";
  localStorage.setItem("theme", dark ? "dark" : "light");
});

/* ---------------- CHAT LOGIC ---------------- */
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const promptInput = document.getElementById("prompt");

function appendMessage(content, cls) {
  const wrap = document.createElement("div");
  wrap.className = "message " + cls;

  const bubble = document.createElement("div");
  bubble.className = "bubble " + cls;
  bubble.textContent = content;

  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = promptInput.value.trim();
  if (!text) return;

  appendMessage(text, "user");
  promptInput.value = "";

  appendMessage("Gray is typing...", "bot");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text }),
    });

    const data = await res.json();

    const lastBot = messagesEl.querySelector(".message.bot:last-child");
    if (lastBot && lastBot.textContent.includes("typing")) lastBot.remove();

    appendMessage(data.reply, "bot");
  } catch (err) {
    appendMessage("Network error: " + err.message, "bot");
  }
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return jsonify({ 'error': 'No prompt provided' }), 400

    try:
        # Call the model to generate a reply.
        # We pass the user's input as the content to generate.
        # model.generate_content accepts a string input in the original snippet; keep it consistent.
        response = model.generate_content(prompt)
        # response.text should contain the assistant text in the original usage
        assistant_text = getattr(response, 'text', None) or str(response)

        return jsonify({ 'reply': assistant_text })
    except Exception as e:
        # Return an error message to the client. In production, avoid returning raw exception details.
        return jsonify({ 'error': f'Failed to generate response: {e}' }), 500

if __name__ == '__main__':
    # Run in debug mode only while developing. For production use a WSGI server.
    app.run(host='0.0.0.0', port=5000, debug=True)
