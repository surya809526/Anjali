import os
import io
import requests
from flask import Flask, request
import telebot
import google.generativeai as genai

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

# Telegram
bot = telebot.TeleBot(BOT_TOKEN)

# Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Hugging Face Image API
HF_IMAGE_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

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
        telebot.types.BotCommand("imagine", "Generate AI Image")
    ]

    bot.set_my_commands(commands)

    return f"Webhook Set: {webhook_url}"

@app.route("/webhook", methods=["POST"])
def webhook():

    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )

    if update.message:

        chat_id = update.message.chat.id
        text = update.message.text or ""

        try:

            # START
            if text == "/start":

                bot.send_message(
                    chat_id,
                    """
👋 Hello!

Main Anjali hoon 💖

💻 Coding Help
📝 Shayari
📚 Story
🎨 AI Images
🤖 AI Chat

Mujhse baat karo 😊
"""
                )

            # HELP
            elif text == "/help":

                bot.send_message(
                    chat_id,
                    """
Commands:

/start
/help
/imagine prompt
"""
                )

            # IMAGE
            elif text.startswith("/imagine"):

                prompt = text.replace(
                    "/imagine",
                    ""
                ).strip()

                if not prompt:
                    bot.send_message(
                        chat_id,
                        "Prompt do 😊"
                    )

                else:

                    bot.send_message(
                        chat_id,
                        "🎨 Image bana rahi hoon..."
                    )

                    response = requests.post(
                        HF_IMAGE_URL,
                        headers=HF_HEADERS,
                        json={"inputs": prompt},
                        timeout=120
                    )

                    if response.status_code == 200:

                        image = io.BytesIO(
                            response.content
                        )

                        image.name = "image.png"

                        bot.send_photo(
                            chat_id,
                            image
                        )

                    else:

                        bot.send_message(
                            chat_id,
                            "Image generate nahi hui."
                        )

            # GEMINI CHAT
            else:

                prompt = f"""
Tum Anjali naam ki friendly female AI assistant ho.

Hindi aur English dono mein baat karo.

User:
{text}
"""

                response = model.generate_content(
                    prompt
                )

                answer = getattr(
                    response,
                    "text",
                    "No response"
                )

                bot.send_message(
                    chat_id,
                    answer[:4000]
                )

        except Exception as e:

            print("ERROR:", e)

            bot.send_message(
                chat_id,
                f"⚠️ {e}"
            )

    return "OK", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
