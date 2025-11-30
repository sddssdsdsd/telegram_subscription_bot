from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os

API_TOKEN = os.environ.get("BOT_TOKEN")  # Telegram Bot Token из Railway env
CHANNEL_USERNAME = "@ТвойКанал"          # Основной канал
MANUAL_LINK = "https://t.me/ТвойМануалКанал"  # Ссылка на мануалы

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def check_button():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub"))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"Привет! Чтобы получить доступ к мануалам, подпишись на канал {CHANNEL_USERNAME}",
        reply_markup=check_button()
    )

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status != 'left':
            await bot.send_message(user_id, f"✅ Доступ открыт: {MANUAL_LINK}")
        else:
            await bot.send_message(user_id, f"❌ Вы ещё не подписаны на {CHANNEL_USERNAME}")
    except Exception as e:
        await bot.send_message(user_id, f"❌ Ошибка проверки: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
