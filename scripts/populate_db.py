#!/usr/bin/env python3
"""
Database Population Script for Saldo App

This script reads transformed transaction files and populates the SQLite database.
It can be used to initially populate the database or update it with new transactions.

Usage:
    ./populate_db.py [--clear]
"""

import os
import json
import argparse
import sys

# Add server directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from database import init_db, insert_transactions, get_db

def clear_database():
    """Clear all data from the transactions table"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        print("Database cleared successfully")
    except Exception as e:
        print(f"Error clearing database: {str(e)}")
    finally:
        conn.close()

def load_transactions(filename: str) -> list:
    """Load transactions from a JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading transactions from {filename}: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description='Populate SQLite database with transformed transaction data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--clear', action='store_true',
                      help='Clear existing data before populating')
    args = parser.parse_args()

    # Initialize database
    init_db()
    
    # Clear database if requested
    if args.clear:
        clear_database()

    # Set up paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    transformed_dir = os.path.join(base_dir, 'saldo', 'transformed')
    
    # Load and insert all transactions
    all_transactions = os.path.join(transformed_dir, 'transactions_transformed.json')
    recent_transactions = os.path.join(transformed_dir, 'transactions_last_5_transformed.json')
    
    files_to_process = [
        ('All Transactions', all_transactions),
        ('Recent Transactions', recent_transactions)
    ]
    
    total_inserted = 0
    for description, filepath in files_to_process:
        if os.path.exists(filepath):
            transactions = load_transactions(filepath)
            if transactions:
                inserted = insert_transactions(transactions)
                total_inserted += inserted
                print(f"\nProcessed {description}:")
                print(f"- Transactions loaded: {len(transactions)}")
                print(f"- Transactions inserted: {inserted}")
        else:
            print(f"\nWarning: File not found - {filepath}")
    
    print(f"\nDatabase population complete: {total_inserted} total transactions inserted")

if __name__ == '__main__':
    main() 