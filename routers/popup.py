from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from configs.popup import POPUP_START_TEXT, POPUP_START_GIF, ASK_NAME, ASK_PHONE, ASK_EMAIL, POPUP_END_TEXT, POP_UP_LOCATION, POP_UP_DATE
from configs.bot import GROUP_ID, POPUP_TOPIC_ID
from keyboards.reply import hide_menu, send_phone_keyboard
from keyboards.inline import build_popup_final_keyboard
from utils.helpers import delete_messages, ask_question, validate, handle_invalid_answer
from utils.states import PopUpForm
from database.requests import save_popup_registration, get_popup_by_telegram_id

router = Router()


@router.callback_query(F.data == "popup_confirm")
async def popup_confirm_callback(query, state: FSMContext):
    await query.message.delete()
    await query.answer()


# Команда та кнопка POP-UP приховані
# @router.message(Command("popup"))
# @router.message(F.text == "POP-UP")
async def start(message: Message, state: FSMContext):
    await delete_messages(message, state, "menu_message_id", "reminder_message_id")
    # existing_registrations = await get_popup_by_telegram_id(message.from_user.id)
    existing_registrations = False
    if existing_registrations:
        registration = existing_registrations[0]
        await state.update_data(
            name=registration.name,
            phone=registration.phone,
            email=registration.email
        )
        await final(message, state)
        return

    # Відправляємо відео (GIF) з текстом
    try:
        from aiogram.types import FSInputFile
        video = FSInputFile(POPUP_START_GIF)
        await message.answer_video(video, caption=POPUP_START_TEXT)
    except Exception as e:
        # Якщо відео не знайдено, відправляємо тільки текст
        await message.answer(text=POPUP_START_TEXT)

    await ask_question(message, state, ASK_NAME["valid"])
    await state.set_state(PopUpForm.name)


@router.message(PopUpForm.name)
async def after_name(message: Message, state: FSMContext):
    await delete_messages(message, state, "last_question_id", "reminder_message_id")
    if not validate("name", message.text):
        await handle_invalid_answer(message, state, text=ASK_NAME["invalid"])
        return
    await state.update_data(name=message.text)
    await ask_question(message, state, text=ASK_PHONE["valid"], reply_markup=send_phone_keyboard)
    await state.set_state(PopUpForm.phone)


@router.message(PopUpForm.phone)
async def after_phone(message: Message, state: FSMContext):
    await delete_messages(message, state, "last_question_id", "reminder_message_id")
    phone_raw = message.contact.phone_number if message.contact else message.text or ""
    if not validate("phone", phone_raw):
        await handle_invalid_answer(message, state, text=ASK_PHONE["invalid"], reply_markup=send_phone_keyboard)
        return       
    await state.update_data(phone=phone_raw)
    await ask_question(message, state, text=ASK_EMAIL["valid"], reply_markup=hide_menu)
    await state.set_state(PopUpForm.email)


@router.message(PopUpForm.email)
async def after_email(message: Message, state: FSMContext):
    await delete_messages(message, state, "last_question_id", "reminder_message_id")
    if not validate("email", message.text):
        await handle_invalid_answer(message, state, text=ASK_EMAIL["invalid"])
        return
    await state.update_data(email=message.text)
    await send_notification(message, state)
    await final(message, state)


async def send_notification(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await save_popup_registration(message, data)
    except Exception as e:
        pass

    current_date = datetime.now().strftime("%d.%m.%Y")

    contact = f"{message.from_user.first_name}"
    if message.from_user.last_name:
        contact += f" {message.from_user.last_name}"
    if message.from_user.username:
        contact += f" / @{message.from_user.username}"

    notify_msg = f"🆕 Реєстрація на Pop-Up 🆕\n"\
        f"🗓Дата реєстрації:  {current_date}\n"\
        f"🔹Контакт:  {contact}\n"\
        f"🔹Ім'я та прізвище: {data['name']}\n"\
        f"🔹Номер: {data['phone']}\n"\
        f"🔹Email: {data['email']}"

    await message.bot.send_message(text=notify_msg, chat_id=GROUP_ID, message_thread_id=POPUP_TOPIC_ID)


async def final(message: Message, state: FSMContext):
    data = await state.get_data()

    # Відправляємо картинку з caption
    try:
        from aiogram.types import FSInputFile
        photo = FSInputFile(POPUP_END_TEXT['img'])
        keyboard = build_popup_final_keyboard()
        await message.answer_photo(photo, caption=POPUP_END_TEXT['caption'])
        await message.answer(text=POPUP_END_TEXT['final'], reply_markup=keyboard)
    except Exception as e:
        # Якщо картинка не знайдена, відправляємо тільки текст
        keyboard = build_popup_final_keyboard()
        await message.answer(POPUP_END_TEXT['caption'])
        await message.answer(text=POPUP_END_TEXT['final'], reply_markup=keyboard)

    await state.clear()