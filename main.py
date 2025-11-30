import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatNotFound

# --- КОНФИГУРАЦИЯ ---

# Токен берется из переменной окружения Railway.
# Убедитесь, что на Railway установлена переменная: KEY=BOT_TOKEN, VALUE=Ваш_токен
BOT_TOKEN = os.getenv('BOT_TOKEN') 

# ID канала для проверки подписки (Ваш Информатор)
CHANNEL_ID = -1003422300617 

# Ссылка на канал с мануалами (куда перенаправляем после проверки)
MANUAL_CHANNEL_LINK = "https://t.me/+A0NALNA1tltjYjIy" 

# Запасная ссылка на основной канал (на случай, если бот не может получить invite_link)
FALLBACK_CHANNEL_LINK = "https://t.me/+Ycncv5PGWvxjNmZi"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен! Бот не может запуститься.")
    exit(1)
    
# Используем ParseMode.MARKDOWN для жирного текста и ссылок
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN) 
dp = Dispatcher(bot)

# Кнопка для проверки подписки
CHECK_BUTTON = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text="✅ Я подписался, проверить доступ", callback_data="check_subscription")
)

# --- ФУНКЦИИ ПРОВЕРКИ ---

async def is_subscribed(user_id):
    """
    Проверяет статус подписки пользователя на канал. 
    Требует, чтобы бот был АДМИНИСТРАТОРОМ в канале с правом "Просмотр списка участников".
    """
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        # Статусы, означающие подписку: 'creator', 'administrator', 'member'
        return member.status in ['creator', 'administrator', 'member']
        
    except ChatNotFound:
        # Эта ошибка чаще всего означает, что бот не является администратором в канале.
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
        # Если подписан
        await message.answer( # <--- Отправляет независимое сообщение
            f"🎉 **Добро пожаловать!** Вы подписаны на наш основной канал.\n\n"
            f"Вот ваша **ссылка на мануалы**:\n"
            f"[🚀 Перейти к мануалам]({MANUAL_CHANNEL_LINK})"
        )
    else:
        # Если не подписан
        invite_link = FALLBACK_CHANNEL_LINK # Начинаем с запасной ссылки
        
        try:
            # Пытаемся получить актуальную инвайт-ссылку (только если бот админ)
            channel_info = await bot.get_chat(CHANNEL_ID)
            if channel_info.invite_link:
                 invite_link = channel_info.invite_link
        except Exception:
            # Если не получилось (например, бот не админ), используем запасную ссылку
            pass
            
        await message.answer( # <--- Отправляет независимое сообщение
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
    
    # Отправляем всплывающее уведомление о проверке
    await bot.answer_callback_query(callback_query.id, text="Проверяю подписку...", show_alert=False)
    
    if await is_subscribed(user_id):
        # Если проверка успешна
        await bot.send_message(
            user_id,
            f"✅ **Отлично!** Подписка подтверждена.\n\n"
            f"Вот ваша **ссылка на мануалы**:\n"
            f"[🚀 Перейти к мануалам]({MANUAL_CHANNEL_LINK})"
        )
        # Редактируем сообщение с кнопкой, чтобы оно выглядело завершенным
        await bot.edit_message_text(
            "✅ Доступ открыт! Нажмите /start, если потеряли ссылку.",
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
    # Запускаем бота в режиме long polling
    executor.start_polling(dp, skip_updates=True)
