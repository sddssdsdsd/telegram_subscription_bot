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

# Ссылка на основной канал (используется как запасная и для кнопки)
FALLBACK_CHANNEL_LINK = "https://t.me/+Ycncv5PGWvxjNmZi"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен! Бот не может запуститься.")
    exit(1)
    
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN) 
dp = Dispatcher(bot)

# Клавиатура для НЕ подписанного пользователя (только кнопка проверки)
CHECK_BUTTON = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text="✅ Я подписался, проверить доступ", callback_data="check_subscription")
)

# Клавиатура для ПОДПИСАННОГО пользователя (кнопки с прямыми ссылками)
SUBSCRIBED_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
# 1. Кнопка с мануалами
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="🚀 Перейти к мануалам", url=MANUAL_CHANNEL_LINK)
)
# 2. Кнопка с основным каналом
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
    """Обрабатывает команду /start, отправляя независимое сообщение (answer)."""
    user_id = message.from_user.id
    
    if await is_subscribed(user_id):
        # Если подписан - выводим две кнопки с прямыми ссылками
        await message.answer(
            f"🎉 **Добро пожаловать!** Вы подписаны на наш основной канал.\n\n"
            f"Выберите, куда вы хотите перейти:",
            reply_markup=SUBSCRIBED_KEYBOARD
        )
    else:
        # Если не подписан - выводим одну кнопку проверки
        invite_link = FALLBACK_CHANNEL_LINK
        
        try:
            channel_info = await bot.get_chat(CHANNEL_ID)
            if channel_info.invite_link:
                 invite_link = channel_info.invite_link
        except Exception:
            pass
            
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
        # Если проверка успешна
        await bot.send_message(
            user_id,
            f"✅ **Отлично!** Подписка подтверждена.\n\n"
            f"Выберите, куда вы хотите перейти:",
            reply_markup=SUBSCRIBED_KEYBOARD # <--- Выводим две кнопки
        )
        # Редактируем сообщение с кнопкой проверки, чтобы убрать ее
        await bot.edit_message_text(
            "✅ Доступ открыт! Нажмите /start, если потеряли ссылки.",
            callback_query.from_user.id,
            callback_query.message.message_id
        )
    else:
        # Если подписка не найдена
        await bot.send_message(
            user_id, 
            "❌ Подписка не найдена. Убедитесь, что вы **подписаны** на основной канал и попробуйте снова."
        )

# --- ЗАПУСК БОТА ---

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
