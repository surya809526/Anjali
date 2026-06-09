import os
import telebot
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        f"""👋 Hello {message.from_user.first_name}

Main tumhari AI Assistant hoon 💖

Main:
💻 Coding kar sakti hoon
📝 Shayari likh sakti hoon
💬 Chat kar sakti hoon
"""
    )

@bot.message_handler(func=lambda m: True)
def chat(message):

    prompt = f"""
Tum ek friendly female AI assistant ho.

User:
{message.text}
"""

    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

print("Bot Started...")
bot.infinity_polling()
