from aiogram import Router, types, F
from aiogram.filters import Command
from keyboards import keyboard, cart_keyboard
from config import PAYMENT_TOKEN
from aiogram.types import LabeledPrice
import logging
from database import get_user_cart, update_user_cart, clear_user_cart, init_db

router = Router()
init_db()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRICE = {
    '1': 70000,
    '2': 55000,
    '3': 75000,
    '4': 80000,
    '5': 75000,
    '6': 75000
}

LIST = {
    '1': 'Суши с лососем',
    '2': 'Рамен',
    '3': 'Суши с креветкой',
    '4': 'Роллы с лососем',
    '5': 'Суши с тунцом',
    '6': 'Роллы с тунцом'
}


@router.message(Command('start'))
async def start(message: types.Message):
    await message.answer(
        "🍣 Добро пожаловать в Tomimo & Tokoso!\n\n"
        "Вы можете:\n"
        "1. Выбрать товары через кнопку '🛍️ Выбрать товары'\n"
        "2. Просмотреть корзину через кнопку '🛒 Корзина'",
        reply_markup=keyboard
    )


@router.message(F.text == "🛒 Корзина")
@router.message(Command('cart'))
async def show_cart(message: types.Message):
    cart = get_user_cart(message.from_user.id)
    if not cart:
        await message.answer("Ваша корзина пуста 🛒\n\nВыберите товары через кнопку '🛍️ Выбрать товары'",
                             reply_markup=keyboard)
        return

    text = "🛒 <b>Ваша корзина</b>:\n\n"
    total = 0
    for item_id, quantity in cart.items():
        item_total = PRICE[item_id] * quantity
        text += f"▪ {LIST[item_id]} x{quantity} = {item_total / 100:.2f} руб.\n"
        total += item_total

    text += f"\n<b>Итого: {total / 100:.2f} руб.</b>"
    await message.answer(text, reply_markup=cart_keyboard)


@router.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        item_id = message.web_app_data.data
        logger.info(f"Received WebApp data: {item_id}")

        if item_id not in PRICE:
            await message.answer("Товар не найден")
            return

        cart = get_user_cart(message.from_user.id)
        cart[item_id] = cart.get(item_id, 0) + 1
        update_user_cart(message.from_user.id, cart)

        await message.answer(
            f"✅ Товар '{LIST[item_id]}' добавлен в корзину!\n"
            f"Текущее количество: {cart[item_id]}\n\n"
            "Вы можете:\n"
            "1. Продолжить выбирать товары\n"
            "2. Перейти в 🛒 Корзину для оформления заказа",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in handle_web_app_data: {e}")
        await message.answer("Произошла ошибка при обработке товара")


@router.message(F.text == "💳 Оформить заказ")
async def checkout(message: types.Message):
    cart = get_user_cart(message.from_user.id)
    if not cart:
        await message.answer("Ваша корзина пуста")
        return

    labeled_prices = []
    description = "Оплата заказа:\n\n"
    total = 0

    for item_id, quantity in cart.items():
        item_total = PRICE[item_id] * quantity
        labeled_prices.append(LabeledPrice(label=f"{LIST[item_id]} x{quantity}", amount=item_total))
        description += f"{LIST[item_id]} x{quantity} - {item_total / 100:.2f} руб.\n"
        total += item_total

    description += f"\nИтого: {total / 100:.2f} руб."

    try:
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="Оплата заказа",
            description=description,
            provider_token=PAYMENT_TOKEN,
            currency="rub",
            prices=labeled_prices,
            payload="cart_payment",
            start_parameter="create_invoice"
        )
    except Exception as e:
        logger.error(f"Error in checkout: {e}")
        await message.answer("Произошла ошибка при создании платежа")


@router.message(F.text == "🗑️ Очистить корзину")
async def clear_cart(message: types.Message):
    clear_user_cart(message.from_user.id)
    await message.answer("Корзина очищена", reply_markup=keyboard)


@router.message(F.text == "⬅️ Назад в меню")
async def back_to_menu(message: types.Message):
    await message.answer("Главное меню:", reply_markup=keyboard)


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    clear_user_cart(message.from_user.id)
    await message.answer(
        "✅ Платеж успешно завершен!\n"
        "Спасибо за покупку!\n\n"
        "Ваша корзина очищена.",
        reply_markup=keyboard
    )