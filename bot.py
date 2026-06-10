import os
from datetime import datetime
from flask import Flask, request
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = os.getenv("RENDER_URL")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def hf_chat(text):

    url = "https://router.huggingface.co/hf-inference/models/microsoft/Phi-3-mini-4k-instruct"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": f"You are a helpful AI assistant.\nUser: {text}\nAssistant:"
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)

        if res.status_code == 200:
            data = res.json()
            return data[0].get("generated_text", "No response")

        return f"HF Error: {res.status_code}"

    except Exception as e:
        return str(e)

answer = hf_chat(text)

bot.send_message(
    chat_id,
    answer[:4000]
)

hour = datetime.now().hour

if hour < 12:
    greeting = "🌅 Good Morning"
elif hour < 17:
    greeting = "☀️ Good Afternoon"
elif hour < 21:
    greeting = "🌇 Good Evening"
else:
    greeting = "🌙 Good Night"
