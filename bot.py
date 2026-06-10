import os
from datetime import datetime
from flask import Flask, request
import telebot
import requests
import logging

logging.basicConfig(level=logging.INFO)

# --- TOKENS SPLIT (Strictly Hardcoded) ---
BT_PART1 = "8566767018:AAFjOKeJG0y0gNLjKHR"
BT_PART2 = "7qReetB29MiSVRWc"
BOT_TOKEN = BT_PART1 + BT_PART2

HF_PART1 = "hf_ectbqcRcRDHgfQfjCRLx"
HF_PART2 = "HeZrExVvcjdSYK"
HF_API_KEY = HF_PART1 + HF_PART2

RENDER_URL = "https://anjali-4-nv0n.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Hugging Face Chat Function
def hf_chat(text):
    url = "https://router.huggingface.co/hf-inference/models/microsoft/Phi-3-mini-4k-instruct"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    # Clean template taaki model direct answer de
    payload = {
        "inputs": f"User: {text}\nAssistant:",
        "parameters": {
            "max_new_tokens": 150,
            "return_full_text": False
        }
    }
    try:
        logging.info("Hugging Face ko data bhej rahe hain...")
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        logging.info(f"HF Status Code: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            logging.info(f"HF Raw Response: {data}")
            
            # Har tarah ke response format ko handle karne ke liye safe parsing
            if isinstance(data, list) and len(data) > 0:
                out = data[0].get("generated_text", "").strip()
            elif isinstance(data, dict):
                out = data.get("generated_text", "").strip()
            else:
                out = str(data)
                
            # Agar output mein prompt wapas aa jaye toh use saaf karna
            if "Assistant:" in out:
                out = out.split("Assistant:")[-1].strip()
                
            return out or "Main samajh nahi payi, kripya dobara poochein. 🥺"
            
        elif res.status_code == 503:
            return "🤖 Model abhi start ho raha hai, please 1 minute mein fir se message bhejein!"
            
        return f"HF API Error: {res.status_code}"
    except Exception as e:
        logging.error(f"HF Function Error: {e}")
        return f"Fetch Error: {str(e)}"

# Telegram Message Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        text = message.text or ""
        chat_id = message.chat.id
        logging.info(f"📥 Message Received: {text}")

        # AI Response
        answer = hf_chat(text)
        logging.info(f"🔮 Model Answered: {answer}")

        # Greeting Logic
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
        
        # Ekदम safe send method
        bot.send_message(chat_id, str(final_response)[:4000])
        logging.info("📤 Reply Sent to Telegram Successfully!")
    except Exception as e:
        logging.error(f"Crash in handler: {e}")

# --- FLASK WEBHOOK ROUTES ---
@app.route("/")
def home():
    return "Anjali AI Bot Server is Running! ❤️"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/anjali_webhook"
        status = bot.set_webhook(url=webhook_url)
        return f"Webhook Register Status: {status}"
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
