from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.ORM.CARTITEM import orm_delete_cart_item_by_id, orm_get_cart_by_user_id, orm_get_all_cart_by_user_id
from bot.database.ORM.ORDER import orm_create_order_from_cart
from bot.database.models import TelegramUser
from bot.kbbs.inline.callback_data import CartRemove, CartPagination
from bot.kbbs.inline.inline_buttons import cart_inline_paginated, get_payment_keyboard
from bot.payment import create_payment_from_order
from bot.states import CartFSM

cat_bot_router= Router()

@cat_bot_router.callback_query(CartRemove.filter())
async def handle_cart_remove(callback: CallbackQuery, callback_data: CartRemove, session: AsyncSession,user:TelegramUser):
    item_id = int(callback_data.item_id)
    await orm_delete_cart_item_by_id(session, item_id)

    items, total = await orm_get_cart_by_user_id(session, user_id=user.id, page=1)
    markup = cart_inline_paginated(items, page=1, total=total, per_page=5)

    await callback.message.edit_text("🧺 Ваша корзина:", reply_markup=markup)
    await callback.answer("❌ Удалено из корзины")


@cat_bot_router.callback_query(CartPagination.filter())
async def handle_cart_page(callback: CallbackQuery, callback_data: CartPagination, session: AsyncSession,user:TelegramUser):
    page = int(callback_data.page)
    items, total = await orm_get_cart_by_user_id(session, user_id=user.id, page=page)
    markup = cart_inline_paginated(items, page=page, total=total, per_page=5)

    await callback.message.edit_text("🧺 Ваша корзина:", reply_markup=markup)
    await callback.answer()

@cat_bot_router.callback_query(F.data == "checkout")
async def make_user_checkout(callback: CallbackQuery, session: AsyncSession, state: FSMContext, user: TelegramUser):
    items = await orm_get_all_cart_by_user_id(session, user_id=user.id)

    if not items:
        await callback.answer("❌ Ваша корзина пуста!", show_alert=True)
        return

    await callback.message.answer("📦 Пожалуйста, введите адрес доставки:")
    await state.set_state(CartFSM.waiting_for_address)
    await callback.answer()

@cat_bot_router.message(CartFSM.waiting_for_address)
async def process_address(message: Message, state: FSMContext, session: AsyncSession, user: TelegramUser):
    address = message.text.strip()

    if len(address) < 5:
        await message.answer("❗ Адрес слишком короткий. Пожалуйста, введите более подробно:")
        return

    try:
        order = await orm_create_order_from_cart(
            session=session,
            user_id=user.id,
            delivery_address=address,
            payment_gateway="manual"
        )
    except ValueError:
        await message.answer("❌ Ваша корзина пуста.")
        await state.clear()
        return
    payment_url = await create_payment_from_order(
        order=order,
        user_id=user.user_id,
    )
    await message.answer(
        f"✅ Заказ №{order.id} оформлен!\n"
        f"📦 Адрес доставки: {address}\n"
        f"💰 Сумма: {order.total_amount} ₽\n"
        f"<b>Перейдите к оплате ⬇️</b>",
        reply_markup=get_payment_keyboard(payment_url=payment_url)
    )

    await state.clear()
