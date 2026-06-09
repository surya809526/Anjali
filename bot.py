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

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print("Webhook Error:", e)
        return "ERROR", 500

# Commands

@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "Friend"

    bot.reply_to(
        message,
        f"""👋 Hello {name}

Main Anjali hoon 💖

✨ Main kya kar sakti hoon?

💻 Coding Help
📝 Shayari
📚 Story Writing
🤖 AI Chat

Commands:
/help
/shayari
/story
/code

Mujhe kuch bhi poochho 😊
"""
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        """
📌 Available Commands

/start - Start Bot
/help - Help
/shayari - Shayari Generate
/story - Story Generate
/code - Coding Help

Ya seedha koi bhi message bhejo.
"""
    )

@bot.message_handler(commands=["shayari"])
def shayari(message):
    try:
        response = model.generate_content(
            "Hindi mein ek emotional aur beautiful shayari likho."
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=["story"])
def story(message):
    try:
        response = model.generate_content(
            "300 words ki ek interesting Hindi story likho."
        )
        bot.reply_to(message, response.text[:4000])
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=["code"])
def code_help(message):
    bot.reply_to(
        message,
        "💻 Apna coding question bhejo, main help karungi."
    )

# Main AI Chat

@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    try:

        user_text = message.text

        prompt = f"""
Tum Anjali naam ki ek friendly female AI assistant ho.

Rules:
- Hindi aur English dono mein baat karo.
- Coding expert ho.
- Shayari likh sakti ho.
- Story likh sakti ho.
- Friendly aur respectful ho.
- Telegram chatbot ho.
- Short aur useful replies do.

User:
{user_text}
"""

        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            bot.reply_to(message, response.text[:4000])
        else:
            bot.reply_to(message, "Response generate nahi hua.")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
