from datetime import datetime
from aiogram import Router, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from configs.popup import POP_UP_REMINDER
from database.requests import get_all_popups, update_popup_last_reminder
import logging

logger = logging.getLogger(__name__)
router = Router()
scheduler = AsyncIOScheduler()


def parse_event_date(date_str: str, year: int = 2025) -> datetime:
    try:
        day, month = date_str.split(".")
        return datetime(year, int(month), int(day))
    except (ValueError, AttributeError) as e:
        logger.error(f"Помилка парсингу дати '{date_str}': {e}")
        return None


async def send_reminders(bot: Bot):
    logger.info("Запуск перевірки нагадувань...")

    try:
        registrations = await get_all_popups()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for registration in registrations:
            event_date = parse_event_date(registration.date)

            if not event_date:
                logger.warning(f"Не вдалося розпарсити дату для реєстрації {registration.id}")
                continue

            days_until_event = (event_date - today).days

            reminder_type = None
            if days_until_event == 5:
                reminder_type = "5days"
            elif days_until_event == 3:
                reminder_type = "3days"
            elif days_until_event == 1:
                reminder_type = "1day"

            if not reminder_type:
                continue

            if registration.last_reminder_sent:
                last_sent = registration.last_reminder_sent.replace(hour=0, minute=0, second=0, microsecond=0)
                if last_sent == today:
                    logger.info(f"Нагадування для {registration.telegram_id} вже відправлено сьогодні")
                    continue

            reminder_text = POP_UP_REMINDER[reminder_type].replace("[date]", f"{registration.date}.2025")

            try:
                await bot.send_message(
                    chat_id=registration.telegram_id,
                    text=reminder_text
                )

                await update_popup_last_reminder(registration.id)

                logger.info(f"Нагадування ({reminder_type}) відправлено для {registration.telegram_id}")
            except Exception as e:
                logger.error(f"Помилка відправки нагадування для {registration.telegram_id}: {e}")

    except Exception as e:
        logger.error(f"Помилка при відправці нагадувань: {e}")


def setup_scheduler(bot: Bot):
    scheduler.add_job(
        send_reminders,
        trigger=CronTrigger(hour=12, minute=0),
        args=[bot],
        id="daily_reminders",
        replace_existing=True
    )

    logger.info("Scheduler нагадувань налаштовано на 12:00 щодня")


async def start_scheduler(bot: Bot):
    setup_scheduler(bot)
    scheduler.start()
    logger.info("Scheduler нагадувань запущено")


async def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler нагадувань зупинено")
