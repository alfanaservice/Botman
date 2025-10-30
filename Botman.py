from telebot import TeleBot

bot = TeleBot("8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es")

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "سلام! ربات از گیت‌هاب لود شده 😎")

bot.infinity_polling()
