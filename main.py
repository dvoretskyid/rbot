import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from configs.bot import BOT_TOKEN, BASE_URL, HOST, PORT
from routers import start, popup
from database.models import init_db

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot)


async def set_commands() -> None:
    commands = [
        BotCommand(command="menu", description="Головне меню"),
        BotCommand(command="popup", description="Реєстрація на POP-UP"),
        # BotCommand(command="order", description="Продукт"),
        # BotCommand(command="news", description="Новини та події"),
        BotCommand(command="help", description="Підтримка"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def on_startup() -> None:
    await init_db()  # Ініціалізуємо базу даних
    await set_commands()
    await bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}")


async def on_shutdown() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


def main() -> None:
    dp.include_router(start.router)
    dp.include_router(popup.router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=f"/{BOT_TOKEN}")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    main()
