from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from configs.products import PRODUCTS, PRODUCT_DETAILS
from keyboards.inline import build_product_keyboard, build_size_selection_keyboard, to_menu
from utils.helpers import delete_messages

router = Router()


async def send_product(message: Message, product_index: int, edit: bool = False):
    """Відправляє або редагує повідомлення з товаром"""
    if product_index < 0 or product_index >= len(PRODUCTS):
        return

    product = PRODUCTS[product_index]
    text = f"🔹 {product['name']}\n\n{product['description']}"
    keyboard = build_product_keyboard(product['id'], product_index, len(PRODUCTS))

    if product.get('image'):
        try:
            photo = FSInputFile(product['image'])
            if edit and message.photo:
                # Якщо це редагування і є фото
                await message.edit_media(
                    media=photo,
                    reply_markup=keyboard
                )
                await message.edit_caption(caption=text, reply_markup=keyboard)
            else:
                # Якщо це нове повідомлення або немає фото
                if edit:
                    await message.delete()
                await message.answer_photo(photo, caption=text, reply_markup=keyboard)
        except Exception:
            if edit:
                await message.edit_text(text=text, reply_markup=keyboard)
            else:
                await message.answer(text=text, reply_markup=keyboard)
    else:
        if edit:
            await message.edit_text(text=text, reply_markup=keyboard)
        else:
            await message.answer(text=text, reply_markup=keyboard)


@router.message(Command("order"))
@router.message(F.text == "Зробити замовлення")
async def show_products(message: Message, state: FSMContext):
    """Показує карусель товарів (перший товар)"""
    await delete_messages(message, state, "menu_message_id", "reminder_message_id")
    await send_product(message, 0)


@router.callback_query(F.data.startswith("show_product:"))
async def show_product(query: CallbackQuery):
    """Перемикання між товарами в каруселі"""
    product_index = int(query.data.split(":")[1])
    await send_product(query.message, product_index, edit=True)
    await query.answer()


@router.callback_query(F.data.startswith("back_to_product:"))
async def back_to_product(query: CallbackQuery):
    """Повернення до товару з вибору розміру"""
    product_id = query.data.split(":")[1]
    product_index = next((i for i, p in enumerate(PRODUCTS) if p["id"] == product_id), 0)
    await send_product(query.message, product_index, edit=True)
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
    product_index = next((i for i, p in enumerate(PRODUCTS) if p["id"] == product_id), 0)

    details = PRODUCT_DETAILS.get(product_id, "Інформація відсутня")
    keyboard = build_product_keyboard(product_id, product_index, len(PRODUCTS))

    await query.message.edit_text(details, reply_markup=keyboard)
    await query.answer()


