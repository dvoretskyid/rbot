from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext 
from configs.support import SUPPORT_TEXT
from configs.bot import GROUP_ID, SUPPORT_TOPIC_ID
from utils.helpers import delete_messages
from keyboards.inline import support_menu, to_menu

router = Router()


@router.message(Command("help"))
@router.message(F.text == "Підтримка")
async def support(message: Message, state: FSMContext):
    await delete_messages(message, state, "menu_message_id")
    msg = await message.answer(SUPPORT_TEXT["start"], reply_markup=support_menu)
    await state.update_data(
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        support_message_id=msg.message_id
    )


@router.callback_query(F.data=="faq")
async def faq(query: CallbackQuery, state: FSMContext):
    await delete_messages(query.message, state, "support_message_id")
    await query.message.answer(SUPPORT_TEXT["faq"], reply_markup=to_menu)
    await query.answer()


@router.callback_query(F.data=="to_connect")
async def connect(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_messages(query.message, state, "support_message_id")
    current_date = datetime.now().strftime('%d.%m.%Y %H:%m')
    notify_msg = "🆘 Запит на консультацію 🆘\n"\
        f"🗓Дата та час:  {current_date}\n"\
        f"🔹Контакт: {data['full_name']} / @{data['username']}\n"
    await query.message.bot.send_message(text=notify_msg, chat_id=GROUP_ID, message_thread_id=SUPPORT_TOPIC_ID)
    await query.message.answer(SUPPORT_TEXT["answer"], reply_markup=to_menu)
    await query.answer()