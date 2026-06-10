import os
import io
from datetime import datetime
import requests
from flask import Flask, request
import telebot
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
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
        telebot.types.BotCommand("imagine", "Generate AI Image"),
        telebot.types.BotCommand("profile", "Profile"),
    ]

    bot.set_my_commands(commands)

    return f"Webhook Set Successfully: {webhook_url}"

@app.route("/webhook", methods=["POST"])
def webhook():

    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)

    bot.process_new_updates([update])

    return "OK", 200


@bot.message_handler(commands=["start"])
def start(message):

    hour = datetime.now().hour

    if hour < 12:
        greeting = "🌅 Good Morning"
    elif hour < 17:
        greeting = "☀️ Good Afternoon"
    elif hour < 21:
        greeting = "🌇 Good Evening"
    else:
        greeting = "🌙 Good Night"

    bot.reply_to(
        message,
        f"""
{greeting} {message.from_user.first_name} ❤️

Main Anjali hoon 💖

💻 Coding Help
📝 Shayari
📖 Story Writing
🎨 AI Images
🤖 AI Chat

Mujhse baat karo 😊
"""
    )

@bot.message_handler(commands=["profile"])
def profile(message):

    bot.reply_to(
        message,
        f"""
👤 Name: {message.from_user.first_name}

🆔 ID: {message.from_user.id}

💎 Plan: Free
"""
    )

@bot.message_handler(commands=["imagine"])
def imagine(message):

    prompt = message.text.replace("/imagine", "").strip()

    if not prompt:
        bot.reply_to(
            message,
            "Example:\n/imagine cinematic horse riding scene"
        )
        return

    try:

        bot.reply_to(
            message,
            "🎨 Image bana rahi hoon..."
        )

        response = requests.post(
            "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers={
                "Authorization": f"Bearer {HF_API_KEY}"
            },
            json={
                "inputs": prompt
            },
            timeout=120
        )

        if response.status_code == 200:

            image = io.BytesIO(response.content)
            image.name = "image.png"

            bot.send_photo(
                message.chat.id,
                image,
                caption=f"✨ Prompt: {prompt}"
            )

        else:

            bot.reply_to(
                message,
                f"HF Error: {response.status_code}"
            )

    except Exception as e:

        bot.reply_to(
            message,
            str(e)
        )

@bot.message_handler(func=lambda m: True)
def chat(message):

    try:

        hour = datetime.now().hour

        if hour < 12:
            greet = "Good Morning"
        elif hour < 17:
            greet = "Good Afternoon"
        elif hour < 21:
            greet = "Good Evening"
        else:
            greet = "Good Night"

        prompt = f"""
You are Anjali, a friendly female AI assistant.

First greet the user with:
{greet}

User:
{message.text}
"""

        response = model.generate_content(prompt)

        answer = getattr(
            response,
            "text",
            "No response generated."
        )

        bot.reply_to(
            message,
            answer[:4000]
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"Error: {e}"
        )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
