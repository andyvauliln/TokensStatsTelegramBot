from abc import ABC, abstractmethod
import json
from .logging_config import logger
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_abi import decode
from .config import ETH_NODE_URL
from datetime import datetime

w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


class EventParser(ABC):
    """
    Abstract base class for event parsers. Each event type should have a subclass
    implementing the parse_event_data method.
    """

    @abstractmethod
    def parse_event_data(self, event, event_config):
        """
        Parses the raw event data into a structured format.

        :param event_data: The raw event data.
        :return: A dictionary representing the parsed data.
        """
        pass


class TotalDistributionParser(EventParser):
    """
    Parser for TotalDistribution events.
    """

    def parse_event_data(self, event, event_config):
        """
        Parses TotalDistribution event data.

        :param event_data: The raw event data.
        :return: A dictionary representing the parsed data.
        """
        try:
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
            tx_receipt = w3.eth.get_transaction_receipt(
                event['transactionHash'].hex())
            distributor_wallet = tx_receipt['from']

            # Get the balance of the distributor wallet
            distributor_balance = float(
                w3.eth.get_balance(distributor_wallet) / 1e18)

            # Get the timestamp of the transaction
            block = w3.eth.get_block(event['blockNumber'])
            timestamp = datetime.utcfromtimestamp(block['timestamp'])

            event_data_dict = {
                'aix_processed': formatted_inputAixAmount,
                'aix_distributed': formatted_distributedAixAmount,
                'eth_bought': formatted_swappedEthAmount,
                'eth_distributed': formatted_distributedEthAmount,
                'distributor_wallet': distributor_wallet,
                'distributor_balance': distributor_balance,
            }

            event_data = {
                'blockNumber': event['blockNumber'],
                'name': event_config['db_name'],
                'contractName': event_config['contractName'],
                'blockHash': event['blockHash'].hex(),
                'logIndex': event['logIndex'],
                'removed': event['removed'],
                'transactionIndex': event['transactionIndex'],
                'transactionHash': event['transactionHash'].hex(),
                'data': event_data_dict,
                'timestamp': timestamp,
            }

            logger.info("TotalDistribution event data parsed successfully.")
            return event_data
        except Exception as e:
            logger.error(
                "Error parsing TotalDistribution event data: %s", e, exc_info=True)
            return {}


def get_event_parser(event_name):
    """
    Factory function to get the appropriate event parser based on the event name.

    :param event_name: The name of the event.
    :return: An instance of the appropriate subclass of EventParser.
    """
    if event_name == "TotalDistribution":
        return TotalDistributionParser()
    else:
        logger.error("No parser found for event: %s", event_name)
        return None
