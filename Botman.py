import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import json
import os

# ==========================
# مدیریت توکن‌ها
# ==========================
TOKENS_FILE = "user_tokens.json"

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f)

user_tokens = load_tokens()

# ==========================
# Dispatcher ربات منیجر
# ==========================
MANAGER_TOKEN = os.getenv("8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es")  # توکن ربات منیجر روی هاست
manager_bot = Bot(token=MANAGER_TOKEN, parse_mode="HTML")
manager_dp = Dispatcher()

CHANNEL_USERNAME = "YourChannel"  # نام کانال برای عضویت اجباری

# ==========================
# دکمه‌ها شیشه‌ای
# ==========================
def main_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💬 ارسال نظر", callback_data="send_feedback"),
         InlineKeyboardButton("🛠 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("➕ اضافه کردن ربات", callback_data="add_bot")]
    ])
    return kb

# ==========================
# بررسی عضویت در کانال
# ==========================
async def check_subscription(user_id):
    member = await manager_bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    return member.status in ["member", "creator", "administrator"]

# ==========================
# استارت ربات منیجر
# ==========================
@manager_dp.message(Command("start"))
async def start_cmd(message: types.Message):
    subscribed = await check_subscription(message.from_user.id)
    if not subscribed:
        await message.answer(f"⚠️ برای استفاده از ربات ابتدا باید عضو کانال شوید: @Sfg_team1")
        return

    await message.answer(
        "<b>سلام! 👋 ربات منیجر آماده است.</b>\nتوکن ربات خود را وارد کنید یا یکی اضافه کنید.",
        reply_markup=main_keyboard()
    )

# ==========================
# هندلر دکمه‌ها
# ==========================
@manager_dp.callback_query(lambda c: c.data)
async def callbacks_handler(callback: types.CallbackQuery):
    if callback.data == "send_feedback":
        await callback.message.answer("💬 لطفاً نظر خود را ارسال کنید:")
    elif callback.data == "support":
        await callback.message.answer("🛠 برای پشتیبانی با این آیدی تماس بگیرید: @YourSupport")
    elif callback.data == "add_bot":
        await callback.message.answer("🔑 توکن ربات خود را ارسال کنید:")

    await callback.answer()

# ==========================
# دریافت توکن کاربر و ذخیره
# ==========================
@manager_dp.message()
async def handle_tokens(message: types.Message):
    text = message.text.strip()
    if text.startswith("bot"):  # می‌تونی regex بذاری تا اعتبارسنجی بهتر باشه
        user_tokens[str(message.from_user.id)] = text
        save_tokens(user_tokens)
        await message.answer("✅ توکن ذخیره شد. ربات شما آماده اجراست!")
        asyncio.create_task(start_user_bot(message.from_user.id, text))

# ==========================
# اجرای ربات کاربر
# ==========================
async def start_user_bot(user_id, token):
    user_bot = Bot(token=token, parse_mode="HTML")
    user_dp = Dispatcher()

    @user_dp.message()
    async def echo_all(msg: types.Message):
        # پیام شیشه‌ای
        await msg.answer(f"💎 پیام شما دریافت شد:\n<code>{msg.text}</code>")

    # پاک کردن پیام‌ها هر ۳۰ ثانیه
    async def auto_delete():
        while True:
            await asyncio.sleep(30)
            try:
                updates = await user_bot.get_updates()
                for upd in updates:
                    if upd.message:
                        await user_bot.delete_message(upd.message.chat.id, upd.message.message_id)
            except:
                pass

    asyncio.create_task(auto_delete())
    await user_dp.start_polling(user_bot)

# ==========================
# اجرای ربات منیجر
# ==========================
async def main():
    await manager_dp.start_polling(manager_bot)

if __name__ == "__main__":
    asyncio.run(main())
    
