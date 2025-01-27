import requests
import time
import os
from dotenv import load_dotenv
import csv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
MONOBANK_API_TOKEN = os.getenv('MONOBANK_API_TOKEN')
ACCOUNT_ID = os.getenv('MONOBANK_ACCOUNT_ID')

if not MONOBANK_API_TOKEN or not ACCOUNT_ID:
    raise ValueError("Missing required environment variables")

# Define the initial time range
end_time = int(time.time())  # Current time
start_time = end_time - 31 * 24 * 60 * 60  # Last 31 days (max allowed by Monobank API)

# Monobank API base URL
base_url = "https://api.monobank.ua/personal/statement"

# Set headers
headers = {
    "X-Token": MONOBANK_API_TOKEN
}

all_transactions = []  # To store all retrieved transactions

# Initial request
url = f"{base_url}/{ACCOUNT_ID}/{start_time}/{end_time}"

while True:
    # Add delay between requests to respect rate limits
    time.sleep(1)  # 1 second delay between requests

    try:
        response = requests.get(url, headers=headers)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        response.raise_for_status()

        # Parse the response
        transactions = response.json()

        if not transactions:
            print("No more transactions to fetch.")
            break
        
        all_transactions.extend(transactions)  # Add to the full list
        print(f"Fetched {len(transactions)} transactions")

        # If we got 500 transactions (max per request), fetch more
        if len(transactions) == 500:
            last_transaction_time = transactions[-1]['time']
            # Update URL to fetch from the last transaction time
            url = f"{base_url}/{ACCOUNT_ID}/{start_time}/{last_transaction_time}"
        else:
            # Less than 500 transactions received, we're done
            break

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            continue  # Skip to next iteration if rate limited
        print(f"HTTP error occurred: {http_err}")
        print(f"Response: {response.text}")
        break
    except Exception as err:
        print(f"Other error occurred: {err}")
        break

# Print total transactions
print(f"Total transactions retrieved: {len(all_transactions)}")

# Create a dictionary to store monthly transaction counts
monthly_counts = {}

# Get current month and year for the filename
current_date = datetime.now()
filename = f"transactions_{current_date.strftime('%Y_%m')}.csv"

# Open CSV file for writing
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Date', 'Description', 'Amount', 'Balance']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for transaction in all_transactions:
        # Get the month and year for this transaction
        transaction_date = time.localtime(transaction['time'])
        month_key = time.strftime('%Y-%m', transaction_date)
        
        # Increment the count for this month
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        # Write transaction to CSV
        writer.writerow({
            'Date': time.strftime('%Y-%m-%d %H:%M:%S', transaction_date),
            'Description': transaction['description'],
            'Amount': f"{transaction['amount'] / 100:.2f}",
            'Balance': f"{transaction['balance'] / 100:.2f}"
        })
        
        # Print transaction details
        print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S', transaction_date)}")
        print(f"Description: {transaction['description']}")
        print(f"Amount: {transaction['amount'] / 100:.2f} UAH")
        print(f"Balance: {transaction['balance'] / 100:.2f} UAH")
        print("-" * 30)

print(f"\nTransactions exported to {filename}")

# Print monthly transaction counts
print("\nMonthly Transaction Counts:")
for month, count in sorted(monthly_counts.items()):
    print(f"{month}: {count} transactions")
