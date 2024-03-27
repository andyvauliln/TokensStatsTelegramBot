# models.py

from sqlalchemy import func, create_engine, Column, Integer, Float, String, DateTime, UniqueConstraint, Boolean, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from .logging_config import logger
from .config import PG_DB_URI

# Load environment variables
load_dotenv()

# Define the base class
Base = declarative_base()

# Define the TotalDistribution class


class TotalDistribution(Base):
    __tablename__ = 'total_distribution'
    id = Column(Integer, primary_key=True)
    blockNumber = Column(BigInteger)
    blockHash = Column(String(66))
    logIndex = Column(Integer)
    removed = Column(Boolean)
    transactionIndex = Column(Integer)
    transactionHash = Column(String(66))
    aix_processed = Column(Float)
    aix_distributed = Column(Float)
    eth_bought = Column(Float)
    eth_distributed = Column(Float)
    distributor_wallet = Column(String)
    distributor_balance = Column(Float)
    timestamp = Column(DateTime)

    # Define unique constraint within the class using __table_args__
    __table_args__ = (
        UniqueConstraint('blockNumber', 'transactionIndex', 'logIndex',
                         name='uix_blocknumber_txindex_logindex'),
    )

    @staticmethod
    def insert_event(session, event_data):
        """
        Inserts an event into the database if it does not already exist.
        :param session: Database session
        :param event_data: Dictionary containing event data
        """
        try:
            distribution = TotalDistribution(**event_data)
            session.add(distribution)
            session.commit()
            logger.info("Event successfully inserted into the database.")
            return True
        except IntegrityError:
            session.rollback()
            logger.warning("Duplicate event detected and skipped.")
            return False
        except Exception as e:
            session.rollback()
            logger.error(
                "Error inserting event into the database: %s", e, exc_info=True)
            return False

    @staticmethod
    def reset_table():
        """
        Drops the 'total_distribution' table from the database and recreates it.
        :param engine: SQLAlchemy engine instance
        """
        try:
            # Drop the table if it exists
            TotalDistribution.__table__.drop(engine, checkfirst=True)
            logger.info("Table 'total_distribution' dropped successfully.")

            # Recreate the table
            TotalDistribution.__table__.create(engine, checkfirst=True)
            logger.info("Table 'total_distribution' created successfully.")
        except Exception as e:
            logger.error("Error resetting table: %s", e, exc_info=True)

    @staticmethod
    def get_last_block_number(session):
        """Retrieves the block number of the most recent event processed."""
        try:
            result = session.query(
                func.max(TotalDistribution.timestamp)).scalar()
            if result is None:
                return None
            else:
                # Find the block number corresponding to the maximum timestamp
                event = session.query(TotalDistribution).filter(
                    TotalDistribution.timestamp == result
                ).first()
                return event.blockNumber
        except Exception as e:
            logger.error("Error retrieving last block number: %s",
                         e, exc_info=True)
            return None


# Create the database engine
try:
    engine = create_engine(PG_DB_URI)
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Error creating database engine or tables: %s",
                 e, exc_info=True)
    raise

# Create a sessionmaker bound to the engine
Session = sessionmaker(bind=engine)
