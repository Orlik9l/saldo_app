import json
import logging
from datetime import datetime, date
from typing import List, Dict
from dataclasses import asdict
import os
import sys

# Add the parent directory to sys.path when running as script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from saldo.saldo_api import SaldoAPI
    from saldo.saldo_types import Transaction
else:
    from .saldo_api import SaldoAPI
    from .saldo_types import Transaction

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_transaction(data: Dict) -> Transaction:
    """
    Parse raw transaction data into a Transaction object
    
    Args:
        data: Raw transaction data from API
        
    Returns:
        Transaction object with typed data
    """
    try:
        # Map API response fields to Transaction fields
        transaction_data = {
            'transactionDate': data.get('transactionDate', 0),
            'title': data.get('title', ''),
            'journalList': data.get('journalList', []),
            'id': data.get('id', ''),
            'sourceDescription': data.get('sourceDescription'),
            'actionStatus': data.get('actionStatus'),
            'createdTimestamp': data.get('createdTimestamp'),
            'updatedTimestamp': data.get('updatedTimestamp')
        }
        
        logger.debug(f"Parsing transaction data: {json.dumps(transaction_data, indent=2)}")
        return Transaction(**transaction_data)
    except Exception as e:
        logger.error(f"Error parsing transaction: {str(e)}")
        # Return a minimal valid transaction
        return Transaction(
            transactionDate=data.get('transactionDate', 0),
            title=data.get('title', 'Unknown'),
            journalList=data.get('journalList', [{'accountName': 'Unknown', 'amount': 0}]),
            id=data.get('id', '0')
        )

def get_current_month_transactions() -> str:
    """
    Fetch transactions for the current month and save them to files
    
    Returns:
        str: Name of the main transactions file
    """
    try:
        logger.debug("Initializing SaldoAPI")
        api = SaldoAPI()
        
        logger.debug("Fetching transactions")
        response = api.get_transactions(
            page=0,
            size=1000,
            sort_by="DATE",
            sort_dir="DESC"
        )
        
        logger.debug(f"API Response: {json.dumps(response, indent=2)}")

        # Check if response has items
        if not response or 'items' not in response or not response['items']:
            logger.warning("No transactions found in API response")
            return save_empty_transactions()

        # Parse transactions into typed objects
        transactions: List[Transaction] = []
        for item in response['items']:
            try:
                transactions.append(parse_transaction(item))
            except Exception as e:
                logger.error(f"Error processing transaction: {str(e)}")
                continue
        
        if not transactions:
            logger.warning("No transactions were successfully parsed")
            return save_empty_transactions()

        # Convert back to dictionaries for JSON serialization
        items = [asdict(t) for t in transactions]
        
        # Save all transactions
        filename = "transactions.json"
        logger.debug(f"Saving {len(items)} transactions to {filename}")
        with open(filename, 'w') as f:
            json.dump(items, f, indent=4)
        
        # Save last 5 transactions
        filename_last_5 = "transactions_last_5.json"
        logger.debug(f"Saving last {min(5, len(items))} transactions to {filename_last_5}")
        with open(filename_last_5, 'w') as f:
            json.dump(items[:5], f, indent=4)

        return filename
    except Exception as e:
        logger.error(f"Error in get_current_month_transactions: {str(e)}")
        return save_empty_transactions()

def save_empty_transactions() -> str:
    """Save empty transaction lists when no data is available"""
    empty_data = []
    
    # Save empty main file
    filename = "transactions.json"
    with open(filename, 'w') as f:
        json.dump(empty_data, f)
    
    # Save empty recent file
    with open("transactions_last_5.json", 'w') as f:
        json.dump(empty_data, f)
    
    return filename

if __name__ == "__main__":
    try:
        output_file = get_current_month_transactions()
        print(f"Transactions saved to {output_file}")
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        logger.error(f"Error in main: {str(e)}", exc_info=True) 