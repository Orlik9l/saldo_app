import json
from datetime import datetime
from collections import defaultdict
from saldo_types import Transaction, JournalEntry, Account, Asset, BankProperties, LiabilityProperties
from typing import List, Dict

def create_asset(data: Dict) -> Asset:
    return Asset(**data)

def create_bank_properties(data: Dict) -> BankProperties:
    return BankProperties(**data) if data else None

def create_liability_properties(data: Dict) -> LiabilityProperties:
    return LiabilityProperties(**data) if data else None

def create_account(data: Dict) -> Account:
    if data.get('bankProperties'):
        data['bankProperties'] = create_bank_properties(data['bankProperties'])
    if data.get('liabilityProperties'):
        data['liabilityProperties'] = create_liability_properties(data['liabilityProperties'])
    return Account(**data)

def create_journal_entry(data: Dict) -> JournalEntry:
    data['asset'] = create_asset(data['asset'])
    data['account'] = create_account(data['account'])
    if data.get('associatedAccount'):
        data['associatedAccount'] = create_account(data['associatedAccount'])
    return JournalEntry(**data)

def load_transactions(filename: str) -> List[Transaction]:
    """Load transactions from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
        transactions = []
        for tx_data in data:
            # Convert journal entries
            tx_data['journalList'] = [create_journal_entry(j) for j in tx_data['journalList']]
            transactions.append(Transaction(**tx_data))
        return transactions

def get_latest_month_transactions(transactions: List[Transaction]) -> tuple[List[Transaction], datetime]:
    """Get transactions from the most recent month"""
    if not transactions:
        return [], None
    
    # Find the most recent transaction date
    latest_date = max(tx.get_datetime() for tx in transactions)
    
    # Filter transactions for the latest month
    latest_month_txs = [
        tx for tx in transactions 
        if tx.get_datetime().year == latest_date.year 
        and tx.get_datetime().month == latest_date.month
    ]
    
    return latest_month_txs, latest_date

def get_category(tx: Transaction) -> str:
    """Get category from transaction's tags"""
    # Get tags from the master journal entry
    master_entry = next(j for j in tx.journalList if j.master)
    # Return first tag or 'Uncategorized' if no tags
    return master_entry.tags[0] if master_entry.tags else 'Uncategorized'

def is_expense(tx: Transaction) -> bool:
    """Determine if a transaction is an expense"""
    master_entry = next(j for j in tx.journalList if j.master)
    # CREDIT with positive amount is money going out (expense)
    return master_entry.entryType == "CREDIT" and master_entry.amount > 0

def analyze_expenses():
    # Load all transactions
    print("Loading transactions...")
    transactions = load_transactions('transactions.json')
    print(f"Loaded {len(transactions)} transactions")
    
    # Print date range
    dates = [tx.get_datetime() for tx in transactions]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")
    
    # Get latest month transactions
    latest_txs, latest_date = get_latest_month_transactions(transactions)
    
    if not latest_txs:
        print("\nNo transactions found")
        return
    
    # Filter for expenses
    expenses = [tx for tx in latest_txs if is_expense(tx)]
    print(f"\nFound {len(expenses)} expenses in {latest_date.strftime('%B %Y')}")
    
    # Group by category and currency
    categories: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for tx in expenses:
        category = get_category(tx)
        currency = tx.get_currency()
        master_entry = next(j for j in tx.journalList if j.master)
        categories[category][currency] += master_entry.amount
    
    # Print results
    month_year = latest_date.strftime('%B %Y')
    print(f"\nExpenses by Category - {month_year}")
    print("-" * 60)
    totals = defaultdict(float)
    
    for category, currencies in sorted(categories.items(), key=lambda x: sum(x[1].values()), reverse=True):
        print(f"{category:<25}", end="")
        for currency, amount in currencies.items():
            print(f" {amount:>10.2f} {currency}", end="")
            totals[currency] += amount
        print()  # New line after each category
    
    print("-" * 60)
    print("Total:", end="")
    for currency, total in totals.items():
        print(f" {total:>10.2f} {currency}", end="")
    print()  # Final newline

if __name__ == '__main__':
    analyze_expenses() 