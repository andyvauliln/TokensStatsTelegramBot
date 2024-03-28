import sys
from threading import Thread
from src.event_listener import listen_for_events, fetch_and_process_events
from src.models import Session, Event
from src.config import EVENTS_CONFIG
from src.logging_config import logger


def main():
    try:
        session = Session()
        for event_name, event_config in EVENTS_CONFIG.items():
            if event_config['active']:
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
                        last_block = fetch_and_process_events(
                            event_name, event_config, start_block)
                    else:
                        # Delete all events and start Backfill from first block
                        Event.delete_events(session, event_name)
                        last_block = fetch_and_process_events(
                            event_name, event_config, event_config['start_block'])
                else:
                    last_block_number = Event.get_last_event_block_number(
                        session, event_name)

                    if last_block_number:
                        # Start Backfill from last Block
                        last_block = fetch_and_process_events(
                            event_name, event_config, last_block_number + 1)
                    else:
                        # Start Backfill from first block
                        last_block = fetch_and_process_events(
                            event_name, event_config, event_config['start_block'])

                logger.info(f"Backfill completed for {event_name}.")

                event_listener_thread = Thread(target=listen_for_events, args=(
                    last_block + 1, event_name, event_config))
                event_listener_thread.start()
            else:
                logger.info(f"Event {event_name} is not active. Skipping...")

    except Exception as e:
        logger.error("An error occurred in the main function: %s",
                     e, exc_info=True)
    finally:
        session.close()


if __name__ == "__main__":
    main()
