import pytest
from unittest.mock import patch
from web3 import Web3
from web3.middleware import geth_poa_middleware
from src.event_listener import fetch_and_process_events, save_event_in_db
from src.models import Event, Session

# Setup a mock Web3 provider
@pytest.fixture
def mock_web3():
    w3 = Web3(Web3.EthereumTesterProvider())
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

# Test the fetch_and_process_events function
def test_fetch_and_process_events(mock_web3):
    with patch('src.event_listener.w3', new_callable=lambda: mock_web3):
        event_name = "TotalDistribution"
        event_config = {
            "address": "0xaBE235136562a5C2B02557E1CaE7E8c85F2a5da0",
            "topics": ["0xe689c8111f40a171596b9d81ac47c6fe406d2297392957c5126c2f7448c58694"],
        }
        from_block = 0
        to_block = 'latest'

        # Mock the response from the Ethereum blockchain
        mock_web3.eth.filter.return_value.get_all_entries.return_value = []

        # Call the function with the mocked Web3 object
        last_block = fetch_and_process_events(event_name, event_config, from_block, to_block)

        # Assert that the function returns the from_block when no events are found
        assert last_block == from_block

# Test the save_event_in_db function
def test_save_event_in_db():
    event_name = "TotalDistribution"
    event_data = {
        "name": event_name,
        "contractName": "AIX",
        "blockNumber": 123456,
        "blockHash": "0x123",
        "transactionIndex": 0,
        "transactionHash": "0xabc",
        "data": {},
        "timestamp": "2021-01-01T00:00:00",
        "logIndex": 0,
        "removed": False
    }

    # Use a session in a context manager to ensure it's closed after the test
    with Session() as session:
        # Call the function to save the event in the database
        result = Event.insert_event(session, event_name, event_data)

        # Assert that the event was inserted successfully
        assert result is True

        # Try to insert the same event again to test duplicate handling
        result_duplicate = Event.insert_event(session, event_name, event_data)

        # Assert that the duplicate event was not inserted
        assert result_duplicate is False