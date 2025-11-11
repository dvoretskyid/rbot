from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Зробити замовлення"), KeyboardButton(text="Підтримка")],
], resize_keyboard=True)

hide_menu = ReplyKeyboardRemove()

send_phone_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Надіслати контакт", request_contact=True)]
], resize_keyboard=True)

def build_reply_keyboard(values:list, lenght:int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for val in values:
        builder.button(text=val)
    builder.adjust(lenght)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

