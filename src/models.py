# models.py

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, UniqueConstraint, Boolean, BigInteger, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from .logging_config import logger
from .config import PG_DB_URI, EVENTS_CONFIG

# Define the base class
Base = declarative_base()


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    contractName = Column(String(10), nullable=False)
    blockNumber = Column(BigInteger)
    blockHash = Column(String(66))
    transactionIndex = Column(Integer)
    transactionHash = Column(String(66))
    data = Column(JSON)  # Store event-specific data as JSON
    timestamp = Column(DateTime)
    # Optional field for events that include log index
    logIndex = Column(Integer, nullable=True)
    # Optional field to indicate if the event was removed
    removed = Column(Boolean, default=False)

    # Define unique constraint within the class using __table_args__
    __table_args__ = (
        UniqueConstraint('blockNumber', 'transactionIndex', 'transactionHash',
                         name='uix_blocknumber_txindex_txhash'),
    )

    @staticmethod
    def insert_event(session, event_name, event_data):
        """
        Inserts an event into the database if it does not already exist.
        :param session: Database session
        :param event_name: Name of the event
        :param event_data: Dictionary containing event data
        """
        try:
            event = Event(**event_data)
            session.add(event)
            session.commit()
            logger.info(
                f"Event {event_name} successfully inserted into the database. \nTxHash: {event_data['transactionHash']} \nLogIndex: {event_data['logIndex']} \nTransactionIndex: {event_data['transactionIndex']}")
            return True
        except IntegrityError:
            session.rollback()
            logger.warning(
                f"Duplicate event {event_name} detected and skipped. \nTxHash: {event_data['transactionHash']} \nLogIndex: {event_data['logIndex']} \nTransactionIndex: {event_data['transactionIndex']}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(
                f"Error inserting event {event_name} into the database: {e}", exc_info=True)
            return False

    @staticmethod
    def reset_table():
        """
        Drops the 'total_distribution' table from the database and recreates it.
        :param engine: SQLAlchemy engine instance
        """
        try:
            # Drop the table if it exists
            Event.__table__.drop(engine, checkfirst=True)
            logger.info("Table 'total_distribution' dropped successfully.")

            # Recreate the table
            Event.__table__.create(engine, checkfirst=True)
            logger.info("Table 'total_distribution' created successfully.")
        except Exception as e:
            logger.error("Error resetting table: %s", e, exc_info=True)

    @staticmethod
    def delete_events(session, event_name):
        try:
            session.query(Event).filter(Event.name == event_name).delete()
            session.commit()
            logger.info(
                f"{event_name} Events was deleted")
        except Exception as e:
            # If there was an error, rollback the session
            session.rollback()
            logger.error(
                "An error occurred when deleting {event_name} %s", e, exc_info=True)

    @staticmethod
    def get_last_event_block_number(session, event_name):
        """
        Retrieves the timestamp of the most recent event processed for a given event name.
        :param session: Database session
        :param event_name: Name of the event
        """
        try:
            result = session.query(Event).filter(
                Event.name == event_name).order_by(Event.timestamp.desc()).first()
            if result:
                return result.blockNumber
            return None
        except Exception as e:
            logger.error(
                f"Error retrieving last event timestamp for {event_name}: {e}", exc_info=True)
            return None


# Create the database engine
try:
    engine = create_engine(PG_DB_URI)
    Base.metadata.create_all(engine)
except Exception as e:
    logger.error(
        f"Error creating database engine or tables: {e}", exc_info=True)
    raise

# Create a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)
