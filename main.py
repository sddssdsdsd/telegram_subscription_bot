import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import ChatNotFound

# --- КОНФИГУРАЦИЯ ---

BOT_TOKEN = os.getenv('BOT_TOKEN') 
CHANNEL_ID = -1003422300617 
MANUAL_CHANNEL_LINK = "https://t.me/+A0NALNA1tltjYjIy" 
FALLBACK_CHANNEL_LINK = "https://t.me/+UCv7qEQLX-wxZDE6" 
PHOTO_FILE_ID = "AgACAgIAAxkBAAE-j_ZpK81Rtgm5SohtE1bMtI0XB_YHKQACCAtrG-zcYEn1PjRKletkuwEAAwIAA3kAAzYE" 

CONTACT_USERNAME = "antoha666s"
CONTACT_LINK = f"https://t.me/{CONTACT_USERNAME}"
# ----------------------------------------------------------------------

# --- КОНСТАНТЫ ТАРИФОВ (ДЛЯ КРАСИВОГО ОФОРМЛЕНИЯ) ---

# --- ИСПОЛЬЗУЕМ ➖➖➖➖➖➖➖➖➖➖ ДЛЯ РАЗДЕЛЕНИЯ ---

TARIFF_50_DESC = (
    "**1. Доступ в Приват**\n"
    "💰 **Цена:** 50$\n\n"
    "➖➖➖➖➖➖➖➖➖➖\n" # <-- Разделитель
    "**Вы получаете:**\n"
    "• Полную библиотеку материалов\n"
    "• Закрытые кейсы и методички\n"
    "• Обновления, схемы, рабочие пайплайны\n"
    "• Чат участников, Техническую поддержку\n"
    "• Эксклюзивную информацию, которой нет в открытом доступе\n"
    "• Мини-гайды по DA, SPS, NDP, SBS\n\n"
    "➖➖➖➖➖➖➖➖➖➖\n" # <-- Разделитель
    "***Подходит тем, кто хочет войти в нишу и работать самостоятельно.***"
)

TARIFF_100_DESC = (
    "**2. Личное введение — Индивидуальная работа**\n"
    "💰 **Цена:** 100$\n\n"
    "➖➖➖➖➖➖➖➖➖➖\n" # <-- Разделитель
    "**Вы получаете:**\n"
    "• Ведение *1-на-1*\n"
    "• Полную настройку ComfyUI и LoRA (MIU)\n"
    "• Разбор контента, персонажа, аккаунтов\n"
    "• Постановку Production Flow, Настройку всей воронки (SBS)\n"
    "• Монетизацию и разбор Fanvue\n"
    "• **Совместную работу по видеосвязи**\n"
    "• Коррекцию ошибок, Сопровождение до результата\n\n"
    "➖➖➖➖➖➖➖➖➖➖\n" # <-- Разделитель
    "***Это путь для тех, кто хочет максимально быстрый и точный старт.***"
)

# --- НАСТРОЙКА И ИНИЦИАЛИЗАЦИЯ ---

logging.basicConfig(level=logging.INFO)

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен! Бот не может запуститься.")
    exit(1)
    
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.MARKDOWN) 
dp = Dispatcher(bot)

# --- КЛАВИАТУРЫ ---

# 1. Клавиатура для НЕ подписанного пользователя
CHECK_BUTTON = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(text="✅ Я подписался, проверить доступ", callback_data="check_subscription")
)

# 2. Клавиатура для ВЫБОРА ТАРИФА (Кнопки 50$ и 100$)
TARIFF_CHOICE_KEYBOARD = types.InlineKeyboardMarkup(row_width=2)
TARIFF_CHOICE_KEYBOARD.row(
    types.InlineKeyboardButton(text="50$", callback_data="show_tariff_50"),
    types.InlineKeyboardButton(text="100$", callback_data="show_tariff_100")
)

# 3. Клавиатура для ПОДПИСАННОГО пользователя (главное меню)
SUBSCRIBED_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="🚀 Перейти к мануалам", url=MANUAL_CHANNEL_LINK)
)
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="➡️ Перейти к основному каналу", url=FALLBACK_CHANNEL_LINK)
)
SUBSCRIBED_KEYBOARD.add(
    types.InlineKeyboardButton(text="🔒 Приватное комьюнити", callback_data="private_community")
)

