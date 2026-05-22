import telebot
from flask import Flask
from threading import Thread
import os

TOKEN = os.geten("8694782952:AAFSaRBRE2cPNXSRQAeFdu3A4UNdgyVI2Sw"

bot = telebot.TeleBot(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start(message):

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = telebot.types.KeyboardButton("📦 Generate")
    btn2 = telebot.types.KeyboardButton("💰 Balance")
    btn3 = telebot.types.KeyboardButton("➕ Add Balance")
    btn4 = telebot.types.KeyboardButton("📜 History")

    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)

    bot.send_message(
        message.chat.id,
        "🔥 Welcome to your Premium Bot!",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda m: True)
def buttons(message):

    if message.text == "📦 Generate":
        bot.reply_to(message, "Generator coming soon.")

    elif message.text == "💰 Balance":
        bot.reply_to(message, "Your balance: ₱0")

    elif message.text == "➕ Add Balance":
        bot.reply_to(message, "Payment system coming soon.")

    elif message.text == "📜 History":
        bot.reply_to(message, "No history yet.")

keep_alive()

print("Bot is running...")

bot.infinity_polling(timeout=30, long_polling_timeout=10)
