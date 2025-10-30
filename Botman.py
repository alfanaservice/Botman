from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import exceptions
import asyncio

# ================== تنظیمات ==================
MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"  # کانال برای عضویت اجباری
# ============================================

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# وضعیت ربات‌ها: {user_id: {"bot": Bot, "messages": []}}
user_bots = {}

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

# ================== دستورات ==================
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    # بررسی عضویت
    try:
        member = await manager_bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
            return
    except exceptions.TelegramAPIError:
        await message.answer("❌ بررسی عضویت امکان‌پذیر نیست. لطفا بعدا دوباره امتحان کنید.")
        return

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="💬 ارسال پیام همگانی", callback_data="broadcast"))
    kb.add(InlineKeyboardButton(text="➕ اضافه کردن دکمه", callback_data="add_button"))
    kb.add(InlineKeyboardButton(text="🔄 روشن/خاموش ربات", callback_data="toggle_bot"))
    kb.add(InlineKeyboardButton(text="📨 پشتیبانی", callback_data="support"))
    kb.add(InlineKeyboardButton(text="📝 ارسال نظر", callback_data="feedback"))

    await message.answer(
        "💎 سلام! ربات منیجر شما فعال است.",
        reply_markup=kb.as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )

# ================== هندلرها ==================
@dp.callback_query(F.data == "broadcast")
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("📢 پیام همگانی خود را وارد کنید:")

@dp.callback_query(F.data == "add_button")
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("➕ متن دکمه و لینک را وارد کنید:")

@dp.callback_query(F.data == "toggle_bot")
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        user_bots.pop(user_id)
        await query.message.answer("🛑 ربات شما خاموش شد.")
    else:
        await query.message.answer("✅ ربات شما روشن شد. پیام‌ها هر ۳۰ ثانیه پاک می‌شوند.")
        # نمونه ربات ساده با توکن کاربر (اینجا توکن باید از کاربر گرفته شود)
        # user_bots[user_id] = {"bot": Bot(token=user_token), "messages": []}
        # asyncio.create_task(clear_messages_loop(user_id, user_bots[user_id]["bot"]))

@dp.callback_query(F.data == "support")
async def support_handler(query: types.CallbackQuery):
    await query.message.answer("📬 برای پشتیبانی با @Amirlphastam تماس بگیرید.")

@dp.callback_query(F.data == "feedback")
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

# ================== اجرای منیجر ==================
async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
