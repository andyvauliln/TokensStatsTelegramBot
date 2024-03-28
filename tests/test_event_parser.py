import pytest
from unittest.mock import patch
from src.event_parser import TotalDistributionParser
from decimal import Decimal

@pytest.fixture
def mock_event():
    return {
        'blockNumber': 123456,
        'blockHash': '0x123abc',
        'transactionHash': '0xabcd1234',
        'logIndex': 1,
        'removed': False,
        'data': '0x' + '01' * 32 + '02' * 32 + '03' * 32 + '04' * 32,
        'transactionIndex': 0
    }

@pytest.fixture
def expected_data():
    return {
        'blockNumber': 123456,
        'name': 'TotalDistribution',
        'contractName': 'AIX',
        'blockHash': '0x123abc',
        'logIndex': 1,
        'removed': False,
        'transactionIndex': 0,
        'transactionHash': '0xabcd1234',
        'data': {
            'aix_processed': Decimal('1.157920892373162e+77'),
            'aix_distributed': Decimal('2.003529309238059e+77'),
            'eth_bought': Decimal('2.848034883359073e+77'),
            'eth_distributed': Decimal('3.692540457480087e+77'),
            'distributor_wallet': '0x0',
            'distributor_balance': Decimal('100')
        },
        'timestamp': None
    }

@patch('src.event_parser.Web3')
@patch('src.event_parser.datetime')
def test_total_distribution_parser(mock_datetime, mock_web3, mock_event, expected_data):
    # Mock the Web3 and datetime functionalities
    mock_web3.eth.get_transaction_receipt.return_value = {'from': '0x0'}
    mock_web3.eth.get_balance.return_value = 100 * 10**18  # Wei
    mock_web3.eth.get_block.return_value = {'timestamp': 1234567890}
    mock_datetime.utcfromtimestamp.return_value = None  # Assuming we don't need the actual datetime

    # Initialize the parser
    parser = TotalDistributionParser()

    # Parse the mock event
    parsed_data = parser.parse_event_data(mock_event, {'db_name': 'TotalDistribution', 'contractName': 'AIX'})

    # Adjust parsed_data for comparison
    parsed_data['data']['aix_processed'] = Decimal(parsed_data['data']['aix_processed'])
    parsed_data['data']['aix_distributed'] = Decimal(parsed_data['data']['aix_distributed'])
    parsed_data['data']['eth_bought'] = Decimal(parsed_data['data']['eth_bought'])
    parsed_data['data']['eth_distributed'] = Decimal(parsed_data['data']['eth_distributed'])
    parsed_data['data']['distributor_balance'] = Decimal(parsed_data['data']['distributor_balance'])

    # Assert the parsed data matches the expected data
    assert parsed_data == expected_data, "Parsed data does not match expected data"