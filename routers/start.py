from aiogram import Bot, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext 
from configs.start import WELCOME_TEXT, MENU_TEXT
from configs.bot import GROUP_ID, USER_TOPIC_ID
from utils.helpers import delete_messages
from keyboards.reply import menu


router = Router()
@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    await message.answer(text=WELCOME_TEXT)
    notify_msg = "🆕 Новий користувач бота 🆕\n"\
        f"Імʼя: {message.from_user.full_name}\n"\
        f"Telegram: @{message.from_user.username}\n"
    await message.bot.send_message(text=notify_msg, chat_id=GROUP_ID, message_thread_id=USER_TOPIC_ID)
    await show_menu(message, state)


@router.message(Command("menu"))
async def show_menu(message: Message, state: FSMContext):
    await state.clear()
    msg = await message.answer(text=MENU_TEXT, reply_markup=menu)
    await state.update_data(menu_message_id=msg.message_id)


@router.callback_query(F.data == "to_menu")
async def to_menu_callback(query: CallbackQuery, state: FSMContext):
    await delete_messages(query.message, state, "last_question_id", "reminder_message_id")
    msg = await query.message.answer(text=MENU_TEXT, reply_markup=menu)
    await state.update_data(menu_message_id=msg.message_id)
    