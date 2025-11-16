from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.products import PRODUCTS

confirm_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продовжити", callback_data="popup_confirm"),
     InlineKeyboardButton(text="До меню", callback_data="to_menu")]
])

to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="До меню", callback_data="to_menu")]
])

support_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Доставка та оплата", callback_data="faq")],
    [InlineKeyboardButton(text="Звʼязатися зі мною", callback_data="to_connect")],
    [InlineKeyboardButton(text="До меню", callback_data="to_menu")]
])


def build_popup_final_keyboard() -> InlineKeyboardMarkup:
    """
    Створює клавіатуру для фінального повідомлення з кнопками додавання в календар та повернення в меню.

    Returns:
        InlineKeyboardMarkup з двома кнопками
    """
    # Пряме посилання на повторювану подію в Google Calendar (31.10-02.11)
    calendar_url = "https://calendar.app.google/1BN2NgxouqWiH6VYA"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Додати в календар", url=calendar_url),
        InlineKeyboardButton(text="До меню", callback_data="to_menu")]
    ])


def build_product_keyboard(product_id: str, current_index: int, total_products: int) -> InlineKeyboardMarkup:
    """
    Створює клавіатуру для товару з кнопками "Зробити замовлення" та "Дізнатися детальніше"
    """
    buttons = [
        [InlineKeyboardButton(text="🛒 Зробити замовлення", callback_data=f"order_product:{product_id}")],
        [InlineKeyboardButton(text="ℹ️ Дізнатися детальніше", callback_data=f"product_details:{product_id}")]
    ]

    # Додаємо кнопки навігації
    navigation = []
    if current_index > 0:
        prev_index = current_index - 1
        navigation.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"show_product:{prev_index}"))

    if current_index < total_products - 1:
        next_index = current_index + 1
        navigation.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"show_product:{next_index}"))

    if navigation:
        buttons.append(navigation)

    buttons.append([InlineKeyboardButton(text="🏠 До меню", callback_data="to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_size_selection_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """
    Створює клавіатуру для вибору розміру товару
    """
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return to_menu

    buttons = []
    for size_info in product["sizes"]:
        size = size_info["size"]
        buttons.append([InlineKeyboardButton(
            text=f"📦 {size}",
            callback_data=f"select_size:{product_id}:{size}"
        )])

    buttons.append([InlineKeyboardButton(text="◀️ Назад до товару", callback_data=f"back_to_product:{product_id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)