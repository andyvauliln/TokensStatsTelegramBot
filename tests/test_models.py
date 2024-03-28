import pytest
from sqlalchemy.exc import IntegrityError
from src.models import Session, Event
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def db_session():
    """Fixture to create a database session."""
    session = Session()
    yield session
    session.close()

def test_insert_event(db_session):
    """Test inserting an event into the database."""
    event_data = {
        "name": "TestEvent",
        "contractName": "AIX",
        "blockNumber": 123456,
        "blockHash": "0x123",
        "transactionIndex": 0,
        "transactionHash": "0xabc",
        "data": {"key": "value"},
        "timestamp": datetime.utcnow(),
        "logIndex": 1,
        "removed": False
    }
    result = Event.insert_event(db_session, "TestEvent", event_data)
    assert result is True, "Event should be inserted successfully."

def test_prevent_duplicate_event_insertion(db_session):
    """Test that duplicate events are not inserted into the database."""
    event_data = {
        "name": "DuplicateEvent",
        "contractName": "AIX",
        "blockNumber": 1234567,
        "blockHash": "0x1234",
        "transactionIndex": 1,
        "transactionHash": "0xabcd",
        "data": {"key": "value"},
        "timestamp": datetime.utcnow(),
        "logIndex": 2,
        "removed": False
    }
    # Insert the event for the first time
    first_insertion_result = Event.insert_event(db_session, "DuplicateEvent", event_data)
    assert first_insertion_result is True, "First insertion should be successful."

    # Attempt to insert the same event again
    with pytest.raises(IntegrityError):
        second_insertion_result = Event.insert_event(db_session, "DuplicateEvent", event_data)
        assert second_insertion_result is False, "Duplicate event insertion should be prevented."

def test_get_last_event_block_number(db_session):
    """Test retrieving the last event block number."""
    event_name = "TestEvent"
    # Insert a test event to ensure there's data to query
    test_event_data = {
        "name": event_name,
        "contractName": "AIX",
        "blockNumber": 12345678,
        "blockHash": "0x12345",
        "transactionIndex": 2,
        "transactionHash": "0xabcde",
        "data": {"key": "value"},
        "timestamp": datetime.utcnow() - timedelta(days=1),
        "logIndex": 3,
        "removed": False
    }
    Event.insert_event(db_session, event_name, test_event_data)

    last_block_number = Event.get_last_event_block_number(db_session, event_name)
    assert last_block_number == 12345678, "Should return the correct last event block number."