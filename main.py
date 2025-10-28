import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault
from configs.bot import BOT_TOKEN
from routers import start, popup, support, order
from database.models import init_db

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def set_commands() -> None:
    commands = [
        BotCommand(command="menu", description="Головне меню"),
        BotCommand(command="popup", description="Реєстрація на POP-UP"),
        BotCommand(command="help", description="Підтримка"),
    ]
    try:
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        logging.info("Команди бота успішно встановлені")
    except Exception as e:
        logging.error(f"Помилка при встановленні команд: {e}")


async def on_startup() -> None:
    logging.info("Запуск бота...")
    await init_db()
    logging.info("База даних ініціалізована")
    await set_commands()
    # Видаляємо webhook якщо він був встановлений
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущено в режимі polling")


async def on_shutdown() -> None:
    logging.info("Вимикання бота...")
    await bot.session.close()


async def main() -> None:
    # Підключаємо роутери
    dp.include_router(start.router)
    dp.include_router(popup.router)
    dp.include_router(support.router)
    dp.include_router(order.router)

    # Реєструємо startup та shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запускаємо polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот зупинено користувачем")
