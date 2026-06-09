import os
from flask import Flask, request
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found!")

if not RENDER_URL:
    raise Exception("RENDER_URL not found!")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is Running!"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()

        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"

        result = bot.set_webhook(url=webhook_url)

        return f"""
Webhook Set Successfully<br>
Result: {result}<br>
URL: {webhook_url}
"""
    except Exception as e:
        return str(e)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():

    print("🔥 MESSAGE RECEIVED FROM TELEGRAM")

    try:

        json_string = request.get_data().decode("utf-8")

        print(json_string)

        update = telebot.types.Update.de_json(json_string)

        if update.message:

            chat_id = update.message.chat.id
            text = update.message.text

            print("CHAT ID:", chat_id)
            print("MESSAGE:", text)

            if text == "/start":

                bot.send_message(
                    chat_id,
                    "👋 Hello! Main tumhari AI Assistant hoon 💖"
                )

            else:

                bot.send_message(
                    chat_id,
                    f"✅ Webhook Working\n\nTumne likha: {text}"
                )

        return "OK", 200

    except Exception as e:

        print("ERROR:", str(e))

        return str(e), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
                )
