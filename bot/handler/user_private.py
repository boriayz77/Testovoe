from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.ORM.CARTITEM import orm_get_cart_by_user_id
from bot.database.models import TelegramUser
from bot.filters.isSubscribe import IsSubscriber
from bot.handler.user_cat import cat_bot_router
from bot.handler.user_catalog import catalog_bot_router
from bot.kbbs.inline.inline_buttons import main_bot_command_start_inline, cart_inline_paginated
from bot.message_answer import main_bot_command_start_message

main_bot_router=Router()
main_bot_router.include_routers(
    catalog_bot_router,
            cat_bot_router

)
main_bot_router.message.filter(IsSubscriber())
main_bot_router.callback_query.filter(IsSubscriber())

@main_bot_router.message(CommandStart())
async def main_bot_command_start(message: Message, bot: Bot):
    user=message.from_user
    await message.answer(main_bot_command_start_message(user.first_name),reply_markup=main_bot_command_start_inline())

@main_bot_router.callback_query(F.data=="check_subscription")
async def check_subscription(callback: CallbackQuery):
    user=callback.from_user
    await callback.message.answer(main_bot_command_start_message(user.first_name),reply_markup=main_bot_command_start_inline())
    await callback.answer()

@main_bot_router.callback_query(F.data=="back_main_menu")
async def back_main_menu(callback: CallbackQuery):
    user=callback.from_user
    await callback.message.edit_text(main_bot_command_start_message(user.first_name),reply_markup=main_bot_command_start_inline())
    await callback.answer()

@main_bot_router.callback_query(F.data=="cart")
async def cart(callback: CallbackQuery,session: AsyncSession,user: TelegramUser):
    items, total = await orm_get_cart_by_user_id(session, user_id=user.id, page=1)
    markup = cart_inline_paginated(items, page=1, total=total, per_page=5)

    await callback.message.edit_text("🧺 Ваша корзина:", reply_markup=markup)
