from datetime import datetime
from aiogram.types import Message
from sqlalchemy import select
from database.models import AsyncSessionLocal, PopUp, User


async def save_popup_registration(message: Message, data: dict):
    """
    Зберігає дані реєстрації на popup в базу даних

    Args:
        message: Message об'єкт з Telegram
        data: Словник з даними форми (name, phone, email)
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
                email=data.get("email")
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


# ============= USER FUNCTIONS =============

async def register_user(message: Message):
    """
    Реєструє нового користувача або оновлює існуючого при /start

    Args:
        message: Message об'єкт з Telegram

    Returns:
        User об'єкт (новий або оновлений)
    """
    async with AsyncSessionLocal() as session:
        try:
            # Перевіряємо чи існує користувач
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Оновлюємо дані існуючого користувача
                user.username = message.from_user.username
                user.first_name = message.from_user.first_name
                user.last_name = message.from_user.last_name
                user.updated_at = datetime.now()
            else:
                # Створюємо нового користувача
                user = User(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )
                session.add(user)

            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            raise e


async def get_user_by_telegram_id(telegram_id: int):
    """
    Отримує користувача за telegram_id

    Args:
        telegram_id: ID користувача в Telegram

    Returns:
        Об'єкт User або None
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def get_all_users():
    """
    Отримує всіх користувачів

    Returns:
        Список всіх об'єктів User
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def get_user_count():
    """
    Отримує кількість зареєстрованих користувачів

    Returns:
        Кількість користувачів
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return len(users)


