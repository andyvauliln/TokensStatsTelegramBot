from .blockchain_listener import fetch_distribution_events, save_event_in_db
from .config import ETH_NODE_URL
from web3 import Web3
import argparse
from .logging_config import logger


def backfill_events(start_block):
    """
    Backfills events from the specified start block to the current block.
    :param start_block: The block number from which to start backfilling events.
    """
    w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
    current_block = w3.eth.block_number
    logger.info(
        f"Starting backfill from block {start_block} to {current_block}")

    try:
        events = fetch_distribution_events(
            from_block=start_block, to_block=current_block)
        if len(events) > 0:
            for event in events:
                save_event_in_db(event)
            logger.info(f"Successfully backfilled {len(events)} events.")
        else:
            logger.info("No events found to backfill.")

        return current_block
    except Exception as e:
        logger.error("Error during backfill operation: %s", e, exc_info=True)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill events from a specified start block.")
    parser.add_argument("start_block", type=int,
                        help="The block number from which to start backfilling events.")
    args = parser.parse_args()
    backfill_events(args.start_block)
