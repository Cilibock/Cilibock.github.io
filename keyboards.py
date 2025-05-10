from aiogram.types import (
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)

web_app = WebAppInfo(url="https://cilibock.github.io/")

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍️ Выбрать товары", web_app=web_app)],
        [KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

cart_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оформить заказ")],
        [KeyboardButton(text="🗑️ Очистить корзину")],
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True
)