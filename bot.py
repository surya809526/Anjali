import os
from datetime import datetime
from flask import Flask, request
import telebot
import requests
import logging

# Logging set kiya taaki Render dashboard par errors saaf dikhein
logging.basicConfig(level=logging.INFO)

# --- APKI CONFIGURATIONS (BINA BADLAV KE) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = "https://anjali-4-nv0n.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Hugging Face Chat Function (Phi-3 Model Support)
def hf_chat(text):
    url = "https://router.huggingface.co/hf-inference/models/microsoft/Phi-3-mini-4k-instruct"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    # Model ko sahi context dene ke liye strict prompt template
    payload = {
        "inputs": f"<|user|>\n{text}<|end|>\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 250,
            "return_full_text": False
        }
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            # Hugging face list return karta hai, usme se clean text nikalna
            if isinstance(data, list) and len(data) > 0:
                raw_text = data[0].get("generated_text", "No response")
                return raw_text.strip()
            elif isinstance(data, dict):
                return data.get("generated_text", "No response").strip()
            return "Khabar nahi mili model se."
        
        # Agar model abhi load ho raha ho (503 error)
        elif res.status_code == 503:
            return "Hugging Face model abhi jag raha hai, please 1 minute baad fir se message bhejiye! 😴"
            
        return f"HF API Error: {res.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Telegram Message Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text or ""
    chat_id = message.chat.id

    # 1. Hugging Face Se Response Lena
    answer = hf_chat(text)

    # 2. Aapka Exact Greeting Logic
    hour = datetime.now().hour
    if hour < 12:
        greeting = "🌅 Good Morning"
    elif hour < 17:
        greeting = "☀️ Good Afternoon"
    elif hour < 21:
        greeting = "🌇 Good Evening"
    else:
        greeting = "🌙 Good Night"

    # 3. Final Format Me Message Bhejna
    final_response = f"{greeting}\n\n{answer}"
    
    try:
        bot.send_message(chat_id, final_response[:4000])
    except Exception as e:
        logging.error(f"Message send karne me error: {e}")

# --- FLASK WEBHOOK ROUTES ---
@app.route("/")
def home():
    return "Anjali AI Bot Server is Running Perfectly! ❤️"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        return f"Webhook Set Successfully to: {webhook_url}"
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
