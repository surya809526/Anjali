import os
import io
import requests
from flask import Flask, request
import telebot
import google.generativeai as genai

# =========================
# ENV VARIABLES
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# =========================
# TELEGRAM BOT
# =========================
bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# GEMINI
# =========================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# FLASK APP
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Anjali AI Bot Running ❤️"

@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()

        webhook_url = f"{RENDER_URL}/webhook"

        bot.set_webhook(url=webhook_url)

        commands = [
            telebot.types.BotCommand("start", "Start Bot"),
            telebot.types.BotCommand("imagine", "Generate AI Image"),
            telebot.types.BotCommand("profile", "View Profile"),
            telebot.types.BotCommand("plan", "Premium Plan")
        ]

        bot.set_my_commands(commands)

        return f"Webhook Set Successfully<br>{webhook_url}"

    except Exception as e:
        return str(e)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_str = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return "ERROR", 500

# =========================
# START
# =========================
@bot.message_handler(commands=["start"])
def start(message):

    text = f"""
👋 Hello {message.from_user.first_name}

💖 Main Anjali hoon

💻 Coding Help
📝 Shayari
📖 Story Writing
🎨 AI Images
🤖 AI Chat

Mujhse baat karo 😊
"""

    bot.reply_to(message, text)

# =========================
# PROFILE
# =========================
@bot.message_handler(commands=["profile"])
def profile(message):

    text = f"""
👤 Name: {message.from_user.first_name}

🆔 User ID: {message.from_user.id}

🤖 Plan: Free
"""

    bot.reply_to(message, text)

# =========================
# PLAN
# =========================
@bot.message_handler(commands=["plan"])
def plan(message):

    bot.reply_to(
        message,
        "💎 Premium Plan Coming Soon!"
    )

# =========================
# IMAGE GENERATION
# =========================
@bot.message_handler(commands=["imagine"])
def imagine(message):

    prompt = message.text.replace("/imagine", "").strip()

    if not prompt:
        bot.reply_to(
            message,
            "🎨 Example:\n/imagine cinematic horse riding scene"
        )
        return

    wait_msg = bot.reply_to(
        message,
        "🎨 Image bana rahi hoon..."
    )

    try:

        HF_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        response = requests.post(
            HF_URL,
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
            image.name = "anjali.png"

            bot.send_photo(
                message.chat.id,
                image,
                caption=f"✨ Prompt:\n{prompt}"
            )

        else:

            bot.reply_to(
                message,
                f"⚠️ HF Error: {response.status_code}"
            )

    except Exception as e:

        bot.reply_to(
            message,
            f"⚠️ Error:\n{e}"
        )

# =========================
# AI CHAT
# =========================
@bot.message_handler(func=lambda m: True)
def chat(message):

    try:

        prompt = f"""
Tum Anjali naam ki friendly female AI assistant ho.

User:
{message.text}
"""

        response = model.generate_content(prompt)

        answer = getattr(
            response,
            "text",
            "Mujhe jawab nahi mila."
        )

        bot.reply_to(
            message,
            answer[:4000]
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"⚠️ Error:\n{e}"
        )

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
        )
