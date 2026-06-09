import os
import io
import logging
import requests
from flask import Flask, request
import telebot
import google.generativeai as genai

# Logging setup for Render logs
logging.basicConfig(level=logging.INFO)

# --- APKA FRESH NEW TOKEN HARDCODED ---
BOT_TOKEN = "8566767018:AAFjOKeJG0y0gNLjKHR7qReetB29MiSVRWc"

# Baki keys Render se hi load hongi
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
RENDER_URL = "https://anjali-2-cvcf.onrender.com"

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Hugging Face Setup (For AI Images)
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Telegram Bot Instance
bot = telebot.TeleBot(BOT_TOKEN)

# Flask App
app = Flask(__name__)

@app.route("/")
def home():
    return "Anjali AI Bot Running Perfectly! ❤️"

# Automate Menu Buttons and Webhook Setup
@app.route("/setup")
def setup():
    try:
        bot.remove_webhook()
        webhook_url = f"{RENDER_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        
        # Bottom menu ke custom buttons set karna
        commands = [
            telebot.types.BotCommand("start", "Anjali ko start karein 🚀"),
            telebot.types.BotCommand("imagine", "AI Images generate karein 🎨"),
            telebot.types.BotCommand("profile", "Apna profile dekhein 👤"),
            telebot.types.BotCommand("daily", "Claim Daily Coins 🎁"),
            telebot.types.BotCommand("plan", "Get Unlimited Chat 💎")
        ]
        bot.set_my_commands(commands)
        
        return f"Webhook and Menu Commands Set Successfully!<br>{webhook_url}"
    except Exception as e:
        return str(e)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        return "Unsupported Media Type", 403

# --- TELEGRAM BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """👋 Hello!

Main Anjali hoon 💖

✨ Main kya kar sakti hoon?
💻 Coding Help
📝 Shayari
🎨 AI Image Generation (/imagine)
🤖 AI Chat

Bataiye, aaj main aapki kya madad karoon? 😊"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['imagine'])
def generate_image(message):
    prompt = message.text.replace('/imagine', '').strip()
    if not prompt:
        bot.reply_to(message, "Bhai, prompt toh do! Jaise: `/imagine a beautiful cinematic sunset` 🥺")
        return
    
    status_msg = bot.reply_to(message, "Anjali aapke liye image generate kar rahi hai... Please thoda wait karein 🎨✨")
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        if response.status_code == 200:
            image_bytes = response.content
            image_file = io.BytesIO(image_bytes)
            image_file.name = 'anjali_generation.png'
            bot.send_photo(message.chat.id, image_file, caption=f"Aapki image taiyar hai! ✨\nPrompt: {prompt}")
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("Oops! Image generate nahi ho payi. Ek baar phir se try karenge? 💔", message.chat.id, status_msg.message_id)
    except Exception as e:
        logging.error(f"Error in Imagine: {e}")
        bot.edit_message_text("Kuch toh gadbad hui image banane mein.", message.chat.id, status_msg.message_id)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    text = message.text or ""
    chat_id = message.chat.id
    
    prompt = f"Tum Anjali naam ki ek friendly female AI assistant ho. Hindi aur English dono mein short, respectful aur useful replies do.\nUser: {text}"
    try:
        response = model.generate_content(prompt)
        answer = getattr(response, "text", "Response generate nahi hua.")
        bot.send_message(chat_id, answer[:4000])
    except Exception as e:
        logging.error(f"Error in Gemini Chat: {e}")
        bot.send_message(chat_id, "Sorry, thoda network issue hai. Ek baar phir se boliye na? 🥺")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
