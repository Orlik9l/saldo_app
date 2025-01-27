import json
import requests
from typing import Dict, Optional
from datetime import datetime
import jwt
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

REFRESH_TOKEN_URL = "https://admin-api.saldoapps.com/admin-api/v1/user/auth/refresh-token"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'tokens.json')

def load_tokens() -> Dict:
    """Load tokens from the token file"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            
            # Handle token structure
            if 'jwt' in data and isinstance(data['jwt'], dict):
                if 'accessToken' in data['jwt'] and 'refreshToken' in data['jwt']:
                    return data['jwt']
            
            logger.error(f"Invalid token structure in {TOKEN_FILE}")
            raise ValueError(f"Invalid token structure in {TOKEN_FILE}")
            
    except FileNotFoundError:
        logger.error(f"Token file {TOKEN_FILE} not found")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {TOKEN_FILE}")
        raise
    except Exception as e:
        logger.error(f"Error loading tokens: {str(e)}")
        raise

def save_tokens(response_data: Dict) -> None:
    """
    Save the complete response data to the token file
    Args:
        response_data: Complete response containing jwt and user data
    """
    try:
        # Validate the response structure
        if not isinstance(response_data, dict):
            logger.error("Invalid response format: not a dictionary")
            raise ValueError("Response must be a dictionary")
        
        # Check if response has jwt field or is already in the right format
        if 'jwt' in response_data and isinstance(response_data['jwt'], dict):
            tokens = response_data['jwt']
        else:
            tokens = response_data
            response_data = {'jwt': tokens}
            
        if not isinstance(tokens, dict) or 'accessToken' not in tokens or 'refreshToken' not in tokens:
            logger.error("Invalid token format")
            raise ValueError("Tokens must contain 'accessToken' and 'refreshToken'")
        
        # Save the complete response
        with open(TOKEN_FILE, 'w') as f:
            json.dump(response_data, f, indent=4)
        logger.debug("Complete response saved successfully")
    except Exception as e:
        logger.error(f"Error saving response data: {str(e)}")
        raise

def refresh_tokens() -> Dict[str, str]:
    """
    Refresh the JWT tokens using the refresh token stored in tokens.json
    Returns the complete response containing new tokens and user data
    """
    try:
        current_tokens = load_tokens()
        refresh_token = current_tokens.get('refreshToken')
        
        if not refresh_token:
            logger.error("No refresh token found")
            raise ValueError("No refresh token found")
        
        logger.debug("Attempting to refresh tokens")
        response = requests.post(
            REFRESH_TOKEN_URL,
            json={"refreshToken": refresh_token}
        )
        response.raise_for_status()
        
        # Get the complete response data
        response_data = response.json()
        
        # Save complete response
        save_tokens(response_data)
        logger.debug("Tokens and user data refreshed successfully")
        
        # Return the jwt part for compatibility with other functions
        return response_data['jwt'] if 'jwt' in response_data else response_data
    except Exception as e:
        logger.error(f"Error refreshing tokens: {str(e)}")
        raise

def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired"""
    try:
        logger.debug("Checking token expiration")
        payload = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = payload['exp']
        is_expired = datetime.fromtimestamp(exp_timestamp) <= datetime.now()
        logger.debug(f"Token expired: {is_expired}")
        return is_expired
    except Exception as e:
        logger.error(f"Error checking token expiration: {str(e)}")
        return True

def get_access_token() -> str:
    """
    Get the current access token, refreshing if necessary
    Returns the access token string
    """
    try:
        logger.debug("Getting access token")
        tokens = load_tokens()
        access_token = tokens.get('accessToken')
        
        if not access_token:
            logger.error("No access token found")
            raise ValueError("No access token found")
        
        if is_token_expired(access_token):
            logger.debug("Token expired, refreshing")
            tokens = refresh_tokens()
            access_token = tokens['accessToken']
        
        return access_token
    except Exception as e:
        logger.error(f"Error in get_access_token: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        new_tokens = refresh_tokens()
        print("Tokens refreshed successfully!")
    except Exception as e:
        print(f"Error refreshing tokens: {e}") 