from typing import Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.models import Product, Category


async def orm_get_products_by_category_paginated(
    session: AsyncSession,
    category_id: int,
    page: int = 1,
    per_page: int = 5
) -> Tuple[list[Product], int]:
    """
    Возвращает продукты для категории с пагинацией и общее количество.
    """
    offset = (page - 1) * per_page

    stmt = select(Product).where(Product.category_id == category_id).offset(offset).limit(per_page)
    result = await session.execute(stmt)
    products = result.scalars().all()

    # Общее количество для пагинации
    total_result = await session.execute(
        select(func.count()).select_from(Product).where(Product.category_id == category_id)
    )
    total = total_result.scalar_one()

    return products, total

async def orm_get_parent_id_by_category_id(session: AsyncSession, category_id: int) -> int | None:
    result = await session.execute(
        select(Category.parent_id).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()

async def orm_get_product_by_id(session: AsyncSession, product_id: int) -> Product | None:
    result = await session.execute(
        select(Product)
        .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()
