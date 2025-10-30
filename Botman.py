from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"  # کانال برای عضویت اجباری
SUPPORT_USER = "@amirlphastam"

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

user_bots = {}  # {user_id: {"token": str, "messages": [], "bot": Bot}}

async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass

async def clear_messages_loop(user_id):
    while True:
        await asyncio.sleep(30)
        if user_id in user_bots:
            bot_data = user_bots[user_id]
            await delete_messages(manager_bot, user_id, bot_data.get("messages", []))
            user_bots[user_id]["messages"] = []

def create_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="💬 پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton(text="➕ اضافه کردن دکمه", callback_data="add_button")
    )
    kb.row(
        InlineKeyboardButton(text="🔄 روشن/خاموش ربات", callback_data="toggle_bot"),
        InlineKeyboardButton(text="📨 پشتیبانی", callback_data="support")
    )
    kb.row(
        InlineKeyboardButton(text="📝 ارسال نظر", callback_data="feedback"),
        InlineKeyboardButton(text="🗑 پاک کردن چت", callback_data="del_chat")
    )
    return kb.as_markup()

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    # بررسی عضویت
    try:
        member = await manager_bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
            return
    except:
        await message.answer("❌ مشکلی پیش آمد. لطفا بعدا امتحان کنید.")
        return

    if message.from_user.id in user_bots:
        await message.answer("ربات شما قبلا فعال شده است.", reply_markup=create_main_keyboard())
    else:
        await message.answer("سلام! لطفا توکن ربات خود را ارسال کنید:")

@dp.message()
async def receive_token(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_bots:
        token = message.text.strip()
        try:
            # بررسی توکن با ساخت Bot
            temp_bot = Bot(token=token)
            await temp_bot.get_me()
            user_bots[user_id] = {"token": token, "messages": [], "bot": temp_bot}
            asyncio.create_task(clear_messages_loop(user_id))
            await message.answer("✅ ربات شما با موفقیت اضافه شد.", reply_markup=create_main_keyboard())
        except:
            await message.answer("❌ توکن نامعتبر است. لطفا دوباره ارسال کنید.")

@dp.callback_query(F.data == "broadcast")
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("💬 لطفا پیام همگانی را ارسال کنید:")

@dp.callback_query(F.data == "add_button")
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("➕ لطفا متن دکمه و لینک را وارد کنید:")

@dp.callback_query(F.data == "toggle_bot")
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        # فقط روشن/خاموش کردن داخلی
        await query.message.answer("🔄 ربات شما روشن/خاموش شد.")
    else:
        await query.message.answer("❌ ابتدا توکن خود را ارسال کنید.")

@dp.callback_query(F.data == "support")
async def support_handler(query: types.CallbackQuery):
    await query.message.answer(f"📬 برای پشتیبانی با {SUPPORT_USER} تماس بگیرید.")

@dp.callback_query(F.data == "feedback")
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

@dp.callback_query(F.data == "del_chat")
async def del_chat_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        bot_data = user_bots[user_id]
        await delete_messages(manager_bot, user_id, bot_data.get("messages", []))
        user_bots[user_id]["messages"] = []
        await query.message.answer("🗑 چت شما پاک شد.")

@dp.message()
async def handle_feedback(message: types.Message):
    # ارسال نظرات به پشتیبانی
    if not message.text.startswith("/"):
        await manager_bot.send_message(
            SUPPORT_USER,
            f"نظر از {message.from_user.id}:\n{message.text}"
        )

async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
        
