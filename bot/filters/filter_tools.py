from aiogram import Bot
from aiogram.types import Message, CallbackQuery

from bot.kbbs.inline.inline import get_inline_keyboard
from bot.parametrs import CHANNELS


async def send_subscription_message(obj, bot, not_subscribed):
    """
    Отправляет пользователю сообщение с кнопками подписки на недостающие каналы.

    Аргументы:
        obj (Message | CallbackQuery): Объект события Telegram, откуда был вызван хендлер.
        bot (Bot): Экземпляр Telegram-бота.
        not_subscribed (list[str]): Список каналов, на которые пользователь ещё не подписан.
    """
    buttons = {f"Подписаться на канал {idx + 1}": CHANNELS[ch] for idx, ch in enumerate(not_subscribed)}
    buttons["✅ Я подписался"] = "check_subscription"
    keyboard = get_inline_keyboard(btns=buttons, sizes=(1,))

    if isinstance(obj, Message):
        await obj.answer("Для доступа к боту подпишитесь на каналы:", reply_markup=keyboard)
    elif isinstance(obj, CallbackQuery):
        await obj.message.answer("Для доступа к боту подпишитесь на каналы:", reply_markup=keyboard)


async def check_subscription(bot: Bot, user_id: int, channel: str) -> bool:
    """
    Проверяет, подписан ли пользователь на конкретный канал.

    Аргументы:
        bot (Bot): Экземпляр Telegram-бота.
        user_id (int): ID пользователя.
        channel (str): username или ID канала.

    Возвращает:
        bool: True, если пользователь подписан, иначе False.
    """
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def check_user(bot: Bot, user_id: int):
    """
    Возвращает список каналов, на которые пользователь ещё не подписан.

    Аргументы:
        bot (Bot): Экземпляр Telegram-бота.
        User_id (int): ID пользователя.

    Возвращает:
        list[str]: Список каналов, на которые пользователь не подписан.
    """
    not_subscribed = [ch for ch in CHANNELS if not await check_subscription(bot, user_id, ch)]
    return not_subscribed