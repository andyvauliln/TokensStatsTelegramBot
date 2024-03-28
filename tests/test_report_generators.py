import pytest
from datetime import datetime, timedelta
from sqlalchemy import func
from src.models import Session, Event
from src.report_generators import TotalDistributionReportGenerator
from src.logging_config import logger

@pytest.fixture(scope="module")
def db_session():
    """Fixture to create a database session."""
    session = Session()
    yield session
    session.close()

@pytest.fixture
def setup_test_data(db_session):
    """Setup test data for report generator tests."""
    event_data = {
        "name": "TotalDistribution",
        "contractName": "AIX",
        "blockNumber": 123456,
        "blockHash": "0x123",
        "transactionIndex": 0,
        "transactionHash": "0xabc",
        "data": {
            "aix_processed": 1000,
            "aix_distributed": 500,
            "eth_bought": 200,
            "eth_distributed": 150,
            "distributor_wallet": "0x123",
            "distributor_balance": 2.5
        },
        "timestamp": datetime.utcnow() - timedelta(hours=2),
        "logIndex": 1,
        "removed": False
    }
    Event.insert_event(db_session, "TotalDistribution", event_data)

def test_generate_report(db_session, setup_test_data):
    """Test generating a report for TotalDistribution events."""
    report_generator = TotalDistributionReportGenerator("TotalDistribution")
    report = report_generator.generate_report()
    assert "Daily $AIX Stats:" in report
    assert "AIX processed: 1,000.00" in report
    assert "AIX distributed: 500.00" in report
    assert "ETH bought: 200.00" in report
    assert "ETH distributed: 150.00" in report
    assert "Distributor wallet: 0x123" in report
    assert "Distributor balance: 2.50 ETH" in report
    logger.info("Report generation test passed successfully.")