from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from configs.popup import POP_UP_LOCATION
from urllib.parse import urlencode

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


def build_popup_final_keyboard(date: str) -> InlineKeyboardMarkup:
    """
    Створює клавіатуру для фінального повідомлення з кнопками додавання в календар та повернення в меню.

    Args:
        date: Дата у форматі "DD.MM" (наприклад, "31.10")

    Returns:
        InlineKeyboardMarkup з двома кнопками
    """
    day, month = date.split(".")
    year = datetime.now().strftime('%Y')

    start_datetime = f"{year}{month.zfill(2)}{day.zfill(2)}T150000"
    end_datetime = f"{year}{month.zfill(2)}{day.zfill(2)}T200000"

    # Параметри для Google Calendar
    calendar_params = {
        'action': 'TEMPLATE',
        'text': 'REASONANCE Pop-Up',
        'dates': f"{start_datetime}/{end_datetime}",
        'details': 'Відчуй REASONANCE – познайомся з ароматами ближче на нашому pop-up',
        'location': f'{POP_UP_LOCATION}',
        'ctz': 'Europe/Kiev'
    }

    calendar_url = f"https://calendar.google.com/calendar/render?{urlencode(calendar_params)}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Додати в календар", url=calendar_url),
        InlineKeyboardButton(text="До меню", callback_data="to_menu")]
    ])