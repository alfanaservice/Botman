import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import exceptions

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
FEEDBACK_CHAT = "@amirlphastam"
CHANNEL_ID = "@sfg_team1"

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

TOKENS_FILE = "user_tokens.json"
user_bots = {}  # {user_id: {"bot": Bot instance, "messages": []}}

# بارگذاری توکن‌ها از فایل
try:
    with open(TOKENS_FILE, "r") as f:
        saved_tokens = json.load(f)
except:
    saved_tokens = {}

async def save_tokens():
    with open(TOKENS_FILE, "w") as f:
        json.dump(saved_tokens, f)

async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

async def clear_messages_loop(user_id, bot):
    while True:
        await asyncio.sleep(30)
        if user_id in user_bots:
            messages = user_bots[user_id].get("messages", [])
            await delete_messages(bot, user_id, messages)
            user_bots[user_id]["messages"] = []

def main_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💬 ارسال پیام همگانی", callback_data="broadcast")],
        [InlineKeyboardButton("➕ اضافه کردن دکمه", callback_data="add_button")],
        [InlineKeyboardButton("🔄 روشن/خاموش ربات", callback_data="toggle_bot")],
        [InlineKeyboardButton("📨 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("📝 ارسال نظر", callback_data="feedback")]
    ])
    return kb

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    member = await manager_bot.get_chat_member(CHANNEL_ID, message.from_user.id)
    if member.status in ["left", "kicked"]:
        await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
        return

    user_id = str(message.from_user.id)
    if user_id in saved_tokens:
        await message.answer(
            f"ربات شما فعال است. توکن ثبت شده:\n`{saved_tokens[user_id]}`",
            reply_markup=main_keyboard(),
        )
    else:
        await message.answer("لطفا توکن ربات خود را ارسال کنید:")

@dp.message(F.text)
async def receive_token(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in saved_tokens:
        return  # قبلاً ثبت شده
    token = message.text.strip()
    try:
        bot_test = Bot(token=token)
        await bot_test.get_me()  # بررسی توکن
    except:
        await message.answer("❌ توکن نامعتبر است. دوباره امتحان کنید.")
        return

    saved_tokens[user_id] = token
    await save_tokens()
    user_bots[user_id] = {"bot": bot_test, "messages": []}
    asyncio.create_task(clear_messages_loop(user_id, bot_test))
    await message.answer("✅ توکن ثبت شد و ربات شما فعال است.", reply_markup=main_keyboard())

@dp.callback_query(F.data == "broadcast")
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("پیام همگانی را وارد کنید:")

@dp.callback_query(F.data == "add_button")
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("متن دکمه و لینک را وارد کنید:")

@dp.callback_query(F.data == "toggle_bot")
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = str(query.from_user.id)
    if user_id in user_bots:
        user_bots.pop(user_id)
        await query.message.answer("ربات شما خاموش شد.")
    else:
        token = saved_tokens.get(user_id)
        if token:
            bot_instance = Bot(token=token)
            user_bots[user_id] = {"bot": bot_instance, "messages": []}
            asyncio.create_task(clear_messages_loop(user_id, bot_instance))
            await query.message.answer("ربات شما روشن شد و پیام‌ها پاک می‌شوند هر ۳۰ ثانیه.")
        else:
            await query.message.answer("ابتدا توکن خود را ارسال کنید.")

@dp.callback_query(F.data == "support")
async def support_handler(query: types.CallbackQuery):
    await query.message.answer("📬 برای پشتیبانی با @amirlphastam تماس بگیرید.")

@dp.callback_query(F.data == "feedback")
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

@dp.message(F.text)
async def feedback_receive(message: types.Message):
    user_id = message.from_user.id
    await manager_bot.send_message(FEEDBACK_CHAT, f"نظر از کاربر {user_id}:\n{message.text}")
    await message.answer("✅ نظر شما ارسال شد.")

async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
