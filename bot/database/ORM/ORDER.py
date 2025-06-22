import logging
from decimal import Decimal
from io import BytesIO

import openpyxl
from aiogram.types import BufferedInputFile
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.database.ORM.USERS import orm_get_user
from bot.database.models import OrderItem, Order, CartItem


async def orm_create_order_from_cart(
    session: AsyncSession,
    user_id: int,
    delivery_address: str,
    payment_gateway: str = "t-bank"
) -> Order:
    stmt = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        raise ValueError("Корзина пуста")

    total = 0
    for item in cart_items:
        total += item.quantity * float(item.product.price)

    order = Order(
        user_id=user_id,
        delivery_address=delivery_address,
        payment_gateway=payment_gateway,
        total_amount=Decimal(total)
    )
    session.add(order)
    await session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            quantity=item.quantity
        )
        session.add(order_item)

    for item in cart_items:
        await session.delete(item)

    await session.commit()

    await session.refresh(order, ['items'])  # загружаем order.items
    for item in order.items:
        await session.refresh(item, ['product'])  # загружаем item.product

    return order

async def export_order_to_excel_by_user(
    session: AsyncSession,
    order_id: int,
    user_id: int
) -> BytesIO:
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.user_id == user_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError("❌ Заказ не найден или не принадлежит пользователю")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Заказ №{order.id}"

    headers = ["ID заказа", "Пользователь", "Адрес", "Дата", "Сумма", "Оплачен?", "Товар", "Кол-во", "Цена за шт."]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for item in order.items:
        ws.append([
            order.id,
            order.user_id,
            order.delivery_address,
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            float(order.total_amount),
            "Да" if order.is_paid else "Нет",
            item.product.name,
            item.quantity,
            float(item.product.price)
        ])

    file = BytesIO()
    wb.save(file)
    file.seek(0)
    return file


async def orm_process_payment(session: AsyncSession, order_id: int, user_id: int) -> BufferedInputFile:
    """
    Обрабатывает успешную оплату:
    - находит заказ
    - помечает как оплаченный
    - возвращает Excel-файл для отправки пользователю
    """
    user= await orm_get_user(session, user_id)
    user_id=user.id
    stmt = select(Order).where(Order.id == order_id, Order.user_id == user_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"❌ Заказ {order_id} не найден или не принадлежит пользователю {user_id}")

    if not order.is_paid:
        order.is_paid = True
        await session.commit()
        logging.info(f"💰 Заказ {order.id} оплачен.")

    excel_file = await export_order_to_excel_by_user(session, order_id, user_id)
    return BufferedInputFile(excel_file.read(), filename=f"order_{order.id}.xlsx")