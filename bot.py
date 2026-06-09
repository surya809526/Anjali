import os
import logging
import asyncio
import io
import requests
from flask import Flask, request
import google.generativeai as genai
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
HF_KEY = os.environ.get("HF_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

# Hugging Face Config (SDXL Model)
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_KEY}"}

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

# Telegram Application Setup
ptb_application = Application.builder().token(TOKEN).build()

# --- BOT COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        BotCommand("start", "Anjali ko start karein 🚀"),
        BotCommand("imagine", "AI Images generate karein 🎨 (/imagine a cute cat)"),
        BotCommand("profile", "Apna profile dekhein 👤"),
        BotCommand("daily", "Claim Daily Coins 🎁"),
        BotCommand("plan", "Get Unlimited Chat 💎")
    ]
    await context.bot.set_my_commands(commands)
    
    welcome_text = (
        "Hello! Main hoon Anjali. ✨\n\n"
        "Main aapki baatein sunne, aapke liye badiya coding karne aur pyaari shayaris likhne ke liye taiyar hoon. "
        "Agar aapko koi AI image banwani hai, toh `/imagine` command ka use karein!\n\n"
        "Bataiye, aaj main aapki kya madad karoon? 💖"
    )
    await update.message.reply_text(welcome_text)

async def imagine_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check agar user ne prompt diya hai ya nahi
    if not context.args:
        await update.message.reply_text("Bhai, prompt toh do! Jaise: `/imagine a futuristic city, 8k resolution, cinematic lighting` 🥺")
        return

    prompt = " ".join(context.args)
    status_message = await update.message.reply_text("Anjali aapke liye image generate kar rahi hai... Please thoda wait karein 🎨✨")

    try:
        # Hugging Face API Request
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        
        if response.status_code == 200:
            # Image bytes ko memory mein rakh kar Telegram par send karna
            image_bytes = response.content
            image_file = io.BytesIO(image_bytes)
            image_file.name = 'anjali_generation.png'
            
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_file, caption=f"Aapki image taiyar hai! ✨\nPrompt: *{prompt}*", parse_mode="Markdown")
            await status_message.delete()
        else:
            logging.error(f"HF Error: {response.status_code} - {response.text}")
            # Agar model load ho raha ho (Hugging Face pe cold start hota hai kabhi-kabhi)
            if "loading" in response.text:
                await status_message.edit_text("Hugging Face ka model abhi ready ho raha hai, please 1 minute baad fir se try kijiye na? 🥺")
            else:
                await status_message.edit_text("Oops! Image generate nahi ho payi. Ek baar phir se try karenge? 💔")
                
    except Exception as e:
        logging.error(f"Error in Imagine: {e}")
        await status_message.edit_text("Kuch toh gadbad hui image banane mein. Please thoda der baad try karein!")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = model.generate_content(user_message)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error in Gemini: {e}")
        await update.message.reply_text("Sorry, thoda network issue hai shayad. Ek baar phir se boliye na? 🥺")

# Handlers Registration
ptb_application.add_handler(CommandHandler("start", start))
ptb_application.add_handler(CommandHandler("imagine", imagine_handler))
ptb_application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

# --- SERVER LIFECYCLE & WEBHOOK ---

# Secure startup sequence
async def setup_webhook():
    if not ptb_application.running:
        await ptb_application.initialize()
        if RENDER_URL:
            webhook_url = f"{RENDER_URL}/{TOKEN}"
            await ptb_application.bot.set_webhook(url=webhook_url)
            logging.info(f"Webhook connected to: {webhook_url}")
        await ptb_application.start()

# Flask startup trigger
@app.before_all_requests
def run_init_once():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if not ptb_application.running:
        loop.run_until_complete(setup_webhook())

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()
        
    update = Update.de_json(request.get_json(force=True), ptb_application.bot)
    loop.create_task(ptb_application.process_update(update))
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Anjali Bot is active and fully functional!", 200
