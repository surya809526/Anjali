import os
import logging
import asyncio
from flask import Flask, request
import google.generativeai as genai
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Gemini AI Setup
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

# Flask Application
app = Flask(__name__)

# Telegram Application initialize (bina loop block kiye)
ptb_application = Application.builder().token(TOKEN).build()

# Commands & Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error in Gemini: {e}")
        await update.message.reply_text("Sorry, thoda network issue hai shayad. Ek baar phir se boliye na? 🥺")

# Handlers register karna
ptb_application.add_handler(CommandHandler("start", start))
ptb_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

# Flask context ke andar async init script
@app.before_all_requests
def initialize_bot_service():
    """Ensure bot is initialized once inside Gunicorn's worker context"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if not ptb_application.updater and not ptb_application.running:
        logging.info("Initializing Telegram Bot Application securely...")
        loop.run_until_complete(ptb_application.initialize())
        if RENDER_URL:
            webhook_url = f"{RENDER_URL}/{TOKEN}"
            loop.run_until_complete(ptb_application.bot.set_webhook(url=webhook_url))
            logging.info(f"Webhook set successfully to {webhook_url}")
        loop.run_until_complete(ptb_application.start())

# Flask Routes
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    if ptb_application:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
            
        update = Update.de_json(request.get_json(force=True), ptb_application.bot)
        loop.create_task(ptb_application.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Anjali Bot is running perfectly!", 200
