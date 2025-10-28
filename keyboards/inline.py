from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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