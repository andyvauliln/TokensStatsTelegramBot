# TokensStatsTelegramBot

A Python-based Telegram bot designed to monitor various Ethereum contract events, record them into a PostgreSQL database, and send statistics reports to a Telegram group. This application uses libraries such as `web3.py` for Ethereum blockchain interaction, `python-telegram-bot` for Telegram bot functionality, and `SQLAlchemy` for database operations.

## Features

- **Modular Event Monitoring**: Configurable monitoring of multiple Ethereum contract events.
- **Database Recording**: Storing event data in a PostgreSQL database for historical tracking and analysis.
- **Automated Reporting**: Generating and sending detailed reports for each monitored event to a Telegram group at scheduled intervals.

## Getting started

### Requirements

- Python 3.x
- PostgreSQL
- Telegram Bot API
- An Ethereum node accessible via HTTPS

### Quickstart

1. Clone the repository to your local machine.
2. Install `pip install virtualenv` and create a virtual environment `virtualenv venv`
3. Activate the virtual environment. Windows: `venv\Scripts\activate` Linux/macOS: `source venv/bin/activate`
4. Install required Python libraries with `pip install -r requirements.txt` (ensure you have pip installed).
5. Set up your environment variables and update the `.env` file with your database URI, Telegram bot token, Ethereum node URL, and Telegram group ID. Ensure to also configure the `EVENTS_CONFIG` in `src/config.py` with the events you want to monitor, specifying each event's name, contract address, ABI, whether it is active, and other necessary details as per the updated structure.
6. Run the database migrations to create tables for each event specified in the `EVENTS_CONFIG`. This can be done by executing the script that initializes your database schema.
7. You can start the application as:  
   `python app.py` to fetch events from the last known block number in the DB for all active events.
   `python app.py 154366` to start the application from a specific block number for all active events.
   `python app.py 0` to rewrite all event history in the DB for all active events.
8. To see program logs, check the `app.log` and `telegram.log` files in the project root directory.

### Telegram Report

The application automatically sends reports to the configured Telegram group at scheduled intervals for each active event. Ensure your `.env` file is correctly set up with the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_ID`.

### Customizing Event Monitoring and Reporting

- To add or modify the events being monitored, update the `EVENTS_CONFIG` in `src/config.py`. For each event, you can specify the contract address, ABI, database table name, and other relevant settings.
- Implement custom event parsing logic by creating subclasses of `EventParser` in `src/event_parser.py` for each event type. This allows for flexible handling of different event data structures.
- Customize report generation by implementing subclasses of `ReportGenerator` in `src/report_generators.py` for each event type. This enables tailored reports for different events, including specific calculations and formatting.

### License

Copyright (c) 2024.