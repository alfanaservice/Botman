import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import exceptions

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"  # کانال برای عضویت اجباری

bot = Bot(token=MANAGER_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_bots = {}

async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

async def clear_messages_loop(user_id):
    while True:
        await asyncio.sleep(30)
        if user_id in user_bots:
            messages = user_bots[user_id].get("messages", [])
            await delete_messages(bot, user_id, messages)
            user_bots[user_id]["messages"] = []

def manager_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 پیام همگانی", callback_data="broadcast")],
        [InlineKeyboardButton(text="➕ اضافه کردن دکمه", callback_data="add_button")],
        [InlineKeyboardButton(text="🔄 روشن/خاموش ربات", callback_data="toggle_bot")],
        [InlineKeyboardButton(text="📨 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton(text="📝 ارسال نظر", callback_data="feedback")]
    ])
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    # بررسی عضویت
    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
            return
    except exceptions.TelegramAPIError:
        await message.answer("❌ خطا در بررسی عضویت کانال.")
        return

    await message.answer("سلام! ربات منیجر شما فعال است.", 
                         reply_markup=manager_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(lambda c: c.data == "broadcast")
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("پیام همگانی را وارد کنید:")

@dp.callback_query(lambda c: c.data == "add_button")
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("متن دکمه و لینک را وارد کنید:")

@dp.callback_query(lambda c: c.data == "toggle_bot")
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        user_bots.pop(user_id)
        await query.message.answer("ربات شما خاموش شد.")
    else:
        user_bots[user_id] = {"messages": []}
        asyncio.create_task(clear_messages_loop(user_id))
        await query.message.answer("ربات شما روشن شد. پیام‌ها هر ۳۰ ثانیه پاک می‌شوند.")

@dp.callback_query(lambda c: c.data == "support")
async def support_handler(query: types.CallbackQuery):
    await query.message.answer("📬 برای پشتیبانی با @Amirlphastam تماس بگیرید.")

@dp.callback_query(lambda c: c.data == "feedback")
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
