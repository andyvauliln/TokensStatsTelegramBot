import logging
from telegram import Bot, Update
from telegram import error
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram.constants import ParseMode
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID, TELEGRAM_SENDING_INTERVAL_SECONDS
from src.report_generator import generate_report
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
    try:
        logger.telegram.info("Starting generate report for Telegram.")
        report = generate_report()
        if report:
            logger.telegram.info(f"REPORT: \n {report}")
            await bot.send_message(chat_id=TELEGRAM_GROUP_ID,
                                   text=report, parse_mode=ParseMode.MARKDOWN)
            logger.telegram.info("Daily report sent successfully.")
        else:
            logger.telegram.info("No report generated to send.")
    except error.TelegramError as e:
        logger.telegram.error(
            "Telegram error during report sending: %s", e, exc_info=True)
    except Exception as e:
        logger.telegram.error(
            "Failed to send daily report: %s", e, exc_info=True)


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


def shutdown(signum, frame):
    """Gracefully shut down the bot and the report thread."""
    logger.telegram.info(
        "Received signal to shut down. Terminating gracefully.")
    # shutdown logic
    sys.exit(0)


if __name__ == "__main__":
    # Register the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Run the report sender in a separate thread
    report_thread = Thread(target=asyncio.run, args=(send_daily_report(bot),))
    report_thread.start()
    logger.telegram.info("Report thread started.")

    # Start the Telegram bot
    start_bot()
