import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Assign environment variables to Python variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ETH_NODE_URL = os.getenv('ETH_NODE_URL')
PG_DB_URI = os.getenv('PG_DB_URI')

FILE_LOGGING = True

# Events configuration
EVENTS_CONFIG = {
    "TotalDistribution": {
        "active": True,
        "address": "0xaBE235136562a5C2B02557E1CaE7E8c85F2a5da0",
        "abi": '''[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "inputAixAmount", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "distributedAixAmount", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "swappedEthAmount", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "distributedEthAmount", "type": "uint256"}], "name": "TotalDistribution", "type": "event"}]''',
        "db_name": "TotalDistribution",
        "contractName": "AIX",
        "report_interval_hours": 4,
        "topics": ["0xe689c8111f40a171596b9d81ac47c6fe406d2297392957c5126c2f7448c58694"],
        "telegram_group_ids": [288566859],
        "start_block": 19516698,
    }
}

# Error handling for missing environment variables
if not all([TELEGRAM_BOT_TOKEN, ETH_NODE_URL, PG_DB_URI, EVENTS_CONFIG]):
    missing_vars = [var for var in ["TELEGRAM_BOT_TOKEN", "ETH_NODE_URL",
                                    "PG_DB_URI", "EVENTS_CONFIG"] if not os.getenv(var)]
    error_message = f"Missing environment variables: {', '.join(missing_vars)}"
    logging.error(error_message)
    raise EnvironmentError(error_message)
