import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
import time
from .models import Session, Event
from .config import ETH_NODE_URL, EVENTS_CONFIG
from datetime import datetime
from .logging_config import logger
from .event_parser import get_event_parser

# Initialize web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def fetch_and_process_events(event_name, event_config, from_block=0, to_block='latest'):
    """Fetch and process events from the specified contract."""
    try:
        # contract = w3.eth.contract(address=event_config['address'], abi=event_config['abi'])
        event_filter = w3.eth.filter({
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': event_config['address'],
            'topics': event_config['topics']
        })
        events = event_filter.get_all_entries()
        logger.info(f"Total {event_name} Events Found: {len(events)}")

        for index, event in enumerate(events):
            parser = get_event_parser(event_name)
            parsed_event = parser.parse_event_data(event, event_config)
            logger.info(
                f"\n [{index}/{len(events)}] Parsed Event: \n {parsed_event}\n")
            save_event_in_db(event_name, parsed_event)

        return events[-1]['blockNumber'] if len(events) > 0 else from_block
    except Exception as e:
        logger.error(f"Error fetching {event_name} events: {e}", exc_info=True)
        return from_block


def save_event_in_db(event_name, event_data):
    """Process a single event, transforming it for database insertion."""
    try:
        session = Session()
        if not Event.insert_event(session, event_name, event_data):
            logger.info(
                f"Duplicate {event_name} event skipped: {event_data['transactionHash']}")
    except Exception as e:
        logger.error(
            f"Error processing {event_name} event: {e}", exc_info=True)
    finally:
        session.close()


def listen_for_events(start_block, event_name, event_config):
    """Main listener loop for new events."""
    try:
        logger.info(
            f"Starting event listener from specified block: {start_block}")
        while True:
            if event_config['active']:
                last_block = fetch_and_process_events(
                    event_name, event_config, from_block=start_block)
                start_block = last_block + 1
            time.sleep(10)
    except Exception as e:
        logger.error(f"Error in event listener loop: {e}", exc_info=True)


if __name__ == "__main__":
    listen_for_events(start_block=19516698)
