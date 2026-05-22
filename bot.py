
import telebot
from flask import Flask
from threading import Thread
import os
import random
import string
from telebot.types import ReplyKeyboardMarkup, KeyboardButt


import os

TOKEN = os.getenv("BOT_TOKEN")


try:
    with open("keys.txt", "r") as f:
        keys = f.read().splitlines()
except:
    keys = []

try:
    with open("users.txt", "r") as f:
        approved_users = list(map(int, f.read().splitlines()))
except:
    approved_users = []

ADMIN_ID = 5798647399

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("Generate File"))
    kb.add(KeyboardButton("My Statistics"))

    bot.send_message(
        message.chat.id,
        "Welcome to Zver0x Premium Bot",
        reply_markup=kb
    )



@bot.message_handler(func=lambda m: m.text == "Generate File")
def generate_menu(message):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("CODM"))
    kb.add(KeyboardButton("ML"))
    kb.add(KeyboardButton("Roblox"))
    kb.add(KeyboardButton("Netflix"))
    kb.add(KeyboardButton("Back"))

    bot.send_message(
        message.chat.id,
        "Choose a file:",
        reply_markup=kb
    )



@bot.message_handler(func=lambda m: m.text == "Back")
def back(message):

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add(KeyboardButton("Generate File"))
    kb.add(KeyboardButton("My Statistics"))

    bot.send_message(
        message.chat.id,
        "Main Menu",
        reply_markup=kb
    )



@bot.message_handler(func=lambda m: m.text == "CODM")
def codm(message):

    text = "CODM FILE"

    with open("codm.txt", "w") as f:
        f.write(text)

    with open("codm.txt", "rb") as f:
        bot.send_document(message.chat.id, f)



@bot.message_handler(func=lambda m: m.text == "ML")
def ml(message):

    text = "ML FILE"

    with open("ml.txt", "w") as f:
        f.write(text)

    with open("ml.txt", "rb") as f:
        bot.send_document(message.chat.id, f)




@bot.message_handler(func=lambda m: m.text == "Generate File")
def generate(message):

    if message.from_user.id not in approved_users:
        bot.send_message(
            message.chat.id,
            "🔒 You need a key first.\nUse: /key YOURKEY"
        )
        return

    text = "Hello from your bot"

    with open("output.txt", "w") as f:
        f.write(text)

    with open("output.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(func=lambda m: m.text == "My Statistics")
def stats(message):

    bot.send_message(
        message.chat.id,
        "📊 Statistics\n\nUsers: 1\nFiles Generated: 0"
    )


def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


@bot.message_handler(commands=['genkey'])
def genkey(message):

    if message.from_user.id != ADMIN_ID:
        return

    key = generate_key()

    keys.append(key)

    with open("keys.txt", "a") as f:
        f.write(key + "\n")

    bot.send_message(
        message.chat.id,
        f"🔑 New Key:\n\n{key}"
    )


@bot.message_handler(commands=['key'])
def redeem(message):

    try:
        user_key = message.text.split()[1]

    except:
        bot.send_message(
            message.chat.id,
            "Usage: /key YOURKEY"
        )
        return

    if user_key in keys:

        approved_users.append(message.from_user.id)

        with open("users.txt", "a") as f:
            f.write(str(message.from_user.id) + "\n")

        keys.remove(user_key)

        bot.send_message(
            message.chat.id,
            "✅ Access Approved"
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Invalid Key"
        )

app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))


def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()

bot.infinity_polling(
    timeout=30,
    long_polling_timeout=10
)
=======
import os
import json
import random
import asyncio
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from telegram.error import BadRequest

TOKEN = "8651022857:AAHlDvqCRc2uo5f2MCROx757qFM4tg0SY-U"
ADMIN_IDS = [5446268639]
KEYS_FILE = "keys.json"
USED_ACCOUNTS_FILE = "used_accounts.txt"
DATABASE_FILES = [str(path) for path in Path("/storage/emulated/0/Bot/database/").glob("*.txt")] if os.path.exists("/storage/emulated/0/Bot/database/") else []
LOGS_DIR = Path("/storage/emulated/0/Bot/logs/")
SAVE_DIR = Path("./Results/")
SAVE_DIR.mkdir(parents=True, exist_ok=True)
REFERRAL_FILE = "referrals.json"
WHITELIST_FILE = "whitelist.json"
COINS_FILE = "coins.json"
QUIZ_FILE = "quiz.json"
STYLES_FILE = "styles.json"

DEFAULT_KEY_GEN_LIMIT = 100
MAX_KEY_GEN_LIMIT = 300
ACCOUNTS_PER_REQUEST = 200
WORKERS = 5
ANTI_SPAM = {}
REQUIRED_SHARES = 5

DOMAINS = ["100082", "100054", "ssogarena", "authgop", "garena"]
def load_keys():
    try:
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"keys": {}, "user_keys": {}, "logs": {}, "antispam": {}}

def load_referrals():
    try:
        if os.path.exists(REFERRAL_FILE):
            with open(REFERRAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"pending": {}, "approved": {}}

def load_whitelist():
    try:
        if os.path.exists(WHITELIST_FILE):
            with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"users": []}

