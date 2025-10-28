import re
import asyncio
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.reminders import arm_reminder

async def delete_messages(message: Message, state: FSMContext, *keys: str) -> None:
    data = await state.get_data()
    for key in keys:
        message_id = data.get(key)
        if not message_id:
            continue
        try:
            await message.bot.delete_message(message.chat.id, message_id)
        except Exception:
            pass
    if keys:
        await state.update_data({key: None for key in keys})



async def ask_question(message: Message, state: FSMContext, text: str, **kwargs) -> None:
    ask_msg = await message.answer(text=text, **kwargs)
    await state.update_data(last_question_id=ask_msg.message_id,
                            last_question_time=asyncio.get_running_loop().time())
    await arm_reminder(message.bot, state)


async def handle_invalid_answer(
    message: Message,
    state: FSMContext,
    text: str,
    key: str = "invalid_answer_id",
    **kwargs,
) -> None:
    await ask_question(message, state, text=text, **kwargs)
    await state.update_data({key: message.message_id})
    await delete_messages(message, state, key)


FIELD_PATTERNS = {
    "name": re.compile(r"^[A-Za-zА-Яа-яІіЇїЄєҐґ'’-]+ [A-Za-zА-Яа-яІіЇїЄєҐґ'’-]+$"),
    "phone": re.compile(r"^\+?\d{10,15}$"),
    "email": re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,}$"),
}

def validate(field: str, value: str) -> bool:
    pattern = FIELD_PATTERNS.get(field)
    return bool(pattern and pattern.fullmatch(value.strip()))
