import telebot
import requests

# 🔹 توکن ربات مدیر (ربات اصلی)
MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"

# 🔹 آدرس فایل خام GitHub که قراره ربات‌ها ازش کد بگیرن
GITHUB_RAW_URL = "https://raw.githubusercontent.com/USERNAME/REPOSITORY/main/user_bot.py"

bot = telebot.TeleBot(MANAGER_TOKEN)

# حافظه موقت (برای نگه‌داری توکن کاربران)
user_tokens = {}

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 سلام! لطفاً توکن رباتت رو بفرست تا مدیریتش رو فعال کنم.")

@bot.message_handler(func=lambda m: True)
def handle_token(message):
    token = message.text.strip()
    if len(token) < 40 or not token.startswith(""):
        bot.reply_to(message, "❌ توکن معتبر نیست، لطفاً دوباره وارد کن.")
        return

    user_tokens[message.from_user.id] = token
    bot.reply_to(message, "✅ توکن ذخیره شد!\nدر حال راه‌اندازی ربات اختصاصی شما...")

    # تلاش برای اجرای ربات از GitHub
    try:
        code = requests.get(GITHUB_RAW_URL).text
        exec_env = {"USER_TOKEN": token}
        exec(code, exec_env)
        bot.send_message(message.chat.id, "🤖 ربات شما با موفقیت از GitHub اجرا شد!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطا در اجرای کد: {e}")

print("🚀 Manager Bot is running...")
bot.infinity_polling()
