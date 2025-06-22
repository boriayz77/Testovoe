import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.database.ORM.USERS import orm_add_get_user


def extract_user_from_event(event: TelegramObject):
    for attr in ("from_user", "message", "callback_query", "inline_query", "chat_member"):
        value = getattr(event, attr, None)
        if hasattr(value, "from_user"):
            return value.from_user
    return getattr(event, "from_user", None)


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session

            tg_user = extract_user_from_event(event)
            if tg_user:
                try:
                    db_user = await orm_add_get_user(
                        session=session,
                        user_id=tg_user.id,
                        username=tg_user.username,
                        first_name=tg_user.first_name,
                        last_name=tg_user.last_name,
                    )
                    data["user"] = db_user
                except Exception as e:
                    logging.error(e)

            return await handler(event, data)