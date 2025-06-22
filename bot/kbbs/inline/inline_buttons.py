from typing import List

from aiogram.types import InlineKeyboardMarkup

from bot.database.models import Category, Product
from bot.kbbs.inline.callback_data import CategoryInfo, CategoryPagination, SubCategoryPagination, ProductPagination, \
    ProductInfo, AddToCart, CartRemove, CartPagination
from bot.kbbs.inline.inline import get_flex_inline_keyboard, get_inline_keyboard


def main_bot_command_start_inline()-> InlineKeyboardMarkup:
    btns = [
        [("🛍 Каталог", "catalog")],
        [("🧺 Корзина", "cart")],
        [{"text": "🔍 FAQ", "switch_inline_query_current_chat": ""}]
    ]
    return get_flex_inline_keyboard(btns=btns, sizes=(1,))

def categories_inline_paginated(
    categories: list[Category],
    page: int = 1,
    per_page: int = 5
) -> InlineKeyboardMarkup:
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = categories[start_idx:end_idx]
    total_pages = (len(categories) + per_page - 1) // per_page

    btns = []

    for cat in paginated:
        btns.append([(cat.name, CategoryInfo(category_id=cat.id).pack())])

    pagination = []
    if page > 1:
        pagination.append(("⬅️ Назад", CategoryPagination(page=page - 1).pack()))
    pagination.append((f"{page}/{total_pages} 🔄", CategoryPagination(page=page).pack()))
    if end_idx < len(categories):
        pagination.append(("Вперед ➡️", CategoryPagination(page=page + 1).pack()))

    if pagination:
        btns.append(pagination)

    btns.append([("↩ В главное меню", "back_main_menu")])

    return get_flex_inline_keyboard(btns=btns, sizes=(1,))

def subcategories_inline_paginated(
    subcategories: List[Category],
    parent_id: int,
    page: int = 1,
    per_page: int = 5
) -> InlineKeyboardMarkup:
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = subcategories[start_idx:end_idx]
    total_pages = (len(subcategories) + per_page - 1) // per_page

    btns = []

    for sub in paginated:
        btns.append([(sub.name, CategoryInfo(category_id=sub.id).pack())])  # или тут добавить CallbackData

    pagination = []
    if page > 1:
        pagination.append(("⬅️ Назад", SubCategoryPagination(parent_id=parent_id, page=page - 1).pack()))
    pagination.append((f"{page}/{total_pages}", SubCategoryPagination(parent_id=parent_id, page=page).pack()))
    if end_idx < len(subcategories):
        pagination.append(("Вперёд ➡️", SubCategoryPagination(parent_id=parent_id, page=page + 1).pack()))

    if pagination:
        btns.append(pagination)

    btns.append([("↩ Категории", CategoryPagination(page=1).pack())])

    return get_flex_inline_keyboard(btns=btns, sizes=(1,))

def products_inline_paginated(
    products: List[Product],
    parent_id: int,
    category_id:int,
    page: int,
    total: int,
    per_page: int
) -> InlineKeyboardMarkup:
    total_pages = (total + per_page - 1) // per_page

    btns = [[(product.name, ProductInfo(product_id=product.id).pack())] for product in products]

    pagination = []
    if page > 1:
        pagination.append(("⬅️ Назад", ProductPagination(category_id=category_id, page=page - 1).pack()))
    pagination.append((f"{page}/{total_pages}", ProductPagination(category_id=category_id, page=page).pack()))
    if page < total_pages:
        pagination.append(("Вперёд ➡️", ProductPagination(category_id=category_id, page=page + 1).pack()))

    if pagination:
        btns.append(pagination)

    btns.append([("↩ Подкатегории", CategoryInfo(category_id=parent_id).pack())])

    return get_flex_inline_keyboard(btns=btns, sizes=(1,))

def get_product_action_keyboard(product_id: int,category_id:int) -> InlineKeyboardMarkup:
    buttons = {
        "➕ В корзину": AddToCart(product_id=product_id).pack(),
        "↩ Подкатегории": CategoryInfo(category_id=category_id).pack(),
    }
    return get_flex_inline_keyboard(btns=buttons, sizes=(1, 1))


def cart_inline_paginated(
    items: List,
    page: int,
    total: int,
    per_page: int
) -> InlineKeyboardMarkup:
    total_pages = (total + per_page - 1) // per_page

    btns = []
    for item in items:
        btns.append([
            (f"{item.product.name} × {item.quantity}", ProductInfo(product_id=item.product.id).pack()),
            ("❌ Удалить", CartRemove(item_id=item.id).pack())
        ])

    pagination = []
    if page > 1:
        pagination.append(("⬅️ Назад", CartPagination(page=page - 1).pack()))
        pagination.append((f"{page}/{total_pages}", CartPagination(page=page).pack()))
    if page < total_pages:
        pagination.append(("Вперёд ➡️", CartPagination(page=page + 1).pack()))

    if pagination:
        btns.append(pagination)

    if items:
        btns.append([("🛒 Оформить заказ", "checkout")])

    # ⬇️ Кнопки внизу
    btns.append([("🛍 Каталог", "catalog")])
    btns.append([("↩ В главное меню", "back_main_menu")])

    return get_flex_inline_keyboard(btns=btns, sizes=(1,))


def get_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    return get_flex_inline_keyboard(
        btns=[
            [  # Первая строка — кнопка с URL
                {"text": "💳 Оплатить", "url": payment_url}
            ],
            [  # Вторая строка — возврат
                ("↩ В главное меню", "back_main_menu")
            ]
        ],
        sizes=(1,)
    )
