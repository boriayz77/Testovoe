from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.ORM.CARTITEM import orm_add_to_cart, orm_get_cart_by_user_id
from bot.database.ORM.CATEGORY import orm_get_parent_categories, orm_get_subcategories
from bot.database.ORM.PRODUCT import orm_get_products_by_category_paginated, orm_get_parent_id_by_category_id, \
    orm_get_product_by_id
from bot.database.models import TelegramUser
from bot.kbbs.inline.callback_data import CategoryPagination, CategoryInfo, SubCategoryPagination, ProductPagination, \
    ProductInfo, AddToCart
from bot.kbbs.inline.inline_buttons import categories_inline_paginated, subcategories_inline_paginated, \
    products_inline_paginated, get_product_action_keyboard, cart_inline_paginated
from bot.states import CartFSM

catalog_bot_router=Router()

@catalog_bot_router.callback_query(F.data == "catalog")
async def catalog_handler(callback: CallbackQuery, session: AsyncSession):
    categories = await orm_get_parent_categories(session)
    await callback.message.edit_text("📂 Выберите категорию товаров:", reply_markup=categories_inline_paginated(categories, page=1))
    await callback.answer()


@catalog_bot_router.callback_query(CategoryPagination.filter())
async def category_pagination_handler(callback: CallbackQuery, callback_data: CategoryPagination, session: AsyncSession):
    categories = await orm_get_parent_categories(session)
    await callback.message.edit_text("📂 Выберите категорию товаров:", reply_markup= categories_inline_paginated(categories, page=callback_data.page))
    await callback.answer()


@catalog_bot_router.callback_query(CategoryInfo.filter())
async def handle_category(callback: CallbackQuery, callback_data: CategoryInfo, session: AsyncSession):
    subcategories = await orm_get_subcategories(session, callback_data.category_id)

    if subcategories:
        markup = subcategories_inline_paginated(
            subcategories=subcategories,
            parent_id=callback_data.category_id,
            page=1
        )
        try:
            await callback.message.edit_text("📁 Подкатегории:", reply_markup=markup)
        except TelegramBadRequest:
            await callback.message.delete()
            await callback.message.answer("📁 Подкатегории:", reply_markup=markup)

    else:
        products, total = await orm_get_products_by_category_paginated(
            session=session,
            category_id=callback_data.category_id,
            page=1,
            per_page=5
        )

        if not products:
            await callback.answer("❌ Товары не найдены", show_alert=True)
            return

        parent_id = await orm_get_parent_id_by_category_id(session, callback_data.category_id)

        markup = products_inline_paginated(
            products=products,
            parent_id=parent_id,
            page=1,
            total=total,
            per_page=5,
            category_id=callback_data.category_id
        )
        try:
            await callback.message.edit_text("📦 Продукты:", reply_markup=markup)
        except TelegramBadRequest:
            await callback.message.delete()
            await callback.message.answer("📦 Продукты:", reply_markup=markup)

@catalog_bot_router.callback_query(AddToCart.filter())
async def handle_add_to_cart(callback: CallbackQuery, callback_data: AddToCart, state: FSMContext):
    product_id = callback_data.product_id

    await state.update_data(product_id=product_id)

    await callback.message.answer("📥 Введите количество товара:")
    await state.set_state(CartFSM.waiting_for_quantity)
    await callback.answer()



@catalog_bot_router.callback_query(SubCategoryPagination.filter())
async def subcategory_pagination_handler(callback: CallbackQuery, callback_data: SubCategoryPagination, session: AsyncSession):
    subcategories = await orm_get_subcategories(session, callback_data.parent_id)

    markup = subcategories_inline_paginated(
        subcategories=subcategories,
        parent_id=callback_data.parent_id,
        page=callback_data.page
    )

    await callback.message.edit_text("📁 Подкатегории:", reply_markup=markup)
    await callback.answer()



@catalog_bot_router.callback_query(ProductPagination.filter())
async def handle_product_page(callback: CallbackQuery, callback_data: ProductPagination, session: AsyncSession):
    products, total = await orm_get_products_by_category_paginated(
        session=session,
        category_id=callback_data.category_id,
        page=callback_data.page,
        per_page=5
    )

    if not products:
        await callback.answer("❌ Продукты не найдены", show_alert=True)
        return

    parent_id = await orm_get_parent_id_by_category_id(session, callback_data.category_id)

    markup = products_inline_paginated(
        products=products,
        parent_id=parent_id,
        category_id=callback_data.category_id,
        page=callback_data.page,
        total=total,
        per_page=5
    )

    await callback.message.edit_text("📦 Продукты:", reply_markup=markup)
    await callback.answer()

@catalog_bot_router.callback_query(ProductInfo.filter())
async def handle_product_info(callback: CallbackQuery, callback_data: ProductInfo, session: AsyncSession, bot: Bot):
    product = await orm_get_product_by_id(session, callback_data.product_id)
    if not product:
        await callback.answer("❌ Продукт не найден", show_alert=True)
        return

    await callback.message.delete()

    keyboard = get_product_action_keyboard(product.id,product.category_id)

    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo=product.photo_url,
        caption=f"{product.description} Цена: {product.price}",
        reply_markup=keyboard
    )

@catalog_bot_router.message(CartFSM.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext, session: AsyncSession,user: TelegramUser):
    quantity = int(message.text)
    if quantity <= 0:
        await message.answer("❗ Введите корректное положительное число:")
    data = await state.get_data()
    product_id = data.get("product_id")


    await orm_add_to_cart(session, user_id=user.id, product_id=product_id, quantity=quantity)
    items, total = await orm_get_cart_by_user_id(session, user_id=user.id, page=1)
    markup = cart_inline_paginated(items, page=1, total=total, per_page=5)

    await message.answer("🧺 Ваша корзина:", reply_markup=markup)

    await state.clear()


