import asyncio
from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext
from utils.states import PopUpForm
from keyboards.inline import confirm_cancel_keyboard

REMAINDER_DELAY = 10  # seconds
REMAINDER_TEXT = "Я все ще тут. Бажаєш продовжити дії в боті?"

reminders: dict[StorageKey, asyncio.Task] = {}

async def arm_reminder(bot: Bot, state: FSMContext, delay: float = REMAINDER_DELAY) -> None:
    key = state.key
    if task := reminders.pop(key, None):
        task.cancel()
    reminders[key] = asyncio.create_task(reminder_loop(bot, state.storage, key, delay))

async def reminder_loop(bot: Bot, storage, key, delay):
    await asyncio.sleep(delay)
    state = FSMContext(storage=storage, key=key)
    if await state.get_state() in PopUpForm:
        msg = await bot.send_message(key.chat_id, REMAINDER_TEXT, reply_markup=confirm_cancel_keyboard)
        await state.update_data(reminder_message_id=msg.message_id)