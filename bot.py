import os
import telebot
import google.generativeai as genai

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validation
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found!")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not found!")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception:
    model = genai.GenerativeModel("gemini-1.5-flash")

# Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or "Friend"

    welcome = f"""
👋 Hello {name}

Main tumhari AI Assistant hoon 💖

✨ Main kya kar sakti hoon?

💻 Coding
📝 Shayari
📚 Story Writing
🤖 AI Chat
🎨 Prompt Writing

Bas mujhe message bhejo.
"""

    bot.reply_to(message, welcome)

@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    try:
        user_text = message.text.strip()

        prompt = f"""
Tum ek friendly female AI assistant ho.

User ka message:
{user_text}

Hindi aur English dono mein naturally jawab do.
"""

        response = model.generate_content(prompt)

        answer = ""

        if hasattr(response, "text") and response.text:
            answer = response.text
        else:
            answer = "Sorry, mujhe response generate karne mein problem aa rahi hai."

        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, f"⚠ Error: {str(e)}")

print("✅ Bot Started Successfully")

bot.infinity_polling(skip_pending=True)
