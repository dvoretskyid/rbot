from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()


@router.message(Command("order"))
async def pay_command(message: Message):
    url = "https://secure.wayforpay.com/button/bb2107d545f0f"
    pay_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Pay", url=url), InlineKeyboardButton(text="До меню", callback_data="to_menu")]])
    await message.answer(text="Тестова оплата", reply_markup=pay_btn)


