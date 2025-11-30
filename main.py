import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatNotFound

# --- КОНФИГУРАЦИЯ ---

# Токен берется из переменной окружения Railway.
BOT_TOKEN = os.getenv('BOT_TOKEN') 

# ID канала для проверки подписки (Ваш Информатор)
CHANNEL_ID = -1003422300617 

# Ссылка на канал с мануалами
MANUAL_CHANNEL_LINK = "https://t.me/+A0NALNA1tltjYjIy" 

# Ссылка на основной канал (ЭТА ССЫЛКА БУДЕТ ИСПОЛЬЗОВАТЬСЯ ПРИНУДИТЕЛЬНО!)
FALLBACK_CHANNEL_LINK = "https://t.me/+UCv7qEQLX-wxZDE6" # <--- ОБНОВЛЕНА
# ----------------------------------------------------------------------

# ID фото, которое будет отправляться в начале. (ВЗЯТО ИЗ ВАШЕГО НОВОГО JSON)
# Если возникнут ошибки, вам потребуется получить новый file_id, отправив фото напрямую боту.
PHOTO_FILE_ID = "AgACAgIAAxkBAAE-j_ZpK81Rtgm5SohtE1bMtI0XB_YHKQACCAtrG-zcYEn1PjRKletkuwEAAwIAA3kAAzYE" 
# ----------------------------------------------------------------------

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен! Бот не может запуститься.")
    exit(1)
    
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN) 
dp = Dispatcher(bot)

# Клавиатура для НЕ подписанного пользователя
CHECK_BUTTON = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text="✅ Я подписался, проверить доступ", callback_data="check_subscription")
)

# Клавиатура для ПОДПИСАННОГО пользователя
SUBSCRIBED_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="🚀 Перейти к мануалам", url=MANUAL_CHANNEL_LINK)
)
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="➡️ Перейти к основному каналу", url=FALLBACK_CHANNEL_LINK)
)

# --- ФУНКЦИИ ПРОВЕРКИ ---

async def is_subscribed(user_id):
    """Проверяет статус подписки пользователя на канал."""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
        
    except ChatNotFound:
        logging.error(f"ChatNotFound для ID: {CHANNEL_ID}. Проверьте права бота в канале.")
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки для пользователя {user_id}: {e}")
        return False

# --- ОБРАБОТЧИКИ КОМАНД И КНОПОК ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Обрабатывает команду /start: сначала отправляет фото, затем текст с кнопками."""
    user_id = message.from_user.id
    
    # 1. Отправляем фото
    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=PHOTO_FILE_ID,
            caption="**САМЫЙ ЛУЧШИЙ ГАЙД НА OFM МОДЕЛИ**" # Подпись под фото
        )
    except Exception as e:
        # Если фото не отправилось (Wrong file identifier), продолжаем без него.
        logging.error(f"Не удалось отправить фото {PHOTO_FILE_ID} пользователю {user_id}: {e}")
        
    # 2. Затем отправляем текст с кнопками (как обычно)
    if await is_subscribed(user_id):
        await message.answer(
            f"🎉 **Добро пожаловать!** Вы подписаны на наш основной канал.\n\n"
            f"Выберите, куда вы хотите перейти:",
            reply_markup=SUBSCRIBED_KEYBOARD 
        )
    else:
        invite_link = FALLBACK_CHANNEL_LINK 
        
        await message.answer(
            f"✋ **Доступ ограничен.**\n\n"
            f"Для получения доступа к мануалам, пожалуйста, **подпишитесь на наш основной канал**:\n"
            f"👉 {invite_link}\n\n"
            f"После подписки нажмите кнопку ниже.",
            reply_markup=CHECK_BUTTON,
            disable_web_page_preview=True
        )

@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def process_callback_check(callback_query: types.CallbackQuery):
    """Обрабатывает нажатие кнопки проверки подписки."""
    user_id = callback_query.from_user.id
    
    await bot.answer_callback_query(callback_query.id, text="Проверяю подписку...", show_alert=False)
    
    if await is_subscribed(user_id):
        await bot.send_message(
            user_id,
            f"✅ **Отлично!** Подписка подтверждена.\n\n"
            f"Выберите, куда вы хотите перейти:",
            reply_markup=SUBSCRIBED_KEYBOARD 
        )

        await bot.edit_message_text(
            "✅ Доступ открыт! Нажмите /start, если потеряли ссылки.",
            callback_query.from_user.id,
            callback_query.message.message_id
        )
    else:
        await bot.send_message(
            user_id, 
            "❌ Подписка не найдена. Убедитесь, что вы **подписаны** на основной канал и попробуйте снова."
        )

# --- ЗАПУСК БОТА ---

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
