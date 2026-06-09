import os
import telebot
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

# Purana webhook remove karo
bot.remove_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Main tumhari AI Assistant hoon 💖")

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

print("✅ Bot Started Successfully")

bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
)
