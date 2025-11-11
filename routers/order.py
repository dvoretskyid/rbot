from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from configs.products import PRODUCTS, PRODUCT_DETAILS
from keyboards.inline import build_product_keyboard, build_size_selection_keyboard, to_menu
from utils.helpers import delete_messages

router = Router()


@router.message(Command("order"))
@router.message(F.text == "Зробити замовлення")
async def show_products(message: Message, state: FSMContext):
    """Показує карусель товарів"""
    await delete_messages(message, state, "menu_message_id", "reminder_message_id")

    # Відправляємо товари один за одним (карусель)
    for product in PRODUCTS:
        text = f"🔹 {product['name']}\n\n{product['description']}"
        keyboard = build_product_keyboard(product['id'])

        if product.get('image'):
            try:
                photo = FSInputFile(product['image'])
                await message.answer_photo(photo, caption=text, reply_markup=keyboard)
            except Exception:
                await message.answer(text=text, reply_markup=keyboard)
        else:
            await message.answer(text=text, reply_markup=keyboard)


@router.callback_query(F.data == "back_to_products")
async def back_to_products(query: CallbackQuery, state: FSMContext):
    """Повернення до списку товарів"""
    await query.message.delete()
    await show_products(query.message, state)
    await query.answer()


@router.callback_query(F.data.startswith("order_product:"))
async def order_product(query: CallbackQuery):
    """Обробка натискання кнопки 'Зробити замовлення' для товару"""
    product_id = query.data.split(":")[1]

    # Показуємо вибір розміру
    keyboard = build_size_selection_keyboard(product_id)
    await query.message.edit_text(
        "📦 Оберіть розмір:",
        reply_markup=keyboard
    )
    await query.answer()


@router.callback_query(F.data.startswith("select_size:"))
async def select_size(query: CallbackQuery):
    """Обробка вибору розміру товару"""
    _, product_id, size = query.data.split(":")

    # Тут можна додати логіку оформлення замовлення
    # Наприклад, запросити адресу доставки, контактні дані тощо
    # Поки що просто показуємо підтвердження

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if product:
        text = f"✅ Ви обрали:\n🔹 {product['name']}\n📦 Розмір: {size}\n\nЗамовлення буде оформлено найближчим часом."
        await query.message.edit_text(text, reply_markup=to_menu)

    await query.answer()


@router.callback_query(F.data.startswith("product_details:"))
async def product_details(query: CallbackQuery):
    """Показує детальну інформацію про товар"""
    product_id = query.data.split(":")[1]

    details = PRODUCT_DETAILS.get(product_id, "Інформація відсутня")
    keyboard = build_product_keyboard(product_id)

    await query.message.edit_text(details, reply_markup=keyboard)
    await query.answer()


