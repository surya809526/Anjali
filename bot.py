import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Flask App
app = Flask(__name__)

@app.route("/")
def home():
    return "Anjali AI Bot Running ❤️"

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

    try:

        update = telebot.types.Update.de_json(
            request.get_data().decode("utf-8")
        )

        if update.message:

            chat_id = update.message.chat.id
            text = update.message.text or ""

            print("MESSAGE:", text)

            # Start Command
            if text == "/start":

                bot.send_message(
                    chat_id,
                    """👋 Hello!

Main Anjali hoon 💖

✨ Main kya kar sakti hoon?

💻 Coding Help
📝 Shayari
📚 Story Writing
🤖 AI Chat

Mujhe kuch bhi poochho 😊
"""
                )

            # Help Command
            elif text == "/help":

                bot.send_message(
                    chat_id,
                    """
📌 Available Features

💻 Coding Help
📝 Shayari
📚 Story Writing
🤖 AI Chat

Bas message bhejo aur main jawab dungi.
"""
                )

            # AI Chat
            else:

                prompt = f"""
Tum Anjali naam ki ek friendly female AI assistant ho.

Rules:
- Hindi aur English dono mein baat karo.
- Coding expert ho.
- Shayari likh sakti ho.
- Story likh sakti ho.
- Friendly aur respectful ho.
- Short aur useful replies do.

User:
{text}
"""

                response = model.generate_content(prompt)

                answer = getattr(
                    response,
                    "text",
                    "Response generate nahi hua."
                )

                if not answer:
                    answer = "Response generate nahi hua."

                bot.send_message(
                    chat_id,
                    answer[:4000]
                )

        return "OK", 200

    except Exception as e:

        print("ERROR:", str(e))

        try:
            bot.send_message(
                chat_id,
                f"⚠️ Error:\n{str(e)}"
            )
        except:
            pass

        return "ERROR", 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
