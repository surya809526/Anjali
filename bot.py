import os
from datetime import datetime
from flask import Flask, request
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/")
def home():
    return "Anjali AI Bot Running ❤️"

@app.route("/setup")
def setup():

    webhook_url = f"{os.getenv('RENDER_URL')}/webhook"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    commands = [
        telebot.types.BotCommand("start", "Start Bot"),
        telebot.types.BotCommand("profile", "Profile"),
        telebot.types.BotCommand("help", "Help")
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

            print("MESSAGE:", text)

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
                    f"""
{greeting} ❤️

Main Anjali hoon 💖

💻 Coding Help
📝 Shayari
📖 Story Writing
🤖 AI Chat

Mujhse baat karo 😊
"""
                )

            elif text == "/profile":

                bot.send_message(
                    chat_id,
                    f"""
👤 Name: {update.message.from_user.first_name}

🆔 ID: {update.message.from_user.id}

💎 Plan: Free
"""
                )

            elif text == "/help":

                bot.send_message(
                    chat_id,
                    """
📌 Available Commands

/start
/profile
/help
"""
                )

            else:

                # Simple reply test
                bot.send_message(
                    chat_id,
                    f"🤖 Tumne kaha:\n{text}"
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
