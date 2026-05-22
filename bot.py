import telebot
import time
import random
import string

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8694782952:AAFSaRBRE2cPNXSRQAeFdu3A4UNdgyVI2Sw"
ADMIN_ID = 5798647399

bot = telebot.TeleBot(TOKEN)

def count_lines(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return len(f.readlines())
    except:
        return 0

def generate_key():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(10))

@bot.message_handler(commands=['start'])
def start(message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = KeyboardButton("📂 Generate Files")
    btn2 = KeyboardButton("📊 My Statistics")
    btn3 = KeyboardButton("🔥 Buy Key")
    btn4 = KeyboardButton("ℹ️ Help & Info")

    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)

    codm = count_lines("codm.txt")
    roblox = count_lines("roblox.txt")
    ml = count_lines("ml.txt")

    total = codm + roblox + ml

    text = f"""
📊 Total Available: {total} lines
📄 Per Generation: 700 lines
🔄 Auto-Delete: Lines removed after generation
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


@bot.message_handler(commands=['redeem'])
def redeem(message):

    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(message, "Usage:\n/redeem YOUR_KEY")
        return

    user_key = args[1]

    try:
        with open("keys.txt", "r") as f:
            keys = f.readlines()
    except:
        bot.reply_to(message, "❌ No keys database found.")
        return

    found = False

    for line in keys:

        data = line.strip().split("|")

        saved_key = data[0]
        duration = data[1]

        if user_key == saved_key:

            found = True

            with open("users.txt", "a") as u:
                u.write(f"{message.from_user.id}|{duration}\n")

            remaining_keys = []

            for k in keys:
                if not k.startswith(saved_key):
                    remaining_keys.append(k)

            with open("keys.txt", "w") as f:
                f.writelines(remaining_keys)

            bot.reply_to(
                message,
                f"""
✅ Key Redeemed Successfully

⏳ Duration: {duration}
👤 User ID: {message.from_user.id}
"""
            )

            break

    if not found:
        bot.reply_to(message, "❌ Invalid or used key.")



@bot.message_handler(commands=['genkey'])
def genkey(message):

    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Admin only.")
        return

    args = message.text.split()

    if len(args) < 2:
        bot.reply_to(
            message,
            "Usage:\n/genkey 1d\n/genkey 7d\n/genkey 30d\n/genkey lifetime"
        )
        return

    duration = args[1].lower()

    if duration not in ["1d", "7d", "30d", "lifetime"]:
        bot.reply_to(message, "❌ Invalid duration.")
        return

    key = "KEY-" + generate_key()

    with open("keys.txt", "a") as f:
        f.write(f"{key}|{duration}\n")

    bot.reply_to(
        message,
        f"""
🔑 Key Generated

🗝 Key: {key}
⏳ Duration: {duration}
"""
    )

@bot.message_handler(func=lambda message: True)
def buttons(message):

    if message.text == "📂 Generate Files":

        markup = ReplyKeyboardMarkup(resize_keyboard=True)

        b1 = KeyboardButton("🎮 Codm")
        b2 = KeyboardButton("🟢 Roblox")
        b3 = KeyboardButton("🔥 ML")

        markup.row(b1, b2)
        markup.row(b3)

        bot.send_message(
            message.chat.id,
            "📂 Choose generator:",
            reply_markup=markup
        )








    elif message.text == "🎮 Codm":

        with open("codm.txt", "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            bot.reply_to(message, "❌ No more Codm accounts.")
            return

        generated = lines[:700]
        remaining = lines[700:]

        with open("result_codm.txt", "w") as f:
            f.writelines(generated)

        with open("codm.txt", "w") as f:
            f.writelines(remaining)

        bot.send_document(
            message.chat.id,
            open("result_codm.txt", "rb"),
            caption="🎮 Codm Accounts Generated"
        )

    elif message.text == "🟢 Roblox":

        with open("roblox.txt", "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            bot.reply_to(message, "❌ No more Roblox accounts.")
            return

        generated = lines[:700]
        remaining = lines[700:]

        with open("result_roblox.txt", "w") as f:
            f.writelines(generated)

        with open("roblox.txt", "w") as f:
            f.writelines(remaining)

        bot.send_document(
            message.chat.id,
            open("result_roblox.txt", "rb"),
            caption="🟢 Roblox Accounts Generated"
        )

    elif message.text == "🔥 ML":

        with open("ml.txt", "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            bot.reply_to(message, "❌ No more ML accounts.")
            return

        generated = lines[:700]
        remaining = lines[700:]

        with open("result_ml.txt", "w") as f:
            f.writelines(generated)

        with open("ml.txt", "w") as f:
            f.writelines(remaining)

        bot.send_document(
            message.chat.id,
            open("result_ml.txt", "rb"),
            caption="🔥 ML Accounts Generated"
        )


    elif message.text == "📊 My Statistics":
        bot.reply_to(message, "📊 No statistics yet.")

    elif message.text == "🔥 Buy Key":
        bot.reply_to(message, "🔥 Contact admin to buy a key.")

    elif message.text == "ℹ️ Help & Info":
        bot.reply_to(message, "ℹ️ Premium generator bot.")

print("Bot is running...")
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(e)
        time.sleep(5)




