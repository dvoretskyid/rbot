from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продовжити", callback_data="popup_confirm"),
     InlineKeyboardButton(text="До меню", callback_data="to_menu")]
])