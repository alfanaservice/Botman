import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.command import Command
from aiogram.filters.text import Text as TextFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import exceptions

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"  # کانال عضویت اجباری
SUPPORT_USER = "@amirlphastam"

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

user_bots = {}  # user_id: {"token": str, "messages": list}

async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

async def clear_messages_loop(user_id, bot):
    while user_id in user_bots:
        await asyncio.sleep(30)
        messages = user_bots[user_id].get("messages", [])
        await delete_messages(bot, user_id, messages)
        user_bots[user_id]["messages"] = []

def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💬 ارسال پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton("➕ اضافه کردن دکمه", callback_data="add_button"),
        InlineKeyboardButton("🔄 روشن/خاموش ربات", callback_data="toggle_bot"),
        InlineKeyboardButton("📨 پشتیبانی", callback_data="support"),
        InlineKeyboardButton("📝 ارسال نظر", callback_data="feedback")
    )
    return kb

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # بررسی عضویت
    try:
        member = await manager_bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer(
                "❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید."
            )
            return
    except exceptions.TelegramBadRequest:
        await message.answer("❌ کانال برای بررسی عضویت صحیح نیست.")
        return

    if message.from_user.id in user_bots:
        await message.answer(
            f"سلام! ربات شما فعال است.\nتوکن ثبت شده: `{user_bots[message.from_user.id]['token']}`",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "سلام! لطفا توکن ربات خود را ارسال کنید تا ربات فعال شود."
        )

@dp.message(TextFilter())
async def receive_token(message: types.Message):
    user_id = message.from_user.id
    token = message.text.strip()
    if ":" not in token:
        await message.answer("❌ توکن معتبر نیست، دوباره امتحان کنید.")
        return

    user_bots[user_id] = {"token": token, "messages": []}
    await message.answer(
        f"✅ توکن ثبت شد.\nربات شما آماده استفاده است.",
        reply_markup=main_keyboard()
    )
    asyncio.create_task(clear_messages_loop(user_id, manager_bot))

@dp.callback_query(TextFilter("broadcast"))
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("پیام همگانی را ارسال کنید:")

@dp.callback_query(TextFilter("add_button"))
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("متن دکمه و لینک را ارسال کنید:")

@dp.callback_query(TextFilter("toggle_bot"))
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        user_bots.pop(user_id)
        await query.message.answer("ربات شما خاموش شد.")
    else:
        await query.message.answer("ربات شما روشن شد.")

@dp.callback_query(TextFilter("support"))
async def support_handler(query: types.CallbackQuery):
    await query.message.answer(f"📬 برای پشتیبانی با {SUPPORT_USER} تماس بگیرید.")

@dp.callback_query(TextFilter("feedback"))
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer(
        f"📝 لطفا نظر خود را ارسال کنید. بعد از ارسال، نظر شما به {SUPPORT_USER} فرستاده می‌شود."
    )

@dp.message(Command("del"))
async def del_chat(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_bots:
        messages = user_bots[user_id].get("messages", [])
        await delete_messages(manager_bot, user_id, messages)
        user_bots[user_id]["messages"] = []
    try:
        await manager_bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    await message.answer("تمام پیام‌ها پاک شدند.")

@dp.message(TextFilter())
async def forward_feedback(message: types.Message):
    user_id = message.from_user.id
    if message.text.startswith("/"):
        return
    if user_id in user_bots:
        await manager_bot.send_message(SUPPORT_USER, f"نظر از {user_id}:\n{message.text}")

async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    asyncio.run(main())
    
