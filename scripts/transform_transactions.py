#!/usr/bin/env python3
"""
Transaction Transformer for Saldo App

This script transforms raw transaction data from the Saldo API into a minimal format
containing only the necessary data for the application.

Directory Structure:
    saldo/
    ├── raw/            # Raw transaction files from the API
    ├── transformed/    # Minimized transaction files for the app
    └── cache/          # Cache files (tokens, temporary data)

Usage:
    ./transform_transactions.py [--input-dir DIR] [--output-dir DIR]
"""

import json
import os
import argparse
from typing import Dict, List, Optional

class TransactionTransformer:
    def __init__(self, base_dir: str = 'saldo'):
        """Initialize the transformer with base directory."""
        self.base_dir = base_dir
        self.raw_dir = os.path.join(base_dir, 'raw')
        self.transformed_dir = os.path.join(base_dir, 'transformed')
        
        # Ensure directories exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.transformed_dir, exist_ok=True)

    def transform_transaction(self, transaction: Dict) -> Optional[Dict]:
        """Transform a single transaction to extract only necessary data."""
        try:
            # Find master and category entries
            master_entry = next((entry for entry in transaction['journalList'] if entry['master']), None)
            category_entry = next((entry for entry in transaction['journalList'] if not entry['master']), None)

            if not master_entry or not category_entry:
                return None

            # Extract only needed data
            transformed = {
                'transactionDate': transaction['transactionDate'],
                'title': transaction.get('title') or transaction.get('sourceDescription', 'No Description'),
                'journalList': [
                    {
                        'master': True,
                        'entryType': master_entry['entryType'],
                        'amount': master_entry['amount'],
                        'account': {
                            'name': master_entry['account']['name']
                        }
                    },
                    {
                        'master': False,
                        'entryType': category_entry['entryType'],
                        'amount': category_entry['amount'],
                        'account': {
                            'name': category_entry['account']['name'],
                            'type': category_entry['account']['type'],
                            'icon': category_entry['account'].get('icon')
                        }
                    }
                ]
            }
            return transformed
        except Exception as e:
            print(f"Error transforming transaction: {str(e)}")
            return None

    def transform_file(self, input_filename: str, output_filename: str) -> bool:
        """Transform a single transactions file."""
        input_path = os.path.join(self.raw_dir, input_filename)
        output_path = os.path.join(self.transformed_dir, output_filename)
        
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                print(f"Input file not found: {input_path}")
                return False

            # Read input file
            with open(input_path, 'r') as f:
                transactions = json.load(f)

            # Transform transactions
            transformed_transactions = []
            for transaction in transactions:
                transformed = self.transform_transaction(transaction)
                if transformed:
                    transformed_transactions.append(transformed)

            # Write output file
            with open(output_path, 'w') as f:
                json.dump(transformed_transactions, f, indent=2)

            # Print statistics
            original_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            reduction = (1 - new_size/original_size) * 100
            
            print(f"\nTransformed {input_filename}:")
            print(f"- Transactions processed: {len(transformed_transactions)}")
            print(f"- Original size: {original_size:,} bytes")
            print(f"- New size: {new_size:,} bytes")
            print(f"- Size reduction: {reduction:.1f}%")
            print(f"- Output saved to: {output_path}")
            
            return True

        except Exception as e:
            print(f"Error processing file {input_filename}: {str(e)}")
            return False

    def transform_all(self) -> None:
        """Transform all transaction files."""
        files_to_transform = [
            ('transactions.json', 'transactions_transformed.json'),
            ('transactions_last_5.json', 'transactions_last_5_transformed.json')
        ]
        
        success_count = 0
        for input_file, output_file in files_to_transform:
            if self.transform_file(input_file, output_file):
                success_count += 1
        
        print(f"\nTransformation complete: {success_count}/{len(files_to_transform)} files processed successfully")

def main():
    parser = argparse.ArgumentParser(
        description='Transform Saldo transaction files to a minimal format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--base-dir', default='saldo',
                      help='Base directory containing raw/ and transformed/ subdirectories (default: saldo)')
    args = parser.parse_args()

    # Create transformer and process files
    transformer = TransactionTransformer(args.base_dir)
    transformer.transform_all()

if __name__ == '__main__':
    main() 