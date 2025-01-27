import requests
import logging
import json
from typing import Dict
import os
import sys

# Add the parent directory to sys.path when running as script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from saldo.auth import get_access_token
else:
    from .auth import get_access_token

logger = logging.getLogger(__name__)

class SaldoAPI:
    BASE_URL = "https://api.saldoapps.com/v6"
    ACCOUNT_ID = "381497"  # Your account ID

    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Get headers with current access token"""
        token = get_access_token()
        logger.debug(f"Using token: {token[:50]}...")  # Log only part of the token for security
        headers = {
            "Token": token,
            "Content-Type": "application/json"
        }
        logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
        return headers

    def get_transactions(self, page: int = 0, size: int = 50, sort_by: str = "DATE", sort_dir: str = "DESC") -> Dict:
        """
        Get transactions list
        
        Args:
            page: Page number (0-based)
            size: Number of items per page
            sort_by: Field to sort by (e.g., "DATE")
            sort_dir: Sort direction ("ASC" or "DESC")
            
        Returns:
            Dict containing transactions data
        """
        url = f"{self.BASE_URL}/{self.ACCOUNT_ID}/transactions"
        params = {
            "page": page,
            "size": size,
            "sort.by": sort_by,
            "sort.dir": sort_dir
        }
        
        logger.debug(f"Making request to {url}")
        logger.debug(f"Request params: {json.dumps(params, indent=2)}")
        
        try:
            response = requests.get(
                url=url,
                headers=self._get_headers(),
                params=params
            )
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            
            if response.status_code != 200:
                logger.error(f"Error response: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Response data: {json.dumps(data, indent=2)}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response: {e.response.text}")
            raise

    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """
        Make a request to the Saldo API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data for POST/PUT requests
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method,
            url=url,
            headers=self._get_headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    try:
        api = SaldoAPI()
        new_tokens = api.make_request("POST", "user/auth/refresh-token")
        print("Tokens refreshed successfully!")
    except Exception as e:
        print(f"Error refreshing tokens: {e}")
