import os
from datetime import datetime
from flask import Flask, request
import telebot
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

@app.route("/")
def home():
    return "Anjali AI Bot Running ❤️"

@app.route("/setup")
def setup():

    webhook_url = f"{RENDER_URL}/webhook"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    commands = [
        telebot.types.BotCommand("start", "Start Bot"),
        telebot.types.BotCommand("help", "Help"),
    ]

    bot.set_my_commands(commands)

    return f"Webhook Set Successfully: {webhook_url}"

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        update = telebot.types.Update.de_json(
            request.get_data().decode("utf-8")
        )

        if update.message:

            chat_id = update.message.chat.id
            text = update.message.text or ""

            if text == "/start":

                hour = datetime.now().hour

                if hour < 12:
                    greeting = "🌅 Good Morning"
                elif hour < 17:
                    greeting = "☀️ Good Afternoon"
                elif hour < 21:
                    greeting = "🌇 Good Evening"
                else:
                    greeting = "🌙 Good Night"

                bot.send_message(
                    chat_id,
                    f"""{greeting} {update.message.from_user.first_name} ❤️

Main Anjali hoon 💖

💻 Coding Help
📝 Shayari
📖 Story Writing
🤖 AI Chat

Mujhse baat karo 😊"""
                )

            else:

                prompt = f"""
Tum Anjali naam ki friendly female AI assistant ho.

Tum:
- Coding karti ho
- Shayari likhti ho
- Stories likhti ho
- Hindi aur English dono samajhti ho

User: {text}
"""

                response = model.generate_content(prompt)

                answer = getattr(
                    response,
                    "text",
                    "Sorry, mujhe response nahi mila."
                )

                bot.send_message(
                    chat_id,
                    answer[:4000]
                )

        return "OK", 200

    except Exception as e:

        print("ERROR:", str(e))
        return "ERROR", 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
        )
