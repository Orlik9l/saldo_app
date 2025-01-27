from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import logging
from datetime import datetime
from server.database import get_transactions, get_recent_transactions

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app)

def parse_date_timestamp(date_str: str) -> int:
    """Convert date string to Unix timestamp in milliseconds"""
    try:
        if not date_str:
            return 0
        # Parse the date string to datetime at the start of the day (00:00:00)
        dt = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        # Convert to milliseconds
        ts = int(dt.timestamp() * 1000)
        logger.debug(f"Converted date {date_str} to timestamp {ts}")
        return ts
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        return 0

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/utils/<path:filename>')
def serve_utils(filename):
    return send_from_directory('utils', filename)

@app.route('/api/transactions', methods=['GET'])
def get_transactions_handler():
    try:
        logger.debug(f"Received request with params: {request.args}")
        
        # Get date range from query parameters
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        logger.debug(f"Date range: {start_date} to {end_date}")

        start_ts = None
        end_ts = None
        
        if start_date and end_date:
            # Convert dates to timestamps
            start_ts = parse_date_timestamp(start_date)
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
            end_ts = int(end_dt.timestamp() * 1000)
            
            logger.debug(f"Date range in timestamps: {start_ts} to {end_ts}")

        # Get transactions from database
        transactions = get_transactions(start_ts, end_ts)
        logger.debug(f"Retrieved {len(transactions)} transactions")
        
        return jsonify({
            'status': 'success',
            'data': transactions
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transactions/recent', methods=['GET'])
def get_recent_transactions_handler():
    try:
        transactions = get_recent_transactions(limit=5)
        logger.debug(f"Retrieved {len(transactions)} recent transactions")
        
        return jsonify({
            'status': 'success',
            'data': transactions
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent transactions: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 