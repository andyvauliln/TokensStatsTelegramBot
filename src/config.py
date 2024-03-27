import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Assign environment variables to Python variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
ETH_NODE_URL = os.getenv('ETH_NODE_URL')
PG_DB_URI = os.getenv('PG_DB_URI')

# Interval in a seconds to check Events
INTERVAL_FOR_CHECKING_NEW_EVENTS_MINUTES = 10
REPORT_INTERVAL_FOR_EVENTS_HOURS = 4
TELEGRAM_SENDING_INTERVAL_SECONDS = 120  # 14400
CONTRACT_START_BLOCK = 18607627
CONTRACT_ABI = ""
CONTRACT_ADDRESS = ""
FILE_LOGGING = True
TELEGRAM_CRON_SCHEDULE = "* * * * *"


# Error handling for missing environment variables
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID, ETH_NODE_URL, PG_DB_URI]):
    missing_vars = [var for var in ["TELEGRAM_BOT_TOKEN",
                                    "TELEGRAM_GROUP_ID", "ETH_NODE_URL", "PG_DB_URI"] if not os.getenv(var)]
    error_message = f"Missing environment variables: {', '.join(missing_vars)}"
    print(error_message)
    raise EnvironmentError(error_message)
