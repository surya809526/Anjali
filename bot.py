import os
from datetime import datetime
from flask import Flask, request
import telebot
import requests
import logging

# Logging set kiya taaki Render dashboard par activity saaf dikhe
logging.basicConfig(level=logging.INFO)

# --- APKI CONFIGURATIONS ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = "https://anjali-4-nv0n.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Hugging Face Chat Function
def hf_chat(text):
    url = "https://router.huggingface.co/hf-inference/models/microsoft/Phi-3-mini-4k-instruct"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    payload = {
        "inputs": f"<|user|>\n{text}<|end|>\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 250,
            "return_full_text": False
        }
    }
    
    try:
        logging.info(f"Hugging Face ko request bhej rahe hain: {text}")
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        
        logging.info(f"Hugging Face API Status Code: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            logging.info(f"Hugging Face Raw Data: {data}")
            
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "").strip() or "Model ne khali response diya bhai! 😮"
            elif isinstance(data, dict):
                return data.get("generated_text", "").strip() or "Model ne khali response diya bhai! 😮"
            return "Response format thoda ajeeb hai."
        
        elif res.status_code == 503:
            return "Hugging Face model abhi load ho raha hai, please 1 minute baad fir se try karein! 😴"
            
        return f"HF API Error Status: {res.status_code}"
    except Exception as e:
        return f"Fetch Error: {str(e)}"

# Telegram Message Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        text = message.text or ""
        chat_id = message.chat.id
        logging.info(f"Telegram se naya message aaya: {text} | Chat ID: {chat_id}")

        # 1. Hugging Face Se Response Lena
        answer = hf_chat(text)

        # 2. Greeting Logic
        hour = datetime.now().hour
        if hour < 12:
            greeting = "🌅 Good Morning"
        elif hour < 17:
            greeting = "☀️ Good Afternoon"
        elif hour < 21:
            greeting = "🌇 Good Evening"
        else:
            greeting = "🌙 Good Night"

        final_response = f"{greeting}\n\n{answer}"
        
        # 3. Message Bhejna
        bot.send_message(chat_id, final_response[:4000])
        logging.info("Message successfully user ko bhej diya gaya!")
        
    except Exception as e:
        logging.error(f"Handler ke andar crash hua: {e}")

# --- FLASK WEBHOOK ROUTES ---
@app.route("/")
def home():
    return "Anjali AI Bot Server is Running Perfectly! ❤️"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        # Naya unique route lagaya taaki stuck webhook clear ho jaye
        webhook_url = f"{RENDER_URL}/anjali_webhook"
        bot.set_webhook(url=webhook_url)
        return f"Webhook Clean Route Set Successfully!<br>{webhook_url}"
    except Exception as e:
        return str(e)

@app.route("/anjali_webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
