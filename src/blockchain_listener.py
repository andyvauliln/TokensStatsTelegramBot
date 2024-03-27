import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
import time
from .models import Session, TotalDistribution
from .config import ETH_NODE_URL
from datetime import datetime
from .logging_config import logger
from eth_abi import decode
import json

# Initialize web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Contract details
contract_address = "0xaBE235136562a5C2B02557E1CaE7E8c85F2a5da0"
abi = '''[
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "inputAixAmount",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "distributedAixAmount",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "swappedEthAmount",
                "type": "uint256"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "distributedEthAmount",
                "type": "uint256"
            }
        ],
        "name": "TotalDistribution",
        "type": "event"
    }
]'''
# compact_abi = json.dumps(json.loads(abi, strict=False))

# Instantiate contract
contract = w3.eth.contract(address=contract_address, abi=abi)


def fetch_distribution_events(from_block=0, to_block='latest'):
    """Fetch TotalDistribution events from the specified contract."""
    logger.info(
        f"Starting Fetching TotalDistribution envents from {from_block} to {to_block} for contract {contract_address}")
    try:
        event_filter = w3.eth.filter({
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': contract_address,
            'topics': ["0xe689c8111f40a171596b9d81ac47c6fe406d2297392957c5126c2f7448c58694"]
        })
        events = event_filter.get_all_entries()
        parsed_events = []
        logger.info(
            f"\n Total TotalDistribution Events Found: {len(events)}\n")
        for event in events:
            decoded_event = decode_event_data(event)
            if decoded_event:
                parsed_events.append(decoded_event)
        return parsed_events
    except Exception as e:
        logger.error(
            "Error fetching TotalDistribution events: %s", e, exc_info=True)
        return []


def decode_event_data(event):
    logger.info(
        f"\n Starting Decoding TotalDistribution envent data for TX: {event['transactionHash'].hex()} \n")
    event_data = event['data']
    inputAixAmount, distributedAixAmount, swappedEthAmount, distributedEthAmount = decode(
        ["uint256", "uint256", "uint256", "uint256"], event_data)

    # Convert numbers to a consistent format "{:,.2f}".format
    formatted_inputAixAmount = float(inputAixAmount / 1e18)
    formatted_distributedAixAmount = float(
        distributedAixAmount / 1e18)
    formatted_swappedEthAmount = float(swappedEthAmount / 1e18)
    formatted_distributedEthAmount = float(
        distributedEthAmount / 1e18)

    # Retrieve the transaction receipt to get the initiator address
    tx_receipt = w3.eth.get_transaction_receipt(event['transactionHash'].hex())
    distributor_wallet = tx_receipt['from']

    # Get the balance of the distributor wallet
    distributor_balance = float(w3.eth.get_balance(distributor_wallet) / 1e18)

    # Get the timestamp of the transaction
    block = w3.eth.get_block(event['blockNumber'])
    timestamp = datetime.utcfromtimestamp(block['timestamp'])

    event_data = {
        'blockNumber': event['blockNumber'],
        'blockHash': event['blockHash'].hex(),
        'logIndex': event['logIndex'],
        'removed': event['removed'],
        'transactionIndex': event['transactionIndex'],
        'transactionHash': event['transactionHash'].hex(),
        'aix_processed': formatted_inputAixAmount,
        'aix_distributed': formatted_distributedAixAmount,
        'eth_bought': formatted_swappedEthAmount,
        'eth_distributed': formatted_distributedEthAmount,
        'distributor_wallet': distributor_wallet,
        'distributor_balance': distributor_balance,
        'timestamp': timestamp,
    }
    logger.info(f"\n Decoded Event: \n {event_data}\n")
    return event_data


def save_event_in_db(event):
    """Process a single event, transforming it for database insertion."""
    logger.info("Starting Save TotalDistrebution event to DB: %s",
                event["transactionHash"])
    try:
        session = Session()
        if not event["removed"]:
            if TotalDistribution.insert_event(session, event):
                logger.info("Event processed and added to database: %s",
                            event["transactionHash"])
            else:
                logger.info("Duplicate event skipped: %s",
                            event['transactionHash'])
    except Exception as e:
        logger.error("Error processing event: %s", e, exc_info=True)


def listen_for_events(start_block):
    """Main listener loop for new events."""
    try:
        logger.info(
            "Starting event listener from specified block: %s", start_block)

        while True:
            events = fetch_distribution_events(from_block=start_block)
            if events:
                for event in events:
                    save_event_in_db(event)
                # Update the start_block to the next block after the last event processed to avoid re-fetching the same events
                start_block = events[-1]['blockNumber'] + 1
            else:
                logger.info("No new TotalDistribution events found.")

            time.sleep(10)  # Wait a bit before querying for new events
    except Exception as e:
        logger.error("Error in event listener loop: %s", e, exc_info=True)


if __name__ == "__main__":
    listen_for_events(start_block=19516698)
