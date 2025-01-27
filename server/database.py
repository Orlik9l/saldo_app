import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'saldo', 'db')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'transactions.db')

def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Create transactions table with unique constraint
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            entry_type TEXT NOT NULL,
            account_name TEXT NOT NULL,
            category_name TEXT NOT NULL,
            category_type TEXT,
            category_icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(transaction_date, title, amount, account_name)
        )
        ''')
        
        # Create indices for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_name ON transactions(category_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_name ON transactions(account_name)')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

def insert_transaction(transaction: Dict) -> bool:
    """Insert a single transaction into the database"""
    try:
        # Extract master and category entries
        master_entry = next((entry for entry in transaction['journalList'] if entry['master']), None)
        category_entry = next((entry for entry in transaction['journalList'] if not entry['master']), None)
        
        if not master_entry or not category_entry:
            logger.error("Missing master or category entry")
            return False
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Use INSERT OR IGNORE to skip duplicates
        cursor.execute('''
        INSERT OR IGNORE INTO transactions (
            transaction_date,
            title,
            amount,
            entry_type,
            account_name,
            category_name,
            category_type,
            category_icon
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction['transactionDate'],
            transaction['title'],
            master_entry['amount'],
            master_entry['entryType'],
            master_entry['account']['name'],
            category_entry['account']['name'],
            category_entry['account'].get('type'),
            category_entry['account'].get('icon')
        ))
        
        conn.commit()
        
        # Check if a row was actually inserted
        was_inserted = cursor.rowcount > 0
        if not was_inserted:
            logger.debug("Skipped duplicate transaction")
        
        conn.close()
        return was_inserted
        
    except Exception as e:
        logger.error(f"Error inserting transaction: {str(e)}")
        return False

def insert_transactions(transactions: List[Dict]) -> int:
    """Insert multiple transactions into the database"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        success_count = 0
        
        for transaction in transactions:
            try:
                # Extract master and category entries
                master_entry = next((entry for entry in transaction['journalList'] if entry['master']), None)
                category_entry = next((entry for entry in transaction['journalList'] if not entry['master']), None)
                
                if not master_entry or not category_entry:
                    logger.error("Missing master or category entry")
                    continue
                
                # Use INSERT OR IGNORE to skip duplicates
                cursor.execute('''
                INSERT OR IGNORE INTO transactions (
                    transaction_date,
                    title,
                    amount,
                    entry_type,
                    account_name,
                    category_name,
                    category_type,
                    category_icon
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction['transactionDate'],
                    transaction['title'],
                    master_entry['amount'],
                    master_entry['entryType'],
                    master_entry['account']['name'],
                    category_entry['account']['name'],
                    category_entry['account'].get('type'),
                    category_entry['account'].get('icon')
                ))
                
                if cursor.rowcount > 0:
                    success_count += 1
                
            except Exception as e:
                logger.error(f"Error inserting transaction: {str(e)}")
                continue
        
        conn.commit()
        return success_count
        
    except Exception as e:
        logger.error(f"Error in bulk insert: {str(e)}")
        return 0
    finally:
        conn.close()

def get_transactions(start_date: Optional[int] = None, end_date: Optional[int] = None) -> List[Dict]:
    """Get transactions with optional date range"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions"
        params = []
        
        if start_date is not None and end_date is not None:
            query += " WHERE transaction_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " ORDER BY transaction_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to list of dicts
        transactions = []
        for row in rows:
            transactions.append({
                'transactionDate': row['transaction_date'],
                'title': row['title'],
                'journalList': [
                    {
                        'master': True,
                        'entryType': row['entry_type'],
                        'amount': row['amount'],
                        'account': {'name': row['account_name']}
                    },
                    {
                        'master': False,
                        'entryType': 'DEBIT' if row['entry_type'] == 'CREDIT' else 'CREDIT',
                        'amount': row['amount'],
                        'account': {
                            'name': row['category_name'],
                            'type': row['category_type'],
                            'icon': row['category_icon']
                        }
                    }
                ]
            })
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return []
    finally:
        conn.close()

def get_recent_transactions(limit: int = 5) -> List[Dict]:
    """Get most recent transactions"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        
        # Convert rows to list of dicts (same format as get_transactions)
        transactions = []
        for row in rows:
            transactions.append({
                'transactionDate': row['transaction_date'],
                'title': row['title'],
                'journalList': [
                    {
                        'master': True,
                        'entryType': row['entry_type'],
                        'amount': row['amount'],
                        'account': {'name': row['account_name']}
                    },
                    {
                        'master': False,
                        'entryType': 'DEBIT' if row['entry_type'] == 'CREDIT' else 'CREDIT',
                        'amount': row['amount'],
                        'account': {
                            'name': row['category_name'],
                            'type': row['category_type'],
                            'icon': row['category_icon']
                        }
                    }
                ]
            })
        
        return transactions
        
    except Exception as e:
        logger.error(f"Error getting recent transactions: {str(e)}")
        return []
    finally:
        conn.close()

# Initialize database when module is imported
init_db() 