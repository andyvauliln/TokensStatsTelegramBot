from datetime import datetime, timedelta
from sqlalchemy import func
from .models import Session, Event
from .config import EVENTS_CONFIG
from .logging_config import logger


class ReportGenerator:
    """
    Base class for generating reports for different events.
    """

    def __init__(self, event_name):
        self.event_name = event_name
        self.session = Session()

    def generate_report(self):
        """
        Generates a report for the event. This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def get_events(self):
        """
        Retrieves events from the last specified number of hours.
        """
        try:
            time_ago = datetime.utcnow() - \
                timedelta(
                    hours=EVENTS_CONFIG[self.event_name]['report_interval_hours'])
            events = self.session.query(Event).filter(Event.name == self.event_name).filter(
                Event.timestamp >= time_ago).all()
            return events
        except Exception as e:
            logger.telegram.error(
                "Error generating report: %s", e, exc_info=True)
            return None
        finally:
            self.session.close()


class TotalDistributionReportGenerator(ReportGenerator):
    """
    Report generator for TotalDistribution events.
    """

    def generate_report(self):
        events = self.get_events()
        try:
            if events:
                # Calculate sums using dictionary key access
                aix_processed_sum = sum(
                    event.data['aix_processed'] for event in events)
                aix_distributed_sum = sum(
                    event.data['aix_distributed'] for event in events)
                eth_bought_sum = sum(
                    event.data['eth_bought'] for event in events)
                eth_distributed_sum = sum(
                    event.data['eth_distributed'] for event in events)

                # Calculate times
                first_tx_time = min(event.timestamp for event in events)
                last_tx_time = max(event.timestamp for event in events)

                # Get the most recent distributor wallet info using dictionary key access
                most_recent_event = events[-1]
                distributor_wallet = most_recent_event.data['distributor_wallet']
                distributor_balance = most_recent_event.data['distributor_balance']

                hours_first_tx = (datetime.utcnow() -
                                  first_tx_time).total_seconds() // 3600
                minutes_first_tx = (datetime.utcnow() -
                                    first_tx_time).total_seconds() % 3600 // 60
                hours_last_tx = (datetime.utcnow() -
                                 last_tx_time).total_seconds() // 3600
                minutes_last_tx = (datetime.utcnow() -
                                   last_tx_time).total_seconds() % 3600 // 60

                # Format the hours and minutes
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
                logger.telegram.info(
                    f"Report generated successfully for {self.event_name}")
                return report
            else:
                logger.info(
                    f"No {self.event_name} events found in the last {EVENTS_CONFIG[self.event_name]['report_interval_hours']}h.")
                return f"No {self.event_name} events found in the last {EVENTS_CONFIG[self.event_name]['report_interval_hours']}h."
        except Exception as e:
            logger.telegram.error(
                "Error generating report: %s", e, exc_info=True)
            return f"Error generating report: {e}"


def get_report_generator(event_name):
    """
    Factory function to get the appropriate report generator based on the event name.
    """
    if event_name == "TotalDistribution":
        return TotalDistributionReportGenerator(event_name)
    else:
        logger.error(f"No report generator found for event: {event_name}")
        return None
