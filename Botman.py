from telebot import TeleBot, types

bot = TeleBot(USER_TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 کانال ما", "ℹ️ درباره ما", "⚙️ تنظیمات", "💬 پشتیبانی")
    bot.send_message(
        msg.chat.id,
        "👋 سلام!\nبه ربات رسمی خوش اومدی 😎\n"
        "از منوی زیر استفاده کن 👇",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handler(msg):
    if msg.text == "📢 کانال ما":
        bot.send_message(msg.chat.id, "📣 عضو کانال ما شوید:\nhttps://t.me/YOUR_CHANNEL")
    elif msg.text == "ℹ️ درباره ما":
        bot.send_message(msg.chat.id, "🤖 این ربات با عشق ساخته شده 💖")
    elif msg.text == "⚙️ تنظیمات":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🔊 صدا روشن", "🔇 صدا خاموش", "⬅️ بازگشت")
        bot.send_message(msg.chat.id, "⚙️ تنظیمات دلخواهت رو انتخاب کن:", reply_markup=markup)
    elif msg.text == "💬 پشتیبانی":
        bot.send_message(msg.chat.id, "📞 برای پشتیبانی به @YOUR_TELEGRAM پیام بده.")
    elif msg.text == "🔊 صدا روشن":
        bot.send_message(msg.chat.id, "✅ صدا فعال شد 🎵")
    elif msg.text == "🔇 صدا خاموش":
        bot.send_message(msg.chat.id, "🔕 صدا غیرفعال شد")
    elif msg.text == "⬅️ بازگشت":
        start(msg)
    else:
        bot.send_message(msg.chat.id, f"❓ متوجه نشدم: {msg.text}")

bot.infinity_polling()
