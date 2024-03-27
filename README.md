# TokensStatsTelegramBot

A Python-based Telegram bot designed to monitor Ethereum contract events, such is "TotalDistribution", record them into a PostgreSQL database, and send daily statistics reports to a Telegram group. This application using libraries such as `web3.py` for Ethereum blockchain interaction, `python-telegram-bot` for Telegram bot functionality, and `SQLAlchemy` for database operations.

## Features

- **Event Monitoring**: Continuous monitoring of "TotalDistribution" events from an Ethereum contract.
- **Database Recording**: Storing event data in a PostgreSQL database for historical tracking and analysis.
- **Automated Reporting**: Generating and sending detailed reports to a Telegram group in scheduled intervals

## Getting started

### Requirements

- Python 3.x
- PostgreSQL
- Telegram Bot API
- An Ethereum node accessible via HTTPS

### Quickstart

1. Clone the repository to your local machine.
2. Install `pip install virtualenv` and create virtual environment `virtualenv venv`
3. Activate virtual environment. Windows: `venv\Scripts\activate` Linux/macOS: `source venv/bin/activate`
4. Install required Python libraries with `pip install -r requirements.txt` (ensure you have pip installed).
5. Set up your evironment variables and update the `.env` file with your database URI, Telegram bot token, Ethereum node URL, and Telegram group ID.
6. You can start application as:  
   `python app.py` for fetching event from last known block number in DB.
   `python app.py 154366` to start application from concrete block number
   `python app.py 0` to rewrite all event history in DB
7. To see program logs you

### Telegram Report

For telegram report install `pip install crontab` in it not present on PC and run command `crontab -e` to insert `* * * * * path/to/python path/to/send_report_to_telegram.py` to activate cron or run `python send_report_to_telegram.py` for single use

### License

Copyright (c) 2024.
