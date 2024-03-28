import logging
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram.constants import ParseMode
from src.config import TELEGRAM_BOT_TOKEN, EVENTS_CONFIG
from src.report_generators import get_report_generator
from threading import Thread
from src.logging_config import logger
import asyncio
import pytest
from unittest.mock import patch, MagicMock

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
                    logger.telegram.info(
                        f"No report generated for {event_name}.")
            except Exception as e:
                logger.telegram.error(
                    f"Failed to send report for {event_name}: {e}", exc_info=True)

@pytest.mark.asyncio
@patch('src.report_generators.get_report_generator')
@patch('src.config.EVENTS_CONFIG', new_callable=lambda: {"TotalDistribution": {"active": True, "telegram_group_ids": ["test_group_id"]}})
async def test_send_daily_report(mock_events_config, mock_get_report_generator):
    """Test the send_daily_report function."""
    mock_bot = MagicMock()
    mock_report_generator = MagicMock()
    mock_report_generator.generate_report.return_value = "Test Report"
    mock_get_report_generator.return_value = mock_report_generator

    await send_daily_report(mock_bot)
    mock_bot.send_message.assert_called_with(chat_id="test_group_id",
                                             text="Test Report", parse_mode=ParseMode.MARKDOWN)
    logger.info("Test for send_daily_report passed.")