from aiogram.types import Message
from sqlalchemy import select
from database.models import AsyncSessionLocal, PopUp


async def save_popup_registration(message: Message, data: dict):
    """
    Зберігає дані реєстрації на popup в базу даних

    Args:
        message: Message об'єкт з Telegram
        data: Словник з даними форми (name, phone, email, date)
    """
    async with AsyncSessionLocal() as session:
        try:
            popup_entry = PopUp(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                name=data.get("name"),
                phone=data.get("phone"),
                email=data.get("email"),
                date=data.get("date")
            )
            session.add(popup_entry)
            await session.commit()
            return popup_entry.id
        except Exception as e:
            await session.rollback()
            raise e


async def get_popup_by_telegram_id(telegram_id: int):
    """
    Отримує всі реєстрації користувача за telegram_id

    Args:
        telegram_id: ID користувача в Telegram

    Returns:
        Список об'єктів PopUp
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PopUp).where(PopUp.telegram_id == telegram_id)
        )
        return result.scalars().all()


async def get_all_popups():
    """
    Отримує всі реєстрації на popup

    Returns:
        Список всіх об'єктів PopUp
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PopUp))
        return result.scalars().all()


async def get_popup_by_id(popup_id: int):
    """
    Отримує реєстрацію за ID

    Args:
        popup_id: ID запису в базі

    Returns:
        Об'єкт PopUp або None
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(PopUp).where(PopUp.id == popup_id)
        )
        return result.scalar_one_or_none()
