from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.ORM.USERS import orm_get_user
from bot.database.models import CartItem


async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int, quantity: int = 1):

    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    item = result.scalar_one_or_none()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        session.add(item)

    await session.commit()


async def orm_get_cart_by_user_id(
        session: AsyncSession,
        user_id: int,
        page: int = 1,
        per_page: int = 5
) -> tuple[list[CartItem], int]:
    """
    Возвращает элементы корзины пользователя с пагинацией.

    :param session: SQLAlchemy сессия
    :param user_id: ID пользователя
    :param page: номер страницы
    :param per_page: количество записей на странице
    :return: (список элементов корзины, общее количество элементов)
    """


    offset = (page - 1) * per_page

    stmt = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
        .offset(offset)
        .limit(per_page)
    )
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    # Считаем общее количество
    total_stmt = select(func.count()).select_from(CartItem).where(CartItem.user_id == user_id)
    total = (await session.execute(total_stmt)).scalar_one()

    return cart_items, total


async def orm_delete_cart_item_by_id(session: AsyncSession, item_id: int):
    stmt = select(CartItem).where(CartItem.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if item:
        await session.delete(item)
        await session.commit()


async def orm_get_all_cart_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> List[CartItem]:
    """
    Возвращает все элементы корзины пользователя.
    """
    stmt = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    result = await session.execute(stmt)
    return result.scalars().all()



