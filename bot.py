import os
from datetime import datetime
from flask import Flask, request
import telebot
import requests

# Tokens and Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Hugging Face Chat Function
def hf_chat(text):
    url = "https://router.huggingface.co/hf-inference/models/microsoft/Phi-3-mini-4k-instruct"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    payload = {
        "inputs": f"You are a helpful AI assistant.\nUser: {text}\nAssistant:"
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            raw_text = data[0].get("generated_text", "No response")
            # Prompt ko response se saaf karne ke liye split
            if "Assistant:" in raw_text:
                return raw_text.split("Assistant:")[-1].strip()
            return raw_text
        return f"HF Error: {res.status_code}"
    except Exception as e:
        return str(e)

# --- GLOBAL VARIABLES SE HATAKAR TELEGRAM HANDLER MEIN DAAL DIYA ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text or ""
    chat_id = message.chat.id

    # 1. AI Se Response Lena
    answer = hf_chat(text)

    # 2. Aapka Greeting Logic
    hour = datetime.now().hour
    if hour < 12:
        greeting = "🌅 Good Morning"
    elif hour < 17:
        greeting = "☀️ Good Afternoon"
    elif hour < 21:
        greeting = "🌇 Good Evening"
    else:
        greeting = "🌙 Good Night"

    # 3. Greeting ke saath message bhejna
    final_response = f"{greeting}\n\n{answer}"
    
    bot.send_message(
        chat_id,
        final_response[:4000]
    )

# --- FLASK WEBHOOK ROUTES FOR RENDER ---
@app.route("/")
def home():
    return "Bot Server is Running! 🚀"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        return "Webhook Set Successfully!"
    except Exception as e:
        return str(e)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
