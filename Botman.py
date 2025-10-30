from telebot import TeleBot, types
import datetime

bot = TeleBot(USER_TOKEN)

# ---------------------------
# ⚙️ تنظیمات اولیه
# ---------------------------
ADMIN_USERNAME = "@YOUR_ADMIN"
CHANNEL_LINK = "https://t.me/YOUR_CHANNEL"
SUPPORT_LINK = "https://t.me/YOUR_SUPPORT"
BOT_NAME = "💎 ربات رسمی شما 💎"

# ---------------------------
# 🔹 تابع منوی اصلی
# ---------------------------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 کانال", "💬 پشتیبانی", "⚙️ تنظیمات", "ℹ️ درباره ما")
    markup.add("📊 وضعیت ربات", "📨 ارسال نظر")
    return markup

# ---------------------------
# 🔹 /start
# ---------------------------
@bot.message_handler(commands=["start"])
def start(msg):
    name = msg.from_user.first_name or "کاربر"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    bot.send_message(
        msg.chat.id,
        f"👋 سلام {name}!\n"
        f"به {BOT_NAME} خوش اومدی 😎\n\n"
        "از منوی زیر استفاده کن 👇",
        reply_markup=main_menu()
    )
    print(f"[{now}] کاربر جدید: {msg.from_user.id} ({name})")

# ---------------------------
# 🔹 پاسخ به دکمه‌های منوی اصلی
# ---------------------------
@bot.message_handler(func=lambda m: True)
def main_handler(msg):
    text = msg.text
    chat_id = msg.chat.id

    if text == "📢 کانال":
        bot.send_message(chat_id, f"📣 عضو کانال ما شوید:\n{CHANNEL_LINK}")

    elif text == "💬 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✉️ تماس با پشتیبانی", url=SUPPORT_LINK))
        bot.send_message(chat_id, "📞 برای ارتباط با پشتیبانی روی دکمه زیر بزن:", reply_markup=markup)

    elif text == "⚙️ تنظیمات":
        settings_menu(chat_id)

    elif text == "ℹ️ درباره ما":
        bot.send_message(chat_id,
            f"🤖 {BOT_NAME}\n"
            "نسخه: 1.0.0\n"
            "توسعه‌دهنده: " + ADMIN_USERNAME
        )

    elif text == "📊 وضعیت ربات":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 بروزرسانی وضعیت", callback_data="refresh"))
        bot.send_message(chat_id, "📈 وضعیت فعلی:\nهمه‌چیز عالیه ✅", reply_markup=markup)

    elif text == "📨 ارسال نظر":
        bot.send_message(chat_id, "💭 لطفاً نظرت رو بنویس تا به ادمین ارسال کنم ✍️")
        bot.register_next_step_handler(msg, send_feedback)

    elif text == "⬅️ بازگشت":
        bot.send_message(chat_id, "↩️ بازگشت به منوی اصلی", reply_markup=main_menu())

    else:
        bot.send_message(chat_id, f"❓ دستور ناشناخته: {text}")

# ---------------------------
# 🔹 منوی تنظیمات
# ---------------------------
def settings_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔊 صدا روشن", "🔇 صدا خاموش")
    markup.add("🌙 حالت شب", "☀️ حالت روز")
    markup.add("⬅️ بازگشت")
    bot.send_message(chat_id, "⚙️ تنظیمات ربات:", reply_markup=markup)

# ---------------------------
# 🔹 ارسال بازخورد به ادمین
# ---------------------------
def send_feedback(msg):
    feedback = msg.text
    bot.send_message(msg.chat.id, "✅ نظر شما ارسال شد، ممنون از بازخوردتون 🙏")
    bot.send_message(
        ADMIN_USERNAME,
        f"📬 بازخورد جدید از [{msg.from_user.first_name}](tg://user?id={msg.from_user.id}):\n\n{feedback}",
        parse_mode="Markdown"
    )

# ---------------------------
# 🔹 کال‌بک اینلاین (برای بروزرسانی وضعیت)
# ---------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "refresh":
        bot.edit_message_text(
            "✅ وضعیت ربات: فعال\n📅 آخرین بروزرسانی: هم‌اکنون ⏱",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=call.message.reply_markup
        )

# ---------------------------
# 🚀 اجرای ربات
# ---------------------------
print("✅ ربات با موفقیت اجرا شد!")
bot.infinity_polling()
    
