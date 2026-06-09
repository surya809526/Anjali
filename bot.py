import os
import logging
from flask import Flask, request
import google.generativeai as genai
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration (Aapke Tokens)
TOKEN = "8566767018:AAG9eRrbAnfJ1v6O1eer7Dvw_AFddoJFzRU"
GEMINI_KEY = "AIzaSyDG4RvlLGgqYTerYGInGlEUa3lPkz4UAak"
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL") # Render automatic handle karega

# Gemini AI Setup (Anjali Persona)
genai.configure(api_key=GEMINI_KEY)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}
system_instruction = (
    "Aapka naam Anjali hai. Aap ek bohot hi pyaari, samajhdar aur helpful female AI assistant ho. "
    "Aap user se bohot acche aur affectionate tareeke se baat karti ho. Aapka kaam user ke liye coding karna, "
    "pyaari aur gehri shayaris likhna, aur unke har sawaal ka jawab dena hai. Hamesha friendly aur polite raho."
)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

# Flask Server Setup for Render Webhook
app = Flask(__name__)
ptb_application = None

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if ptb_application:
        update = Update.de_json(request.get_json(force=True), ptb_application.bot)
        ptb_application.create_task(ptb_application.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Anjali Bot is running perfectly!", 200

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Command menu setup karna jab user /start kare
    commands = [
        BotCommand("start", "Anjali ko start karein 🚀"),
        BotCommand("profile", "Apna profile dekhein 👤"),
        BotCommand("imagine", "AI Images generate karein 🎨"),
        BotCommand("daily", "Claim Daily Coins 🎁"),
        BotCommand("plan", "Get Unlimited Chat 💎")
    ]
    await context.bot.set_my_commands(commands)
    
    welcome_text = (
        "Hello! Main hoon Anjali. ✨\n\n"
        "Main aapki baatein sunne, aapke liye badiya coding karne aur pyaari shayaris likhne ke liye taiyar hoon. "
        "Bataiye, aaj main aapki kya madad karoon? 💖"
    )
    await update.message.reply_text(welcome_text)

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # Gemini AI se response lena Anjali ke roop mein
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error in Gemini: {e}")
        await update.message.reply_text("Sorry, thoda network issue hai shayad. Ek baar phir se boliye na? 🥺")

# Webhook Initialization
def main_init():
    global ptb_application
    ptb_application = Application.builder().token(TOKEN).build()
    
    ptb_application.add_handler(CommandHandler("start", start))
    ptb_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))
    
    # Webhook set karna Render URL ke sath
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{TOKEN}"
        ptb_application.bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to {webhook_url}")

main_init()
