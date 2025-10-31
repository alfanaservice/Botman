from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
import asyncio
import json
import os

# ---------------------- تنظیمات اصلی ----------------------
TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"  # توکن ربات
CHANNEL_ID = -1003225803553  # آیدی عددی کانال @tablikhatsfgteam
USERS_FILE = "users.json"  # فایل ذخیره کاربران

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------------- توابع کاربران ----------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

# ---------------------- کیبورد شروع ----------------------
def start_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="اخبار ربات", url="https://t.me/sfg_newsbot/5"))
    return kb.as_markup()

# ---------------------- فرمان /start ----------------------
@dp.message(CommandStart())
async def start_message(message: types.Message):
    add_user(message.from_user.id)
    try:
        await bot.send_message(message.chat.id, "❤️")
    except:
        pass
    await message.answer("🚀 ربات در حال آپدیت است...", reply_markup=start_keyboard())

# ---------------------- فوروارد پست‌های کانال ----------------------
@dp.channel_post()
async def channel_post_handler(message: types.Message):
    if message.chat.id == CHANNEL_ID:
        users = load_users()
        for user_id in users:
            try:
                await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=CHANNEL_ID,
                    message_id=message.message_id
                )
                await asyncio.sleep(0.1)  # جلوگیری از محدودیت تلگرام
            except:
                continue

# ---------------------- اجرای ربات ----------------------
async def main():
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
