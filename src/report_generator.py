# report_generator.py

from datetime import datetime, timedelta
from .models import Session, TotalDistribution
from sqlalchemy import func
from .config import REPORT_INTERVAL_FOR_EVENTS_HOURS
from .logging_config import logger


def generate_report():
    # Create a session
    session = Session()
    # Calculate n hours ago
    time_ago = datetime.utcnow() - timedelta(hours=REPORT_INTERVAL_FOR_EVENTS_HOURS)

    try:
        events = session.query(TotalDistribution).filter(
            TotalDistribution.timestamp >= time_ago).all()
        logger.telegram.info(
            f"FOUND {len(events)} TotalDistribution events for the last {REPORT_INTERVAL_FOR_EVENTS_HOURS} Hour for Report Generation")
        if events:
            # Calculate sums
            aix_processed_sum = sum(event.aix_processed for event in events)
            aix_distributed_sum = sum(
                event.aix_distributed for event in events)
            eth_bought_sum = sum(event.eth_bought for event in events)
            eth_distributed_sum = sum(
                event.eth_distributed for event in events)

            # Calculate times
            first_tx_time = min(event.timestamp for event in events)
            last_tx_time = max(event.timestamp for event in events)

            # Get the most recent distributor wallet info
            most_recent_event = events[-1]
            distributor_wallet = most_recent_event.distributor_wallet
            distributor_balance = most_recent_event.distributor_balance

            hours_first_tx = (datetime.utcnow() -
                              first_tx_time).total_seconds() // 3600
            minutes_first_tx = (datetime.utcnow() -
                                first_tx_time).total_seconds() % 3600 // 60
            hours_last_tx = (datetime.utcnow() -
                             last_tx_time).total_seconds() // 3600
            minutes_last_tx = (datetime.utcnow() -
                               last_tx_time).total_seconds() % 3600 // 60

            # Format the hours and minutes without leading zeros
            formatted_first_tx = f"{int(hours_first_tx)}h {int(minutes_first_tx)}m ago"
            formatted_last_tx = f"{int(hours_last_tx)}h {int(minutes_last_tx)}m ago"
            # Format report
            report = f"""Daily $AIX Stats:
            - First TX: {formatted_first_tx}
            - Last TX: {formatted_last_tx}
            - AIX processed: {aix_processed_sum:,.2f}
            - AIX distributed: {aix_distributed_sum:,.2f}
            - ETH bought: {eth_bought_sum:,.2f}
            - ETH distributed: {eth_distributed_sum:,.2f}
            
            Distributor wallet: {distributor_wallet}
            Distributor balance: {distributor_balance:.2f} ETH"""
            logger.telegram.info("Report generated successfully.")
            return report
        else:
            return "No events found in the last 24 hours."
    except Exception as e:
        logger.telegram.error("Error generating report: %s", e, exc_info=True)
        return None
    finally:
        session.close()


if __name__ == "__main__":
    report = generate_report()
    if report:
        logger.telegram.info(report)
    else:
        logger.telegram.warning("Failed to generate report.")
