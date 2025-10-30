from aiogram import Bot, Dispatcher, types, exceptions
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio

MANAGER_TOKEN = "8230683502:AAFNKrZd-86yrx3ckGlA0BjgSx3vajCp8Es"
ADMIN_ID = 7503028992
CHANNEL_ID = "@sfg_team1"

manager_bot = Bot(token=MANAGER_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

user_bots = {}  # {user_id: {"bots": [{"bot": Bot, "token": str, "messages": []}]}}

class UserBotStates(StatesGroup):
    waiting_token = State()

# ================= Helper =================
async def delete_messages(bot: Bot, chat_id: int, messages: list):
    for msg_id in messages:
        try:
            await bot.delete_message(chat_id, msg_id)
        except exceptions.MessageToDeleteNotFound:
            pass

async def clear_messages_loop(user_id: int, bot: Bot, bot_data: dict):
    while True:
        await asyncio.sleep(30)
        messages = bot_data.get("messages", [])
        await delete_messages(bot, user_id, messages)
        bot_data["messages"] = []

def build_main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="💬 پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton(text="➕ اضافه کردن دکمه", callback_data="add_button")
    )
    kb.row(
        InlineKeyboardButton(text="🔄 روشن/خاموش", callback_data="toggle_bot"),
        InlineKeyboardButton(text="📨 پشتیبانی", callback_data="support")
    )
    kb.row(
        InlineKeyboardButton(text="📝 ارسال نظر", callback_data="feedback")
    )
    return kb.as_markup()

# ================= Handlers =================
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    # بررسی عضویت
    try:
        member = await manager_bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["left", "kicked"]:
            await message.answer("❌ لطفا ابتدا عضو کانال شوید و دوباره /start را بزنید.")
            return
    except:
        pass

    await message.answer("سلام! لطفا توکن ربات خود را وارد کنید تا مدیریت فعال شود:")
    await state.set_state(UserBotStates.waiting_token)

@dp.message()
async def handle_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    # مرحله دریافت توکن
    if current_state == UserBotStates.waiting_token.state:
        user_token = message.text.strip()
        try:
            user_bot = Bot(token=user_token)
            me = await user_bot.get_me()
        except:
            await message.answer("❌ توکن نامعتبر است، دوباره امتحان کنید.")
            return

        user_id = message.from_user.id
        if user_id not in user_bots:
            user_bots[user_id] = {"bots": []}
        bot_data = {"bot": user_bot, "token": user_token, "messages": []}
        user_bots[user_id]["bots"].append(bot_data)

        asyncio.create_task(clear_messages_loop(user_id, user_bot, bot_data))
        await state.clear()

        await message.answer(
            f"✅ ربات {me.username} با موفقیت اضافه شد!",
            reply_markup=build_main_keyboard()
        )
        return

# ================= Callback =================
@dp.callback_query(lambda c: c.data == "broadcast")
async def broadcast_handler(query: types.CallbackQuery):
    await query.message.answer("پیام همگانی را وارد کنید:")

@dp.callback_query(lambda c: c.data == "add_button")
async def add_button_handler(query: types.CallbackQuery):
    await query.message.answer("متن دکمه و لینک را وارد کنید:")

@dp.callback_query(lambda c: c.data == "toggle_bot")
async def toggle_bot_handler(query: types.CallbackQuery):
    user_id = query.from_user.id
    if user_id not in user_bots or not user_bots[user_id]["bots"]:
        await query.message.answer("❌ شما هنوز رباتی اضافه نکرده‌اید.")
        return
    await query.message.answer("🔄 وضعیت ربات‌ها تغییر کرد.")

@dp.callback_query(lambda c: c.data == "support")
async def support_handler(query: types.CallbackQuery):
    await query.message.answer("📬 برای پشتیبانی با @Amirlphastam تماس بگیرید.")

@dp.callback_query(lambda c: c.data == "feedback")
async def feedback_handler(query: types.CallbackQuery):
    await query.message.answer("📝 نظر خود را ارسال کنید:")

@dp.message()
async def forward_feedback(message: types.Message):
    await manager_bot.send_message(ADMIN_ID, f"نظر از {message.from_user.id}:\n{message.text}")

# ================= Run =================
async def main():
    print("🚀 Manager bot is running...")
    await dp.start_polling(manager_bot)

if __name__ == "__main__":
    asyncio.run(main())
        
