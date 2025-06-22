
from aiogram import Bot, types
from aiogram.filters import BaseFilter

from bot.filters.filter_tools import check_user, send_subscription_message


class IsSubscriber(BaseFilter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    async def __call__(self, obj, bot: Bot) -> bool:
        if isinstance(obj, types.Message):
            user_id = obj.from_user.id
        elif isinstance(obj, types.CallbackQuery):
            user_id = obj.from_user.id
            await obj.answer()
        else:
            return True

        not_subscribed = await check_user(bot, user_id)

        if not not_subscribed:
            return True

        await send_subscription_message(obj, bot, not_subscribed)
        return False

