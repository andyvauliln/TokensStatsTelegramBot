import logging
from telegram import Bot, Update
from telegram import error
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram.constants import ParseMode
from src.config import TELEGRAM_BOT_TOKEN
from src.report_generators import get_report_generator
from src.config import TELEGRAM_BOT_TOKEN, EVENTS_CONFIG
from threading import Thread
from src.logging_config import logger
import asyncio
import time
import signal
import sys


bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your TokensStatsTelegramBot.')


async def send_daily_report(bot: Bot) -> None:
    """Function to generate and send the daily report."""
    for event_name, event_config in EVENTS_CONFIG.items():
        if event_config['active']:
            try:
                report_generator = get_report_generator(event_name)
                report = report_generator.generate_report()
                if report:
                    for telegram_group_id in event_config['telegram_group_ids']:
                        await bot.send_message(chat_id=telegram_group_id,
                                               text=report, parse_mode=ParseMode.MARKDOWN)
                        logger.telegram.info(
                            f"Report for {event_name} sent successfully to group {telegram_group_id}.")
                else:
                    logger.telegam.info(
                        f"No report generated for {event_name}.")
            except Exception as e:
                logger.telegram.error(
                    f"Failed to send report for {event_name}: {e}", exc_info=True)


def start_bot() -> None:
    """Start the bot."""
    try:
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        start_handler = CommandHandler('start', start)
        application.add_handler(start_handler)
        application.run_polling()
        logger.telegram.info("Telegram bot started polling.")
    except Exception as e:
        logger.telegram.error(
            "An error occurred while starting the bot: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":

    # Run the report sender in a separate thread
    report_thread = Thread(target=asyncio.run, args=(send_daily_report(bot),))
    report_thread.start()
    logger.telegram.info("Report thread started.")

    # Start the Telegram bot
    start_bot()
