from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram import exceptions
import asyncio

# ================== تنظیمات ==================
MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
CHANNEL_ID = "@sfg_team1"
ADMIN_USERNAME = "Amirlphastam"
# ============================================

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ================== FSM ==================
class UserStates(StatesGroup):
    waiting_token = State()
    active = State()

# وضعیت ربات‌ها: {user_id: {"bot": Bot, "messages": []}}
user_bots = {}

# ================== توابع کمکی ==================
async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

async def clear_messages_loop(user_id):
    while user_id in user_bots:
        await asyncio.sleep(30)
        messages = user_bots[user_id].get("messages", [])
        await delete_messages(user_bots[user_id]["bot"], user_id, messages)
        user_bots[user_id]["messages"] = []

def build_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="💬 پیام همگانی", callback_data="broadcast"))
    kb.add(InlineKeyboardButton(text="➕ اضافه کردن دکمه", callback_data="add_button"))
    kb.add(InlineKeyboardButton(text="🔄 روشن/خاموش ربات", callback_data="toggle_bot"))
    kb.add(InlineKeyboardButton(text="📨 پشتیبانی", callback_data="support"))
    kb.add(InlineKeyboardButton(text="📝 ارسال نظر", callback_data="feedback"))
    kb.adjust(1)  # هر ردیف 1 دکمه
    return kb

# ================== دستورات ==================
@dp.message(lambda message: message.text == "/start")
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

    await message.answer("💎 لطفا توکن ربات خود را وارد کنید:")
    await state.set_state(UserStates.waiting_token)

# ================== دریافت توکن ==================
@dp.message(StateFilter(UserStates.waiting_token))
async def receive_token(message: types.Message, state: FSMContext):
    user_token = message.text.strip()
    try:
        user_bot = Bot(token=user_token)
        me = await user_bot.get_me()  # بررسی اعتبار توکن
    except Exception:
        await message.answer("❌ توکن وارد شده معتبر نیست. دوباره امتحان کنید:")
        return

    user_bots[message.from_user.id] = {"bot": user_bot, "messages": []}
    asyncio.create_task(clear_messages_loop(message.from_user.id))
    await state.set_state(UserStates.active)
    await message.answer(
        f"✅ ربات شما با نام @{me.username} فعال شد!",
        reply_markup=build_main_keyboard().as_markup(),
        parse_mode=ParseMode.MARKDOWN
    )

# ================== هندلرها ==================
@dp.callback_query(lambda c: c.data == "broadcast", StateFilter(UserStates.active))
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("📢 پیام همگانی خود را وارد کنید:")

@dp.callback_query(lambda c: c.data == "add_button", StateFilter(UserStates.active))
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("➕ متن دکمه و لینک را وارد کنید:")

@dp.callback_query(lambda c: c.data == "toggle_bot", StateFilter(UserStates.active))
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id in user_bots:
        user_bots.pop(user_id)
        await query.message.answer("🛑 ربات شما خاموش شد.")
    else:
        await query.message.answer("✅ ربات روشن شد. پیام‌ها هر ۳۰ ثانیه پاک می‌شوند.")
        # برای راه‌اندازی دوباره، باید توکن از کاربر گرفته شود

@dp.callback_query(lambda c: c.data == "support", StateFilter(UserStates.active))
async def support_handler(query: types.CallbackQuery):
    await query.message.answer(f"📬 برای پشتیبانی با @{ADMIN_USERNAME} تماس بگیرید.")

@dp.callback_query(lambda c: c.data == "feedback", StateFilter(UserStates.active))
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 لطفا نظر خود را ارسال کنید:")

@dp.message(StateFilter(UserStates.active))
async def feedback_receive(message: types.Message):
    # ارسال نظر به ادمین
    await manager_bot.send_message(
        ADMIN_USERNAME,
        f"💬 نظر از @{message.from_user.username} ({message.from_user.id}):\n\n{message.text}"
    )
    await message.answer("✅ نظر شما ارسال شد!")

# ================== اجرای منیجر ==================
async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
                        
