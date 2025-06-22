
from aiogram.filters.callback_data import CallbackData


class CategoryInfo(CallbackData, prefix="category_info"):
    category_id: int

class CategoryPagination(CallbackData, prefix="category_page"):
    page: int

class SubCategoryPagination(CallbackData, prefix="subcategory_page"):
    parent_id: int
    page: int

class ProductInfo(CallbackData, prefix="product"):
    product_id: int

class ProductPagination(CallbackData, prefix="products_page"):
    category_id: int
    page: int
class AddToCart(CallbackData, prefix="add_cart"):
    product_id: int

class CartPagination(CallbackData, prefix="cart_page"):
    page: int

class CartRemove(CallbackData, prefix="cart_remove"):
    item_id: int
