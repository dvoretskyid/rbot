from aiogram.fsm.state import StatesGroup, State

class PopUpForm(StatesGroup):
    name = State()
    phone = State()
    email = State()