from typing import Union

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from validators import url as is_valid_url

def get_inline_keyboard(
    *,
    btns: dict[str, str] | list[list[tuple[str, str]]],
    sizes: tuple[int, ...] = (2,)
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    if isinstance(btns, dict):
        for text, value in btns.items():
            if not value:
                continue
            if is_valid_url(value):
                keyboard.add(InlineKeyboardButton(text=text, url=value))
            else:
                keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
        if sizes:
            keyboard.adjust(*sizes)

    elif isinstance(btns, list):
        for row in btns:
            buttons = []
            for text, value in row:
                if not value or not isinstance(value, str):
                    continue
                if is_valid_url(value):
                    buttons.append(InlineKeyboardButton(text=text, url=value))
                else:
                    buttons.append(InlineKeyboardButton(text=text, callback_data=value))
            if buttons:
                keyboard.row(*buttons)

    return keyboard.as_markup()




def get_flex_inline_keyboard(
    *,
    btns: Union[dict[str, str], list[list[Union[tuple[str, str], dict]]]],
    sizes: tuple[int, ...] = (2,)
) -> InlineKeyboardMarkup:
    """
    Создает расширенную Inline-клавиатуру с поддержкой URL, callback и inline query-кнопок.

    Аргументы:
        btns (dict[str, str] | list[list[tuple | dict]]): кнопки
        sizes (tuple[int, ...]): Размерность строк (если передан dict)

    Возвращает:
        InlineKeyboardMarkup: готовая клавиатура
    """
    keyboard = InlineKeyboardBuilder()

    if isinstance(btns, dict):
        for text, value in btns.items():
            if not value:
                continue
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
        return keyboard.adjust(*sizes).as_markup()

    elif isinstance(btns, list):
        for row in btns:
            buttons = []
            for btn in row:
                if isinstance(btn, tuple):
                    text, value = btn
                    buttons.append(InlineKeyboardButton(text=text, callback_data=value))
                elif isinstance(btn, dict):
                    buttons.append(InlineKeyboardButton(**btn))
            if buttons:
                keyboard.row(*buttons)

        return keyboard.as_markup()

    return InlineKeyboardMarkup(inline_keyboard=[])


