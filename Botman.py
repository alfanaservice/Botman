from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"
SUPPORT_USER = "@amirlphastam"

bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

user_bots = {}  # ذخیره توکن‌ها و پیام‌ها

async def delete_messages(chat_id, messages):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass

async def clear_messages_loop(user_id):
    while True:
        await asyncio.sleep(30)
        if user_id in user_bots:
            messages = user_bots[user_id].get("messages", [])
            await delete_messages(user_id, messages)
            user_bots[user_id]["messages"] = []

def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton("💬 پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton("➕ اضافه کردن دکمه", callback_data="add_button")
    )
    kb.row(
        InlineKeyboardButton("🔄 روشن/خاموش ربات", callback_data="toggle_bot"),
        InlineKeyboardButton("📨 پشتیبانی", callback_data="support")
    )
    kb.row(
        InlineKeyboardButton("📝 ارسال نظر", callback_data="feedback"),
        InlineKeyboardButton("🗑 پاک کردن چت", callback_data="del_chat")
    )
    return kb.as_markup()

@dp.message(F.text == "/start")
async def start(message: types.Message):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
            return
    except:
        await message.answer("❌ مشکلی پیش آمد. لطفا بعدا امتحان کنید.")
        return

    if message.from_user.id in user_bots:
        await message.answer("ربات شما فعال است.", reply_markup=main_keyboard())
    else:
        await message.answer("سلام! لطفا توکن ربات خود را ارسال کنید:")

@dp.message()
async def receive_token(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_bots and not message.text.startswith("/"):
        token = message.text.strip()
        try:
            temp_bot = Bot(token=token)
            await temp_bot.get_me()  # بررسی اعتبار توکن
            user_bots[user_id] = {"token": token, "messages": [], "bot": temp_bot}
            asyncio.create_task(clear_messages_loop(user_id))
            await message.answer("✅ ربات شما اضافه شد.", reply_markup=main_keyboard())
        except:
            await message.answer("❌ توکن نامعتبر است. لطفا دوباره ارسال کنید.")

@dp.callback_query(F.data == "broadcast")
async def broadcast(query: types.CallbackQuery):
    await query.message.answer("💬 لطفا پیام همگانی را ارسال کنید:")

@dp.callback_query(F.data == "add_button")
async def add_button(query: types.CallbackQuery):
    await query.message.answer("➕ لطفا متن دکمه و لینک را وارد کنید:")

@dp.callback_query(F.data == "toggle_bot")
async def toggle_bot(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        await query.message.answer("🔄 ربات روشن/خاموش شد.")
    else:
        await query.message.answer("❌ ابتدا توکن خود را ارسال کنید.")

@dp.callback_query(F.data == "support")
async def support(query: types.CallbackQuery):
    await query.message.answer(f"📬 برای پشتیبانی با {SUPPORT_USER} تماس بگیرید.")

@dp.callback_query(F.data == "feedback")
async def feedback(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

@dp.callback_query(F.data == "del_chat")
async def del_chat(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        messages = user_bots[user_id].get("messages", [])
        await delete_messages(user_id, messages)
        user_bots[user_id]["messages"] = []
        await query.message.answer("🗑 چت پاک شد.")

@dp.message()
async def handle_feedback(message: types.Message):
    if not message.text.startswith("/"):
        await bot.send_message(SUPPORT_USER, f"نظر از {message.from_user.id}:\n{message.text}")

async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