# 4. Клавиатура для ПОКУПКИ (Подробное описание тарифа)
PURCHASE_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
PURCHASE_KEYBOARD.add(
    types.InlineKeyboardButton(text="🔥 КУПИТЬ ДОСТУП ", url=CONTACT_LINK)
)
PURCHASE_KEYBOARD.add(
    types.InlineKeyboardButton(text="⬅️ Назад к меню", callback_data="back_to_menu")
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

# Хендлер для /start и для кнопки "Назад к меню"
@dp.message_handler(commands=['start'])
@dp.callback_query_handler(lambda c: c.data == 'back_to_menu')
async def send_welcome_or_menu(item: types.Message | types.CallbackQuery):
    """Обрабатывает /start и возврат в главное меню."""
    if isinstance(item, types.CallbackQuery):
        await bot.answer_callback_query(item.id)
        message = item.message
        user_id = item.from_user.id
    else:
        message = item
        user_id = item.from_user.id

    # 1. Отправляем фото только при /start, не при возврате из меню
    if isinstance(item, types.Message):
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=PHOTO_FILE_ID,
                caption="**САМЫЙ ЛУЧШИЙ ГАЙД НА OFM МОДЕЛИ**" 
            )
        except Exception as e:
            logging.error(f"Не удалось отправить фото {PHOTO_FILE_ID} пользователю {user_id}: {e}")
            
    # 2. Отправляем текст с кнопками
    if await is_subscribed(user_id):
        # Если подписан
        welcome_text = (
            f"🎉 **Добро пожаловать!** Вы подписаны на наш основной канал.\n\n"
            f"Выберите, куда вы хотите перейти:"
        )
        if isinstance(item, types.CallbackQuery):
             # Редактируем сообщение, если это был возврат из меню
            await bot.edit_message_text(
                welcome_text,
                user_id,
                message.message_id,
                reply_markup=SUBSCRIBED_KEYBOARD 
            )
        else:
            # Отправляем новое сообщение, если это /start
            await message.answer(welcome_text, reply_markup=SUBSCRIBED_KEYBOARD)

    else:
        # Если не подписан
        invite_link = FALLBACK_CHANNEL_LINK 
        
        await message.answer(
            f"✋ **Доступ ограничен.**\n\n"
            f"Для доступа к мануалам, пожалуйста, **подпишитесь на наш основной канал**:\n"
            f"👉 {invite_link}\n\n"
            f"После подписки нажмите кнопку ниже.",
            reply_markup=CHECK_BUTTON,
            disable_web_page_preview=True
        )

# Обработчик кнопки "Приватное комьюнити" (Выбор тарифа)
@dp.callback_query_handler(lambda c: c.data == 'private_community')
async def process_private_community(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id) 

    text = (
        "**ГОТОВЫ НАСТРОИТТЬ ПРОЕКТ ПРАВИЛЬНО?**\n\n"
        "Реальная прибыль лежит в деталях, которые не публикуются открыто: *Параметры LoRA, Алгоритмы обхода теневых фильтров, Структура общения для удержания платников.* \n\n"
        "➖➖➖➖➖➖➖➖➖➖\n" # <-- Добавлен разделитель
        "Выберите ваш тариф:"
    )
    
    # Редактируем текущее сообщение, чтобы показать выбор тарифов
    await bot.edit_message_text(
        text,
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=TARIFF_CHOICE_KEYBOARD, # <--- Кнопки 50$ и 100$
        disable_web_page_preview=True 
    )

# Обработчик выбора конкретного тарифа (50$ или 100$)
@dp.callback_query_handler(lambda c: c.data.startswith('show_tariff_'))
async def process_show_tariff(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id) 

    tariff_type = callback_query.data.split('_')[2]
    
    if tariff_type == '50':
        desc = TARIFF_50_DESC
    elif tariff_type == '100':
        desc = TARIFF_100_DESC
    else:
        return

    full_text = (
        "--- ПРИВАТНОЕ КОМЬЮНИТИ ---\n\n"
        f"{desc}\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n" # <-- Добавлен разделитель
        "❗️ **ВАЖНО**\n"
        "Покупка проходит только через личные сообщения. Проверьте юзернейм перед оплатой @antoha666s"
    )

    # Редактируем текущее сообщение, чтобы показать полное описание и кнопки покупки/назад
    await bot.edit_message_text(
        full_text,
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=PURCHASE_KEYBOARD # <--- Кнопки "Купить" и "Назад"
    )

# Обработчик проверки подписки (Callback)
@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def process_callback_check(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    await bot.answer_callback_query(callback_query.id, text="Проверяю подписку...", show_alert=False)
    
    if await is_subscribed(user_id):
        # Редактируем сообщение, чтобы убрать старую кнопку проверки
        await bot.edit_message_text(
            f"✅ **Отлично!** Подписка подтверждена.\n\nВыберите, куда вы хотите перейти:",
            user_id,
            callback_query.message.message_id,
            reply_markup=SUBSCRIBED_KEYBOARD 
        )
    else:
        await bot.send_message(
            user_id, 
            "❌ Подписка не найдена. Убедитесь, что вы **подписаны** на основной канал и попробуйте снова."
        )


# --- ЗАПУСК БОТА ---

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
