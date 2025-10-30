import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ======= ذخیره توکن های کاربران =======
user_bots = {}  # {user_id: Bot}

# ======= استارت ربات منیجر =======
MANAGER_TOKEN = "توکن_منیجر"
manager_bot = Bot(token=MANAGER_TOKEN)
dp = Dispatcher(manager_bot)

# ======= استارت کاربر =======
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "سلام! توکن ربات خودت رو بده تا رباتتو شخصی سازی کنیم."
    )

# ======= گرفتن توکن ربات کاربر =======
@dp.message_handler(lambda m: m.text.startswith("BotToken:"))
async def register_bot(message: types.Message):
    token = message.text.split("BotToken:")[1].strip()
    try:
        user_bot = Bot(token=token)
        user_bots[message.from_user.id] = user_bot
        await message.answer(
            "✅ ربات شما ثبت شد!\nحالا میتونی دکمه و پیام‌هاشو شخصی سازی کنی.",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("➕ اضافه کردن دکمه", callback_data="add_button"),
                InlineKeyboardButton("✏️ ارسال پیام تست", callback_data="send_test")
            )
        )
    except Exception as e:
        await message.answer(f"❌ توکن اشتباه است یا ربات فعال نیست.\nخطا: {e}")

# ======= هندلر دکمه ها =======
@dp.callback_query_handler(lambda c: True)
async def buttons(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in user_bots:
        await call.answer("ابتدا توکن رباتت رو بده!", show_alert=True)
        return

    if call.data == "add_button":
        await call.message.answer("اسم دکمه و متن پاسخشو بده (فرمت: متن_دکمه|متن_پاسخ)")
    elif call.data == "send_test":
        await call.message.answer("در حال ارسال پیام تست به ربات شما...")
        user_bot = user_bots[user_id]
        try:
            await user_bot.send_message(chat_id=user_id, text="این پیام توسط ربات شما ارسال شد ✅")
            await call.message.answer("پیام تست با موفقیت ارسال شد!")
        except Exception as e:
            await call.message.answer(f"❌ خطا در ارسال پیام: {e}")

# ======= هندلر پیام دکمه جدید =======
@dp.message_handler(lambda m: "|" in m.text)
async def add_user_button(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_bots:
        await message.answer("ابتدا توکن رباتت رو بده!")
        return

    btn_text, reply_text = message.text.split("|", 1)
    user_bot = user_bots[user_id]

    # ساخت کیبورد با دکمه جدید
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(btn_text, callback_data=f"userbtn_{btn_text}")
    )
    # ذخیره دکمه ها در memory ساده
    if not hasattr(user_bot, "buttons"):
        user_bot.buttons = {}
    user_bot.buttons[btn_text] = reply_text

    await message.answer(f"✅ دکمه `{btn_text}` اضافه شد!", reply_markup=keyboard)

# ======= هندلر دکمه های کاربر =======
@dp.callback_query_handler(lambda c: c.data.startswith("userbtn_"))
async def user_buttons_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    btn_text = call.data.replace("userbtn_", "")
    user_bot = user_bots.get(user_id)
    if user_bot and hasattr(user_bot, "buttons") and btn_text in user_bot.buttons:
        await call.message.answer(user_bot.buttons[btn_text])
    else:
        await call.answer("❌ دکمه نامعتبر است!", show_alert=True)

# ======= اجرای ربات منیجر =======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    
