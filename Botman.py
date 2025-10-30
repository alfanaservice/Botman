from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"  # توکن رباتت

bot = Bot(token=TOKEN)
dp = Dispatcher()

def start_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="اخبار ربات", url="https://t.me/sfg_newsbot"))
    return kb.as_markup()

@dp.message(F.text == "/start")
async def start_message(message: types.Message):
    # ری‌اکشن قلب به پیام کاربر
    try:
        await bot.send_message(message.chat.id, "❤️")
    except:
        pass

    await message.answer(
        "🚀 ربات در حال آپدیت است...",
        reply_markup=start_keyboard()
    )

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
