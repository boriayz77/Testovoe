import logging

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import TelegramUser


async def orm_add_get_user(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> TelegramUser:
    try:
        query = select(TelegramUser).where(TelegramUser.user_id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        if user is None:
            user = TelegramUser(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            await session.commit()
        else:
            updated = False

            if user.first_name != first_name:
                user.first_name = first_name
                updated = True

            if user.last_name != last_name:
                user.last_name = last_name
                updated = True

            if user.username != username:
                user.username = username
                updated = True

            if user.banned:
                user.banned = False
                updated = True

            if updated:
                await session.commit()
                logging.info(f"🔄 Данные пользователя {user_id} обновлены.")

        return user

    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"❌ Ошибка при добавлении/обновлении пользователя {user_id}: {e}")
        raise


async def orm_get_user(
        session: AsyncSession,
        user_id: int,
):
    try:
        query = select(TelegramUser).where(TelegramUser.user_id == user_id)
        result = await session.execute(query)

        return result.scalars().first()
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Ошибка при добавлении пользователя: {e}")
        raise

async def set_magnet_lead(session: AsyncSession, user_id: int, magnet_lead_video: str) -> None:
       try:
        int(user_id)
        query = (
            update(TelegramUser)
            .where(TelegramUser.user_id == user_id)
            .values(
                magnet_lead_video=magnet_lead_video,
            )
        )
        await session.execute(query)
        await session.commit()
       except SQLAlchemyError as e:
           await session.rollback()
           logging.error(f"Ошибка при добавлении пользователя: {e}")
           raise

async def orm_get_all_user(
        session: AsyncSession
):
    try:
        query = select(TelegramUser.user_id).filter((TelegramUser.banned == False) | (TelegramUser.banned == None))
        result = await session.execute(query)

        return result.scalars().all()
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Ошибка при поиске пользователя: {e}")
        raise


async def orm_set_user_banned(
        session: AsyncSession,
        user_id: int
):
    try:
        # Получаем пользователя по user_id
        query = select(TelegramUser).filter(TelegramUser.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        # Если пользователь найден, обновляем поле banned
        if user:
            user.banned = True
            await session.commit()
            return user
        else:
            logging.error(f"Пользователь с user_id {user_id} не найден")
            return None
    except SQLAlchemyError as e:
        await session.rollback()
        logging.error(f"Ошибка при обновлении пользователя: {e}")
        raise
