import os
from flask import Flask, request
import telebot
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found!")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found!")

if not RENDER_URL:
    raise Exception("RENDER_URL not found!")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is Running!"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        return f"Webhook Set Successfully!<br>{webhook_url}"
    except Exception as e:
        return str(e)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200

    return "Invalid Request", 403

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "Friend"

    bot.reply_to(
        message,
        f"""👋 Hello {name}

Main tumhari AI Assistant hoon 💖

Main:
💻 Coding kar sakti hoon
📝 Shayari likh sakti hoon
🤖 AI Chat kar sakti hoon

Mujhe kuch bhi poochho!
"""
    )

@bot.message_handler(func=lambda m: True)
def chat(message):
    try:
        response = model.generate_content(message.text)

        if hasattr(response, "text") and response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "Mujhe response generate karne mein problem aa rahi hai.")

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
