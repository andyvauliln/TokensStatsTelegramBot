import sys
from threading import Thread
from src.blockchain_listener import listen_for_events
from src.event_backfill import backfill_events
from src.models import Session, TotalDistribution
from src.config import CONTRACT_START_BLOCK
from src.logging_config import logger


def main():
    try:
        session = Session()
        last_block = None
        if len(sys.argv) > 1:
            try:
                start_block = int(sys.argv[1])
            except ValueError:
                logger.error(
                    "Invalid start block provided. Start block must be an integer. Usage: app.py 1525665"
                )
                return
            # Start Backfill from selected block
            if start_block > 0:
                last_block = backfill_events(start_block)
            else:
                # Drop the table and start Backfill from first block
                TotalDistribution.reset_table()
                last_block = backfill_events(CONTRACT_START_BLOCK)
        else:
            last_block_number = TotalDistribution.get_last_block_number(
                session)

            if last_block_number:
                # Start Backfill from last Block
                last_block = backfill_events(last_block_number + 1)
            else:
                # Start Backfill from first block
                last_block = backfill_events(CONTRACT_START_BLOCK)

        logger.info("Backfill completed.")

        event_listener_thread = Thread(
            target=listen_for_events, args=(last_block,))
        event_listener_thread.start()
        logger.info("Event listener started.")

    except Exception as e:
        logger.error("An error occurred in the main function: %s",
                     e, exc_info=True)


if __name__ == "__main__":
    main()
