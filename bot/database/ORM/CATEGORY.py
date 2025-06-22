from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Category


async def orm_get_parent_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(
        select(Category).where(Category.parent_id.is_(None))
    )
    return result.scalars().all()


async def orm_get_subcategories(session: AsyncSession, parent_id: int) -> List[Category]:
    result = await session.execute(
        select(Category).where(Category.parent_id == parent_id)
    )
    return result.scalars().all()