def load_coins():
    try:
        if os.path.exists(COINS_FILE):
            with open(COINS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def load_quiz():
    try:
        if os.path.exists(QUIZ_FILE):
            with open(QUIZ_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {"questions": [], "active": False, "prize": 10}

def load_styles():
    try:
        if os.path.exists(STYLES_FILE):
            with open(STYLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_keys(data):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_referrals(data):
    with open(REFERRAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_whitelist(data):
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_coins(data):
    with open(COINS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_quiz(data):
    with open(QUIZ_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_styles(data):
    with open(STYLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

keys_data = load_keys()
referral_data = load_referrals()
whitelist_data = load_whitelist()
coins_data = load_coins()
quiz_data = load_quiz()
styles_data = load_styles()

def generate_random_key(length=5):
    return "Jirobns-" + ''.join(random.choices("0123456789", k=length))

def parse_duration(duration_str):
    total_seconds = 0
    time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    matches = re.findall(r'(\d+)([dhms])', duration_str.lower())
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]
    return total_seconds if matches else None

def get_expiry_time(duration_str):
    if duration_str.lower() == "lifetime":
        return None
    seconds = parse_duration(duration_str)
    if not seconds:
        return None
    return (datetime.now() + timedelta(seconds=seconds)).timestamp()

async def apply_style(update: Update, style_name: str):
    if style_name not in THEMES:
        return False
    
    styles_data[str(update.effective_user.id)] = style_name
    save_styles(styles_data)
    return True

async def start(update: Update, context: CallbackContext):
    user_style = styles_data.get(str(update.effective_user.id), "default")
    
    keyboard = [
        [InlineKeyboardButton("✨ Redeem Key ✨", callback_data="redeem_key"),
         InlineKeyboardButton("🎁 Generate 🎁", callback_data="generate_menu")],
        [InlineKeyboardButton("📚 Help 📚", callback_data="help"),
         InlineKeyboardButton("📈 Stats 📈", callback_data="stats")],
        [InlineKeyboardButton("💌 Support 💌", callback_data="support"),
         InlineKeyboardButton("👥 Friends 👥", callback_data="friends")],
        [InlineKeyboardButton("💰 Price List 💰", callback_data="price_list"),
         InlineKeyboardButton("🔍 Search Accounts 🔍", callback_data="search_accounts")],
        [InlineKeyboardButton("🤝 Referral Program", callback_data="referral_program")],
        [InlineKeyboardButton("🎮 Quiz Game", callback_data="quiz_command")]
    ]
    if update.effective_user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("👑 Admin Panel 👑", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = {
        "default": "🌟 *Welcome to Jiro Bot!* 🌟\n\n🔥 *Premium Accounts Generator*\n⚡ *Fast & Reliable Service*\n💎 *Best Quality Accounts*",
        "dark": "🌑 *Welcome to Jiro Dark Mode!* 🌑\n\n🔥 *Premium Accounts in the Dark*\n⚡ *Stealthy & Efficient*\n💎 *Exclusive Dark Deals*",
        "light": "🌞 *Welcome to Jiro Light Mode!* 🌞\n\n🔥 *Premium Accounts Made Bright*\n⚡ *Clear & Fast Service*\n💎 *Shining Quality*",
        "neon": "🌈 *Welcome to Jiro Neon Mode!* 🌈\n\n🔥 *Glowing Premium Accounts*\n⚡ *Electrifying Speed*\n💎 *Vibrant Quality*",
        "vintage": "📻 *Welcome to Jiro Vintage Mode!* 📻\n\n🔥 *Classic Premium Accounts*\n⚡ *Retro Speed*\n💎 *Timeless Quality*"
    }.get(user_style, "🌟 *Welcome to Jiro Premium Bot!* 🌟\n\n🔥 *Premium Accounts Generator*\n⚡ *Fast & Reliable Service*\n💎 *Best Quality Accounts*")

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        try:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def generate_menu(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if chat_id not in keys_data["user_keys"] and chat_id not in whitelist_data["users"]:
        if update.message:
            await update.message.reply_text("🔒 You need a valid key to access premium features!")
        elif update.callback_query:
            try:
                await update.callback_query.edit_message_text("🔒 You need a valid key to access premium features!")
            except BadRequest:
                await update.callback_query.message.reply_text("🔒 You need a valid key to access premium features!")
        return

    expiry = keys_data["user_keys"].get(chat_id)
    if expiry is not None and datetime.now().timestamp() > expiry and chat_id not in whitelist_data["users"]:
        del keys_data["user_keys"][chat_id]
        save_keys(keys_data)
        if update.message:
            await update.message.reply_text("⌛ Your key has expired! Renew it to continue.")
        elif update.callback_query:
            try:
                await update.callback_query.edit_message_text("⌛ Your key has expired! Renew it to continue.")
            except BadRequest:
                await update.callback_query.message.reply_text("⌛ Your key has expired! Renew it to continue.")
        return

    keyboard = [[InlineKeyboardButton(f"🌐 {domain}", callback_data=f"generate_{domain}")] for domain in DOMAINS]
    keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("🛠 *Premium Account Generator*\n\nSelect a domain to generate premium accounts:", reply_markup=reply_markup, parse_mode="Markdown")
    else:
        try:
            await update.callback_query.edit_message_text("🛠 *Premium Account Generator*\n\nSelect a domain to generate premium accounts:", reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text("🛠 *Premium Account Generator*\n\nSelect a domain to generate premium accounts:", reply_markup=reply_markup, parse_mode="Markdown")

async def generate_filtered_accounts(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    chat_id, selected_domain = str(query.message.chat_id), query.data.replace("generate_", "")
    
    if chat_id not in keys_data["user_keys"] and chat_id not in whitelist_data["users"]:
        try:
            return await query.edit_message_text("🔒 Premium access required!")
        except BadRequest:
            return await query.message.reply_text("🔒 Premium access required!")

    expiry = keys_data["user_keys"].get(chat_id)
    if expiry is not None and datetime.now().timestamp() > expiry and chat_id not in whitelist_data["users"]:
        del keys_data["user_keys"][chat_id]
        save_keys(keys_data)
        try:
            return await query.edit_message_text("⌛ Your premium access has expired!")
        except BadRequest:
            return await query.message.reply_text("⌛ Your premium access has expired!")

    if check_spam(chat_id) and chat_id not in whitelist_data["users"]:
        try:
            return await query.edit_message_text("🚫 Too many requests! Please wait before generating again.")
        except BadRequest:
            return await query.message.reply_text("🚫 Too many requests! Please wait before generating again.")

    try:
        processing_msg = await query.message.reply_text("⚡ *Processing Your Request...*\n\n⏳ Gathering premium accounts...\n🔍 Filtering best quality...\n✨ Almost done...", parse_mode="Markdown")
    except:
        return

    try:
        with open(USED_ACCOUNTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            used_accounts = set(f.read().splitlines())
    except:
        used_accounts = set()

    matched_lines = []
    seen_accounts = set()
    for db_file in DATABASE_FILES:
        if len(matched_lines) >= ACCOUNTS_PER_REQUEST and chat_id not in whitelist_data["users"]:
            break
        try:
            with open(db_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip():
                        continue
                    if ":" not in line:
                        continue
                    parts = line.strip().split(":", 1)
                    if len(parts) != 2:
                        continue
                    username, password = parts
                    account_line = f"{username}:{password}"
                    if selected_domain.lower() in line.lower() and account_line not in used_accounts and account_line not in seen_accounts:
                        matched_lines.append(account_line)
                        seen_accounts.add(account_line)
                        if len(matched_lines) >= ACCOUNTS_PER_REQUEST and chat_id not in whitelist_data["users"]:
                            break
        except Exception as e:
            continue

    if not matched_lines:
        return await processing_msg.edit_text("⚠️ *No Premium Accounts Available*\n\nWe couldn't find any premium accounts for this domain.\nTry again later or contact support!", parse_mode="Markdown")

    try:
        with open(USED_ACCOUNTS_FILE, "a", encoding="utf-8", errors="ignore") as f:
            f.write("\n".join(matched_lines) + "\n")
    except:
        pass

    filename = f"PREMIUM {selected_domain} {datetime.now().strftime('%Y-%m-%d')}.txt"
    try:
        with open(filename, "w", encoding="utf-8", errors="ignore") as f:
            f.write(f"🔥 Premium Accounts Generated By Jiro Bot\n")
            f.write(f"📅 Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🌐 Domain: {selected_domain}\n")
            f.write(f"🔢 Accounts Count: {len(matched_lines)}\n\n")
            f.write("\n".join(matched_lines))
    except:
        return await processing_msg.edit_text("❌ *Error Creating File*\n\nThere was an issue preparing your accounts.\nPlease try again or contact support!", parse_mode="Markdown")

    await asyncio.sleep(2)
    try:
        await processing_msg.delete()
    except:
        pass
    
    try:
        with open(filename, "rb") as f:
            await query.message.reply_document(
                document=InputFile(f, filename=filename),
                caption=f"🔵 *Premium Accounts Generated Successfully!*\n\n🌐 Domain: `{selected_domain}`\n🔢 Accounts: `{len(matched_lines)}`\n📅 Date: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n💎 Thank you for using Jiro Premium Service!",
                parse_mode="Markdown"
            )
    except Exception as e:
        await query.message.reply_text(f"❌ *Error Sending File*\n\nError details: `{str(e)}`\nPlease contact support!", parse_mode="Markdown")
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

async def generate_key(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")

    if len(context.args) < 1:
        return await update.message.reply_text("🔑 *Key Generation*\n\nUsage: `/genkey <duration> [limit]`\nExample: `/genkey 2d3h 100`\n\n⏳ Duration examples:\n• 7d - 7 days\n• 1h - 1 hour\n• 30m - 30 minutes\n• lifetime - No expiration", parse_mode="Markdown")

    duration = context.args[0]
    limit = int(context.args[1]) if len(context.args) > 1 else 1

    if limit > DEFAULT_KEY_GEN_LIMIT:
        return await update.message.reply_text(f"⚠ *Key Generation Limit*\n\nMaximum limit is {DEFAULT_KEY_GEN_LIMIT} keys for this command!\nUse /keygenlimit for larger batches", parse_mode="Markdown")

    keys = []
    for _ in range(limit):
        new_key = generate_random_key()
        expiry = get_expiry_time(duration)
        keys_data["keys"][new_key] = expiry
        keys.append(new_key)

    save_keys(keys_data)

    await update.message.reply_text(f"🎉 *Key Generation Successful!*\n\n🔑 Generated Keys: `{limit}`\n⏳ Expiration: `{duration}`\n\nHere are your keys:\n`{'`\n`'.join(keys)}`\n\n📌 Share these with your users!", parse_mode="Markdown")

async def keygen_limit(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")

    if len(context.args) < 2:
        return await update.message.reply_text("🔑 *Bulk Key Generation*\n\nUsage: `/keygenlimit <duration> <limit>`\nExample: `/keygenlimit 7d 500`\n\n⏳ Duration examples:\n• 7d - 7 days\n• 1h - 1 hour\n• 30m - 30 minutes\n• lifetime - No expiration", parse_mode="Markdown")

    duration = context.args[0]
    try:
        limit = int(context.args[1])
    except ValueError:
        return await update.message.reply_text("❌ Invalid limit! Please provide a number.", parse_mode="Markdown")

    if limit > MAX_KEY_GEN_LIMIT:
        return await update.message.reply_text(f"⚠ *Key Generation Limit*\n\nMaximum limit is {MAX_KEY_GEN_LIMIT} keys at once!", parse_mode="Markdown")

    keys = []
    for _ in range(limit):
        new_key = generate_random_key()
        expiry = get_expiry_time(duration)
        keys_data["keys"][new_key] = expiry
        keys.append(new_key)

    save_keys(keys_data)

    await update.message.reply_text(f"🎉 *Bulk Key Generation Successful!*\n\n🔑 Total Keys Generated: `{limit}`\n⏳ Expiration: `{duration}`\n\nHere are first 50 keys:\n`{'`\n`'.join(keys[:50])}`\n\n📌 Keys saved to database!", parse_mode="Markdown")

async def redeem_key(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)

    if len(context.args) != 1:
        return await update.message.reply_text("🔑 *Redeem Premium Key*\n\nUsage: `/key <your_key>`\n\nObtain a key from our support to access premium features!", parse_mode="Markdown")

    entered_key = context.args[0]

    if entered_key not in keys_data["keys"]:
        return await update.message.reply_text("❌ *Invalid Key*\n\nThe key you entered is invalid or has expired.\nContact support for a valid key!", parse_mode="Markdown")

    expiry = keys_data["keys"][entered_key]
    if expiry is not None and datetime.now().timestamp() > expiry:
        del keys_data["keys"][entered_key]
        save_keys(keys_data)
        return await update.message.reply_text("⌛ *Expired Key*\n\nThis key has already expired.\nContact support for a new key!", parse_mode="Markdown")

    keys_data["user_keys"][chat_id] = expiry
    del keys_data["keys"][entered_key]
    save_keys(keys_data)

    expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
    await update.message.reply_text(f"🎉 *Premium Access Activated!*\n\n🔑 Key Redeemed Successfully!\n⏳ Expiration: `{expiry_text}`\n\n✨ Now you can access premium features!\nUse /generate to start getting accounts!", parse_mode="Markdown")

async def view_logs(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")

    if not keys_data["user_keys"]:
        return await update.message.reply_text("📂 *No Active Users*\n\nNo users have redeemed keys yet.", parse_mode="Markdown")

    log_text = "📋 *Premium Users Log*\n\n"
    for user, expiry in keys_data["user_keys"].items():
        expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
        log_text += f"👤 User ID: `{user}`\n⏳ Expires: `{expiry_text}`\n\n"

    await update.message.reply_text(log_text, parse_mode="Markdown")

async def key_info_all(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("😈 Admin access required!")

    if not keys_data["keys"]:
        return await update.message.reply_text("📂 *No Keys Available*\n\nNo keys currently in the database.", parse_mode="Markdown")

    active_keys = []
    expired_keys = []
    current_time = datetime.now().timestamp()
    
    for key, expiry in keys_data["keys"].items():
        if expiry is None or expiry > current_time:
            expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
            active_keys.append(f"🔑 `{key}` - ⏳ Expires: `{expiry_text}`")
        else:
            expired_keys.append(f"🔑 `{key}` - ❌ Expired")

    message_text = "🔑 *Keys Database Summary*\n\n"
    message_text += f"✅ *Active Keys ({len(active_keys)})*\n" + "\n".join(active_keys[:50]) + "\n\n"
    message_text += f"❌ *Expired Keys ({len(expired_keys)})*\n" + "\n".join(expired_keys[:50]) + "\n\n"
    
    if len(active_keys) > 50 or len(expired_keys) > 50:
        message_text += "⚠ Showing first 50 keys in each category. Use /logs for full details."

    await update.message.reply_text(message_text, parse_mode="Markdown")

async def admin_panel(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        if update.message:
            await update.message.reply_text("😈 Admin access required!")
        elif update.callback_query:
            try:
                await update.callback_query.answer("😈 Admin access required!")
            except BadRequest:
                pass
        return
    
    keyboard = [
        [InlineKeyboardButton("🔑 Generate Keys", callback_data="admin_genkey"),
         InlineKeyboardButton("📊 View Logs", callback_data="admin_logs")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="admin_restart"),
         InlineKeyboardButton("📈 Bot Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🧹 Clear Database", callback_data="admin_clear"),
         InlineKeyboardButton("⏱ Anti-Spam", callback_data="admin_antispam")],
        [InlineKeyboardButton("🔑 Key Management", callback_data="admin_keymgmt"),
         InlineKeyboardButton("📤 Export Data", callback_data="admin_export")],
        [InlineKeyboardButton("📝 Referral Approvals", callback_data="admin_referrals")],
        [InlineKeyboardButton("👥 Whitelist Users", callback_data="admin_whitelist")],
        [InlineKeyboardButton("🎮 Quiz Management", callback_data="admin_quiz")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("😈 *Admin Control Panel* 😈\n\nManage all bot functions from here:", reply_markup=reply_markup, parse_mode="Markdown")
    else:
        try:
            await update.callback_query.edit_message_text("😈 *Admin Control Panel* 👑\n\nManage all bot functions from here:", reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text("👑 *Admin Control Panel* 👑\n\nManage all bot functions from here:", reply_markup=reply_markup, parse_mode="Markdown")

async def restart_bot(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("😈 Admin access required!")
    
    await update.message.reply_text("🔄 *Bot Restarting...*\n\nThe bot will be back online shortly!", parse_mode="Markdown")
    os.execl(sys.executable, sys.executable, *sys.argv)

async def clear_database(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")
    
    try:
        open(USED_ACCOUNTS_FILE, "w").close()
        await update.message.reply_text("✅ *Database Cleared Successfully!*\n\nThe used accounts database has been reset.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ *Database Clear Error*\n\nError: `{str(e)}`", parse_mode="Markdown")

async def bot_stats(update: Update, context: CallbackContext):
    total_users = len(keys_data["user_keys"])
    active_users = sum(1 for expiry in keys_data["user_keys"].values() 
                      if expiry is None or datetime.now().timestamp() < expiry)
    
    stats_text = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 Users:\n"
        f"• Total: `{total_users}`\n"
        f"• Active: `{active_users}`\n\n"
        f"🔑 Keys:\n"
        f"• Available: `{len(keys_data['keys'])}`\n\n"
        f"💾 Database:\n"
        f"• Files: `{len(DATABASE_FILES)}`\n"
        f"• Workers: `{WORKERS}`\n"
        f"• Accounts/Request: `{ACCOUNTS_PER_REQUEST}`\n\n"
        f"🤝 Referrals:\n"
        f"• Pending: `{len(referral_data.get('pending', {}))}`\n"
        f"• Approved: `{len(referral_data.get('approved', {}))}`\n\n"
        f"👥 Whitelist:\n"
        f"• Users: `{len(whitelist_data.get('users', []))}`\n\n"
        f"🪙 Coins System:\n"
        f"• Total Users: `{len(coins_data)}`\n\n"
        f"🎮 Quiz System:\n"
        f"• Questions: `{len(quiz_data.get('questions', []))}`\n"
        f"• Active: `{'Yes' if quiz_data.get('active', False) else 'No'}`\n\n"
        f"🛡 Security:\n"
        f"• Anti-Spam: `{'Active' if keys_data.get('antispam') else 'Inactive'}`\n"
        f"• Version: `2.5 Premium`"
    )
    
    if update.message:
        await update.message.reply_text(stats_text, parse_mode="Markdown")
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(stats_text, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(stats_text, parse_mode="Markdown")

async def set_antispam(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")

    if len(context.args) < 1:
        return await update.message.reply_text("⏱ *Anti-Spam Settings*\n\nUsage: `/antispam <duration>`\nExample: `/antispam 10s`\n\nDuration examples:\n• 5s - 5 seconds\n• 1m - 1 minute\n• 2h - 2 hours", parse_mode="Markdown")

    duration = context.args[0]
    seconds = parse_duration(duration)
    if not seconds:
        return await update.message.reply_text("❌ *Invalid Duration Format*\n\nPlease use format like: 5s, 1m, 2h", parse_mode="Markdown")

    keys_data["antispam"] = {duration: seconds}
    save_keys(keys_data)
    ANTI_SPAM.clear()
    await update.message.reply_text(f"✅ *Anti-Spam Activated!*\n\n⏳ Cooldown: `{duration}`", parse_mode="Markdown")

async def revoke_antispam(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("🔒 Admin access required!")

    if "antispam" not in keys_data or not keys_data["antispam"]:
        return await update.message.reply_text("ℹ️ *Anti-Spam Status*\n\nNo active anti-spam settings to revoke.", parse_mode="Markdown")

    keys_data["antispam"] = {}
    save_keys(keys_data)
    ANTI_SPAM.clear()
    await update.message.reply_text("✅ *Anti-Spam Revoked!*\n\nUsers can now make unlimited requests.", parse_mode="Markdown")

async def revoke_key(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("😈 Admin access required!")

    if len(context.args) != 1:
        return await update.message.reply_text("🔑 *Revoke User Key*\n\nUsage: `/revokekey <user_id>`", parse_mode="Markdown")

    user_id = context.args[0]
    if user_id not in keys_data["user_keys"]:
        return await update.message.reply_text("❌ *User Not Found*\n\nThis user doesn't have an active key.", parse_mode="Markdown")

    del keys_data["user_keys"][user_id]
    save_keys(keys_data)
    await update.message.reply_text(f"✅ *Key Revoked!*\n\nUser `{user_id}` no longer has premium access.", parse_mode="Markdown")

async def export_data(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("😈 Admin access required!")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ziaabot_export_{timestamp}.json"
    
    export_data = {
        "keys": keys_data["keys"],
        "user_keys": keys_data["user_keys"],
        "referrals": referral_data,
        "whitelist": whitelist_data,
        "coins": coins_data,
        "quiz": quiz_data,
        "styles": styles_data
    }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4)
        
        with open(filename, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=filename),
                caption=f"📤 *Bot Data Export*\n\nExported on: `{timestamp}`"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ *Export Failed*\n\nError: `{str(e)}`")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def manage_referrals(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        if update.callback_query:
            try:
                await update.callback_query.answer("🔒 Admin access required!")
            except BadRequest:
                pass
        return

    pending = referral_data["pending"]
    if not pending:
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.callback_query.edit_message_text(
            "📝 *Referral Approvals*\n\nNo pending referrals to approve.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    keyboard = []
    for user_id, details in pending.items():
        keyboard.append([
            InlineKeyboardButton(
                f"✅ Approve {user_id}",
                callback_data=f"approve_ref_{user_id}"
            ),
            InlineKeyboardButton(
                f"❌ Reject {user_id}",
                callback_data=f"reject_ref_{user_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📝 *Referral Approvals*\n\nPending referrals:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def approve_referral(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    query = update.callback_query
    user_id = query.data.replace("approve_ref_", "")
    
    if user_id not in referral_data["pending"]:
        try:
            await query.answer("Referral already processed!")
        except BadRequest:
            pass
        return await manage_referrals(update, context)

    referral_data["approved"][user_id] = referral_data["pending"][user_id]
    del referral_data["pending"][user_id]
    save_referrals(referral_data)

    referrer_id = referral_data["approved"][user_id]["referrer"]
    if str(referrer_id) not in coins_data:
        coins_data[str(referrer_id)] = 0
    coins_data[str(referrer_id)] += 5
    save_coins(coins_data)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 *Your Referral Was Approved!*\n\nYou now have access to premium features!"
        )
    except:
        pass

    try:
        await query.answer("Referral approved!")
    except BadRequest:
        pass
    
    await manage_referrals(update, context)

async def reject_referral(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    query = update.callback_query
    user_id = query.data.replace("reject_ref_", "")
    
    if user_id not in referral_data["pending"]:
        try:
            await query.answer("Referral already processed!")
        except BadRequest:
            pass
        return await manage_referrals(update, context)

    del referral_data["pending"][user_id]
    save_referrals(referral_data)

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ *Your Referral Was Rejected*\n\nPlease try again with valid shares."
        )
    except:
        pass

    try:
        await query.answer("Referral rejected!")
    except BadRequest:
        pass
    
    await manage_referrals(update, context)

async def whitelist_menu(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        if update.callback_query:
            try:
                await update.callback_query.answer("🔒 Admin access required!")
            except BadRequest:
                pass
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add User", callback_data="whitelist_add")],
        [InlineKeyboardButton("➖ Remove User", callback_data="whitelist_remove")],
        [InlineKeyboardButton("👥 View Whitelist", callback_data="whitelist_view")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                "👥 *Whitelist Management*\n\nManage users who have permanent access:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except BadRequest:
            await update.callback_query.message.reply_text(
                "👥 *Whitelist Management*\n\nManage users who have permanent access:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

async def whitelist_add_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if update.callback_query:
        try:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "👤 *Add to Whitelist*\n\nPlease reply with the user ID to whitelist:",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_whitelist_add"] = True
        except BadRequest:
            pass

async def whitelist_remove_user(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not whitelist_data["users"]:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="whitelist_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.callback_query.edit_message_text(
            "👤 *Remove from Whitelist*\n\nNo users in whitelist.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    keyboard = []
    for user_id in whitelist_data["users"]:
        keyboard.append([InlineKeyboardButton(
            f"➖ Remove {user_id}",
            callback_data=f"whitelist_remove_{user_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="whitelist_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "👤 *Remove from Whitelist*\n\nSelect user to remove:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def whitelist_view_users(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not whitelist_data["users"]:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="whitelist_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.callback_query.edit_message_text(
            "👥 *Whitelisted Users*\n\nNo users in whitelist.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    users_list = "\n".join(f"• `{user_id}`" for user_id in whitelist_data["users"])
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="whitelist_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"👥 *Whitelisted Users*\n\n{users_list}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def process_whitelist_add(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    user_id = update.message.text.strip()
    if not user_id.isdigit():
        await update.message.reply_text("❌ Invalid user ID! Please provide numeric ID.")
        return

    if user_id in whitelist_data["users"]:
        await update.message.reply_text("ℹ️ User is already whitelisted!")
        return

        whitelist_data["users"].append(user_id)
    save_whitelist(whitelist_data)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Whitelist", callback_data="whitelist_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ User `{user_id}` added to whitelist!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    context.user_data.pop("awaiting_whitelist_add", None)

async def process_whitelist_remove(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    query = update.callback_query
    user_id = query.data.replace("whitelist_remove_", "")
    
    if user_id not in whitelist_data["users"]:
        try:
            await query.answer("User not in whitelist!")
        except BadRequest:
            pass
        return await whitelist_remove_user(update, context)

    whitelist_data["users"].remove(user_id)
    save_whitelist(whitelist_data)

    try:
        await query.answer("User removed from whitelist!")
    except BadRequest:
        pass
    
    await whitelist_remove_user(update, context)

async def quiz_management(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        if update.callback_query:
            try:
                await update.callback_query.answer("🔒 Admin access required!")
            except BadRequest:
                pass
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add Question", callback_data="quiz_add")],
        [InlineKeyboardButton("➖ Remove Question", callback_data="quiz_remove")],
        [InlineKeyboardButton("📝 View Questions", callback_data="quiz_view")],
        [InlineKeyboardButton("✅ Toggle Active", callback_data="quiz_toggle")],
        [InlineKeyboardButton("💰 Set Prize", callback_data="quiz_prize")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "🟢 ACTIVE" if quiz_data["active"] else "🔴 INACTIVE"
    await update.callback_query.edit_message_text(
        f"🎮 *Quiz Management*\n\nStatus: {status}\n"
        f"Questions: {len(quiz_data['questions'])}\n"
        f"Prize: {quiz_data.get('prize', 10)} coins",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def quiz_add_question(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if update.callback_query:
        try:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "📝 *Add Quiz Question*\n\nPlease reply with the question in this format:\n"
                "`Question?|Option1|Option2|Option3|Option4|CorrectAnswer`\n\n"
                "Example:\n`What is 2+2?|3|4|5|6|4`",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_quiz_add"] = True
        except BadRequest:
            pass

async def quiz_remove_question(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not quiz_data["questions"]:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="quiz_management")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.callback_query.edit_message_text(
            "📝 *Remove Quiz Question*\n\nNo questions available.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    keyboard = []
    for i, question in enumerate(quiz_data["questions"], 1):
        keyboard.append([InlineKeyboardButton(
            f"➖ Q{i}: {question['question'][:20]}...",
            callback_data=f"quiz_remove_{i-1}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="quiz_management")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "📝 *Remove Quiz Question*\n\nSelect question to remove:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def quiz_view_questions(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if not quiz_data["questions"]:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="quiz_management")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.callback_query.edit_message_text(
            "📝 *Quiz Questions*\n\nNo questions available.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    questions_text = ""
    for i, question in enumerate(quiz_data["questions"], 1):
        options = "\n".join(f"• {opt}" for opt in question["options"])
        questions_text += (
            f"🔹 *Question {i}*\n"
            f"❓ {question['question']}\n"
            f"📋 Options:\n{options}\n"
            f"✅ Correct: {question['correct']}\n\n"
        )
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="quiz_management")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"📝 *Quiz Questions*\n\n{questions_text}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def quiz_toggle_active(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    quiz_data["active"] = not quiz_data["active"]
    save_quiz(quiz_data)
    
    status = "🟢 ACTIVATED" if quiz_data["active"] else "🔴 DEACTIVATED"
    try:
        await update.callback_query.answer(f"Quiz {status.lower()}!")
    except BadRequest:
        pass
    
    await quiz_management(update, context)

async def quiz_set_prize(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    if update.callback_query:
        try:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "💰 *Set Quiz Prize*\n\nPlease reply with the coin amount for correct answers:",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_quiz_prize"] = True
        except BadRequest:
            pass

async def process_quiz_add(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    parts = update.message.text.split("|")
    if len(parts) < 6:
        await update.message.reply_text(
            "❌ Invalid format! Use:\n"
            "`Question?|Option1|Option2|Option3|Option4|CorrectAnswer`",
            parse_mode="Markdown"
        )
        return

    question = {
        "question": parts[0].strip(),
        "options": [opt.strip() for opt in parts[1:5]],
        "correct": parts[5].strip()
    }
    
    quiz_data["questions"].append(question)
    save_quiz(quiz_data)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Quiz", callback_data="quiz_management")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✅ Question added successfully!",
        reply_markup=reply_markup
    )
    context.user_data.pop("awaiting_quiz_add", None)

async def process_quiz_remove(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    query = update.callback_query
    index = int(query.data.replace("quiz_remove_", ""))
    
    if 0 <= index < len(quiz_data["questions"]):
        del quiz_data["questions"][index]
        save_quiz(quiz_data)
    
    try:
        await query.answer("Question removed!")
    except BadRequest:
        pass
    
    await quiz_remove_question(update, context)

async def process_quiz_prize(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMIN_IDS:
        return

    try:
        prize = int(update.message.text.strip())
        if prize <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid amount! Please enter a positive number.")
        return

    quiz_data["prize"] = prize
    save_quiz(quiz_data)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Quiz", callback_data="quiz_management")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Quiz prize set to {prize} coins!",
        reply_markup=reply_markup
    )
    context.user_data.pop("awaiting_quiz_prize", None)

async def quiz_command(update: Update, context: CallbackContext):
    if not quiz_data["active"]:
        try:
            await update.callback_query.answer("Quiz is currently inactive!", show_alert=True)
        except BadRequest:
            pass
        return

    user_id = str(update.effective_user.id)
    if user_id in context.user_data.get("quiz_participants", {}):
        try:
            await update.callback_query.answer("You already participated in this quiz!", show_alert=True)
        except BadRequest:
            pass
        return

    if not quiz_data["questions"]:
        try:
            await update.callback_query.answer("No questions available!", show_alert=True)
        except BadRequest:
            pass
        return

    question = random.choice(quiz_data["questions"])
    options = question["options"].copy()
    random.shuffle(options)
    
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"quiz_answer_{opt}")] for opt in options]
    keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data.setdefault("quiz_questions", {})[user_id] = question
    
    try:
        await update.callback_query.edit_message_text(
            f"🎮 *Quiz Time!*\n\n❓ {question['question']}\n\n"
            f"💰 Prize: {quiz_data['prize']} coins",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except BadRequest:
        await update.callback_query.message.reply_text(
            f"🎮 *Quiz Time!*\n\n❓ {question['question']}\n\n"
            f"💰 Prize: {quiz_data['prize']} coins",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def quiz_answer(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    if user_id in context.user_data.get("quiz_participants", {}):
        try:
            await query.answer("You already participated in this quiz!", show_alert=True)
        except BadRequest:
            pass
        return

    selected_answer = query.data.replace("quiz_answer_", "")
    question = context.user_data.get("quiz_questions", {}).get(user_id)
    
    if not question:
        try:
            await query.answer("Quiz session expired!", show_alert=True)
        except BadRequest:
            pass
        return

    context.user_data.setdefault("quiz_participants", {})[user_id] = True
    
    if selected_answer == question["correct"]:
        coins_data.setdefault(user_id, 0)
        coins_data[user_id] += quiz_data["prize"]
        save_coins(coins_data)
        
        try:
            await query.edit_message_text(
                f"✅ *Correct Answer!*\n\nYou won {quiz_data['prize']} coins!\n\n"
                f"💰 Total coins: {coins_data[user_id]}\n\n"
                f"🔙 /back_to_main",
                parse_mode="Markdown"
            )
        except BadRequest:
            await query.message.reply_text(
                f"✅ *Correct Answer!*\n\nYou won {quiz_data['prize']} coins!\n\n"
                f"💰 Total coins: {coins_data[user_id]}\n\n"
                f"🔙 /back_to_main",
                parse_mode="Markdown"
            )
    else:
        try:
            await query.edit_message_text(
                f"❌ *Wrong Answer!*\n\nThe correct answer was: {question['correct']}\n\n"
                f"🔙 /back_to_main",
                parse_mode="Markdown"
            )
        except BadRequest:
            await query.message.reply_text(
                f"❌ *Wrong Answer!*\n\nThe correct answer was: {question['correct']}\n\n"
                f"🔙 /back_to_main",
                parse_mode="Markdown"
            )

async def referral_program(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    referral_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
    
    pending = referral_data["pending"].get(user_id, {"shares": 0})["shares"]
    approved = user_id in referral_data["approved"]
    
    status = "✅ APPROVED" if approved else f"🔄 PENDING ({pending}/{REQUIRED_SHARES})"
    
    text = (
        f"🤝 *Referral Program*\n\n"
        f"🔗 Your referral link:\n`{referral_link}`\n\n"
        f"📊 Status: {status}\n"
        f"📌 Requirements:\n"
        f"• Share your link with {REQUIRED_SHARES} friends\n"
        f"• They must join and use /start with your link\n\n"
        f"🎁 Reward: 5 coins for each approved referral"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
                        await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def process_referral(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if len(context.args) == 1 and context.args[0].startswith("ref_"):
        referrer_id = context.args[0][4:]
        
        if referrer_id == user_id:
            return await update.message.reply_text("❌ You can't refer yourself!")
            
        if user_id in referral_data["pending"] or user_id in referral_data["approved"]:
            return
            
        if referrer_id not in referral_data["pending"]:
            referral_data["pending"][referrer_id] = {
                "referrals": [],
                "shares": 0
            }
            
        if user_id not in referral_data["pending"][referrer_id]["referrals"]:
            referral_data["pending"][referrer_id]["referrals"].append(user_id)
            referral_data["pending"][referrer_id]["shares"] += 1
            save_referrals(referral_data)
            
            if referral_data["pending"][referrer_id]["shares"] >= REQUIRED_SHARES:
                referral_data["approved"][referrer_id] = referral_data["pending"][referrer_id]
                del referral_data["pending"][referrer_id]
                save_referrals(referral_data)
                
                if referrer_id not in coins_data:
                    coins_data[referrer_id] = 0
                coins_data[referrer_id] += 5
                save_coins(coins_data)
                
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 *Referral Approved!*\n\nYou've earned 5 coins! Your total: {coins_data[referrer_id]}",
                        parse_mode="Markdown"
                    )
                except:
                    pass

async def coins_balance(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    balance = coins_data.get(user_id, 0)
    
    text = (
        f"💰 *Your Coin Balance*\n\n"
        f"🪙 Total coins: {balance}\n\n"
        f"💎 Earn coins by:\n"
        f"• Participating in quizzes (/quiz)\n"
        f"• Referring friends (/referral)\n"
        f"• Daily bonuses (/daily)"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def daily_bonus(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_id not in coins_data:
        coins_data[user_id] = 0
    
    last_claim = keys_data.get("logs", {}).get(user_id, {}).get("last_daily_claim")
    if last_claim == today:
        await update.message.reply_text("❌ You've already claimed your daily bonus today!")
        return
    
    bonus = random.randint(1, 5)
    coins_data[user_id] += bonus
    
    keys_data.setdefault("logs", {}).setdefault(user_id, {})["last_daily_claim"] = today
    save_keys(keys_data)
    save_coins(coins_data)
    
    await update.message.reply_text(
        f"🎉 *Daily Bonus Claimed!*\n\n"
        f"💰 You received: {bonus} coins\n"
        f"🪙 New balance: {coins_data[user_id]}",
        parse_mode="Markdown"
    )

async def search_accounts(update: Update, context: CallbackContext):
    if update.callback_query:
        try:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                "🔍 *Account Search*\n\nPlease reply with the username or email to search for:",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_search"] = True
        except BadRequest:
            pass

async def process_search(update: Update, context: CallbackContext):
    search_term = update.message.text.strip().lower()
    if not search_term:
        await update.message.reply_text("❌ Please provide a search term!")
        return
    
    with open(USED_ACCOUNTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        used_accounts = set(f.read().splitlines())
    
    matched_lines = []
    for db_file in DATABASE_FILES:
        try:
            with open(db_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip():
                        continue
                    if ":" not in line:
                        continue
                    username = line.split(":")[0].strip().lower()
                    if search_term in username and line.strip() not in used_accounts:
                        matched_lines.append(line.strip())
        except:
            continue
    
    if not matched_lines:
        await update.message.reply_text(
            f"❌ No accounts found matching: `{search_term}`",
            parse_mode="Markdown"
        )
        return
    
    filename = f"SEARCH_{search_term[:20]}_{datetime.now().strftime('%Y%m%d')}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"🔍 Search results for: {search_term}\n")
            f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n".join(matched_lines))
        
        with open(filename, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=filename),
                caption=f"🔍 *Search Results*\n\nFound {len(matched_lines)} accounts matching: `{search_term}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
    
    context.user_data.pop("awaiting_search", None)

async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "ℹ️ *Jiro Premium Bot Help*\n\n"
        "🔑 *Key Commands:*\n"
        "/key <code> - Redeem premium key\n"
        "/generate - Generate premium accounts\n\n"
        "🪙 *Coin Commands:*\n"
        "/coins - Check your balance\n"
        "/daily - Claim daily bonus\n"
        "/referral - Get referral link\n\n"
        "🎮 *Fun Commands:*\n"
        "/quiz - Participate in quiz game\n\n"
        "🔍 *Search Commands:*\n"
        "/search - Find specific accounts\n\n"
        "🛠 *Admin Commands:*\n"
        "/genkey - Generate premium keys\n"
        "/logs - View active users\n"
        "/revokekey - Revoke user access\n\n"
        "Need help? Contact @@Jirobns"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
                        await update.callback_query.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")

async def support_command(update: Update, context: CallbackContext):
    support_text = (
        "💌 *Support Information*\n\n"
        "For any issues or questions, please contact:\n"
        "👤 Admin: @@Jirobns\n"
        "📢 Channel: @Jirobns\n\n"
        "⚠️ *Important:*\n"
        "• Don't share your keys with others\n"
        "• Report any bugs immediately\n"
        "• Follow our channel for updates"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(support_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(support_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(support_text, reply_markup=reply_markup, parse_mode="Markdown")

async def price_list(update: Update, context: CallbackContext):
    prices_text = (
        "💰 *Premium Plans*\n\n"
        "🔑 *Key Durations:*\n"
        "• 1 Day - 10 Coins\n"
        "• 7 Days - 50 Coins\n"
        "• 30 Days - 200 Coins\n"
        "• Lifetime - 500 Coins\n\n"
        "🛒 *How to Buy:*\n"
        "1. Earn coins (/coins)\n"
        "2. Contact @Jirobns\n"
        "3. Get your premium key!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🪙 Earn Coins", callback_data="coins_balance")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(prices_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(prices_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
                await update.message.reply_text(prices_text, reply_markup=reply_markup, parse_mode="Markdown")

async def stats_command(update: Update, context: CallbackContext):
    total_users = len(keys_data["user_keys"])
    active_users = sum(1 for expiry in keys_data["user_keys"].values() 
                      if expiry is None or datetime.now().timestamp() < expiry)
    
    stats_text = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 Users:\n"
        f"• Total: {total_users}\n"
        f"• Active: {active_users}\n\n"
        f"🪙 Coins System:\n"
        f"• Total Users: {len(coins_data)}\n"
        f"• Total Coins: {sum(coins_data.values())}\n\n"
        f"🎮 Quiz System:\n"
        f"• Questions: {len(quiz_data['questions'])}\n"
        f"• Active: {'Yes' if quiz_data['active'] else 'No'}\n\n"
        f"🛡 Security:\n"
        f"• Anti-Spam: {'Active' if keys_data.get('antispam') else 'Inactive'}\n"
        f"• Version: 2.5 Premium"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")

async def friends_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    referrals = []
    
    for ref_user_id, details in referral_data["pending"].items():
        if user_id in details["referrals"]:
            referrals.append(ref_user_id)
    
    for ref_user_id, details in referral_data["approved"].items():
        if user_id in details["referrals"]:
            referrals.append(ref_user_id)
    
    if not referrals:
        friends_text = "👥 *Friends*\n\nYou haven't referred any friends yet. Use /referral to get your link!"
    else:
        friends_text = "👥 *Friends*\n\nYou've referred these users:\n" + "\n".join(f"• `{user}`" for user in referrals)
    
    keyboard = [
        [InlineKeyboardButton("🤝 Get Referral Link", callback_data="referral_program")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(friends_text, reply_markup=reply_markup, parse_mode="Markdown")
        except BadRequest:
            await update.callback_query.message.reply_text(friends_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(friends_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    try:
        await query.answer()
    except BadRequest:
        pass
    
    if data == "back_to_main":
        await start(update, context)
    elif data == "redeem_key":
        await query.edit_message_text(
            "🔑 *Redeem Premium Key*\n\nPlease use the command:\n`/key <your_key>`\n\nto redeem your premium access.",
            parse_mode="Markdown"
        )
    elif data == "generate_menu":
        await generate_menu(update, context)
    elif data.startswith("generate_"):
        await generate_filtered_accounts(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data == "stats":
        await stats_command(update, context)
    elif data == "support":
        await support_command(update, context)
    elif data == "friends":
        await friends_command(update, context)
    elif data == "price_list":
        await price_list(update, context)
    elif data == "search_accounts":
        await search_accounts(update, context)
    elif data == "referral_program":
        await referral_proprogram(update, context)
    elif data == "quiz_command":
        await quiz_command(update, context)
    elif data == "coins_balance":
        await coins_balance(update, context)
    elif data == "admin_panel":
        await admin_panel(update, context)
    elif data == "admin_genkey":
        await query.edit_message_text(
            "🔑 *Admin Key Generation*\n\nUse commands:\n`/genkey <duration> [limit]`\nor\n`/keygenlimit <duration> <limit>`",
            parse_mode="Markdown"
        )
    elif data == "admin_logs":
        await view_logs(update, context)
    elif data == "admin_restart":
        await restart_bot(update, context)
    elif data == "admin_stats":
        await bot_stats(update, context)
    elif data == "admin_clear":
        await clear_database(update, context)
    elif data == "admin_antispam":
        await query.edit_message_text(
            "⏱ *Anti-Spam Settings*\n\nUse commands:\n`/antispam <duration>`\nor\n`/revokeantispam`",
            parse_mode="Markdown"
        )
    elif data == "admin_keymgmt":
        await query.edit_message_text(
            "🔑 *Key Management*\n\nUse commands:\n`/revokekey <user_id>`\nor\n`/keyinfo`",
            parse_mode="Markdown"
        )
    elif data == "admin_export":
        await export_data(update, context)
    elif data == "admin_referrals":
        await manage_referrals(update, context)
    elif data == "admin_whitelist":
        await whitelist_menu(update, context)
    elif data == "admin_quiz":
        await quiz_management(update, context)
    elif data.startswith("approve_ref_"):
        await approve_referral(update, context)
    elif data.startswith("reject_ref_"):
        await reject_referral(update, context)
    elif data == "whitelist_add":
        await whitelist_add_user(update, context)
    elif data == "whitelist_remove":
        await whitelist_remove_user(update, context)
    elif data == "whitelist_view":
        await whitelist_view_users(update, context)
    elif data.startswith("whitelist_remove_"):
        await process_whitelist_remove(update, context)
    elif data == "quiz_add":
        await quiz_add_question(update, context)
    elif data == "quiz_remove":
        await quiz_remove_question(update, context)
    elif data == "quiz_view":
        await quiz_view_questions(update, context)
    elif data == "quiz_toggle":
        await quiz_toggle_active(update, context)
    elif data == "quiz_prize":
        await quiz_set_prize(update, context)
    elif data.startswith("quiz_remove_"):
        await process_quiz_remove(update, context)
    elif data.startswith("quiz_answer_"):
        await quiz_answer(update, context)

def check_spam(user_id):
    if not keys_data.get("antispam"):
        return False
        
    duration_str, cooldown = next(iter(keys_data["antispam"].items()))
    now = datetime.now().timestamp()
    
    if user_id in ANTI_SPAM:
        if now - ANTI_SPAM[user_id] < cooldown:
            return True
        else:
            ANTI_SPAM[user_id] = now
            return False
    else:
        ANTI_SPAM[user_id] = now
        return False

async def handle_message(update: Update, context: CallbackContext):
    if update.message.text and update.message.text.startswith("/"):
        return
    
    user_data = context.user_data
    if user_data.get("awaiting_whitelist_add"):
        await process_whitelist_add(update, context)
    elif user_data.get("awaiting_quiz_add"):
        await process_quiz_add(update, context)
    elif user_data.get("awaiting_quiz_prize"):
        await process_quiz_prize(update, context)
    elif user_data.get("awaiting_search"):
        await process_search(update, context)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genkey", generate_key))
    application.add_handler(CommandHandler("keygenlimit", keygen_limit))
    application.add_handler(CommandHandler("key", redeem_key))
    application.add_handler(CommandHandler("logs", view_logs))
    application.add_handler(CommandHandler("keyinfo", key_info_all))
    application.add_handler(CommandHandler("generate", generate_menu))
    application.add_handler(CommandHandler("restart", restart_bot))
    application.add_handler(CommandHandler("clear", clear_database))
    application.add_handler(CommandHandler("stats", bot_stats))
    application.add_handler(CommandHandler("antispam", set_antispam))
    application.add_handler(CommandHandler("revokeantispam", revoke_antispam))
    application.add_handler(CommandHandler("revokekey", revoke_key))
    application.add_handler(CommandHandler("export", export_data))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CommandHandler("prices", price_list))
    application.add_handler(CommandHandler("search", search_accounts))
    application.add_handler(CommandHandler("referral", referral_program))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("coins", coins_balance))
    application.add_handler(CommandHandler("daily", daily_bonus))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()







>>>>>>> f402bc8da551950a280cc12eb512102887d477ae
