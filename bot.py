import os
import logging
import telebot
import requests
from flask import Flask, request
from datetime import datetime, timezone, timedelta

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- ENV VARIABLES ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL")  # e.g. https://anjali-4-nv0n.onrender.com

# --- INIT ---
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- IST TIMEZONE ---
IST = timezone(timedelta(hours=5, minutes=30))

# --- POLLINATIONS AI CHAT FUNCTION ---
def hf_chat(user_message: str) -> str:
    try:
        system = "You are Anjali, a friendly and helpful AI assistant. Speak warmly and concisely."
        prompt = f"{system}\n\nUser: {user_message}\nAnjali:"

        encoded = requests.utils.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}"

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            return response.text.strip()
        else:
            logging.error(f"Pollinations Error: {response.status_code}")
            return "Kuch samajh nahi aaya, dobara poochho! 😊"

    except requests.exceptions.Timeout:
        logging.error("Pollinations Timeout!")
        return "Response aane mein thoda time lag raha hai, retry karo! ⏳"
    except Exception as e:
        logging.error(f"hf_chat Error: {e}")
        return "Kuch technical issue aa gaya, baad mein try karo! 🔧"


# --- MESSAGE HANDLER ---
def handle_message(chat_id: int, text: str):
    try:
        logging.info(f"📥 Message Received: {text}")

        # AI Response
        answer = hf_chat(text)
        logging.info(f"🔮 Model Answered: {answer}")

        # Greeting Logic (IST time)
        hour = datetime.now(IST).hour
        if hour < 12:
            greeting = "🌅 Good Morning"
        elif hour < 17:
            greeting = "☀️ Good Afternoon"
        elif hour < 21:
            greeting = "🌇 Good Evening"
        else:
            greeting = "🌙 Good Night"

        final_response = f"{greeting}!\n\n{answer}"

        # Safe send
        bot.send_message(chat_id, str(final_response)[:4000])
        logging.info("📤 Reply Sent to Telegram Successfully!")

    except Exception as e:
        logging.error(f"Crash in handle_message: {e}")
        try:
            bot.send_message(chat_id, "Oops! Kuch gadbad ho gayi. Dobara try karo 🙏")
        except:
            pass


# --- FLASK ROUTES ---
@app.route("/")
def home():
    return "Anjali AI Bot Server is Running! ❤️"


@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/anjali_webhook"
        status = bot.set_webhook(url=webhook_url)
        return f"Webhook Register Status: {status} ✅"
    except Exception as e:
        return f"Setup Error: {str(e)}"


@app.route("/anjali_webhook", methods=["POST"])
def webhook():
    try:
        json_data = request.get_json(force=True)
        if not json_data:
            return "No data", 400

        update = telebot.types.Update.de_json(json_data)

        if update.message and update.message.text:
            chat_id = update.message.chat.id
            text = update.message.text.strip()
            handle_message(chat_id, text)

        return "OK", 200

    except Exception as e:
        logging.error(f"Webhook Error: {e}")
        return "Error", 500


# --- MAIN ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
