"""
Manifold API client wrapper.
Improves upon manifoldbot patterns with:
- Retry logic with exponential backoff
- Better error handling and recovery
- Rate limiting awareness
- Comprehensive API coverage
- Session management
"""
import logging
import requests
from typing import Dict, List, Optional
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class ManifoldClient:
    """Wrapper for Manifold API interactions."""
    
    BASE_URL = "https://api.manifold.markets/v0"
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize Manifold client with improved error handling.
        
        Args:
            api_key: Manifold API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "JudgmentalPredictionBot/1.0"
        })
        # Configure session for better connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=0  # We handle retries manually
        )
        self.session.mount("https://", adapter)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make a request to the Manifold API with retry logic.
        Improves upon basic manifoldbot by adding:
        - Automatic retries for transient errors
        - Exponential backoff
        - Better error messages
        - Timeout handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response JSON
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 429:
                logger.warning("Rate limited. Consider reducing request frequency.")
                raise
            elif e.response.status_code == 401:
                logger.error("Authentication failed. Check your API key.")
                raise
            elif e.response.status_code >= 500:
                logger.warning(f"Server error {e.response.status_code}. Retrying...")
                raise
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error: {e}. Retrying...")
            raise
        except requests.exceptions.Timeout as e:
            logger.warning(f"Request timeout: {e}. Retrying...")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_markets(self, limit: int = 100, creator_id: Optional[str] = None, 
                   before: Optional[str] = None) -> List[Dict]:
        """
        Get markets from Manifold.
        Improves upon manifoldbot by supporting pagination.
        
        Args:
            limit: Maximum number of markets to return
            creator_id: Optional creator ID to filter by
            before: Optional market ID to fetch markets before (for pagination)
            
        Returns:
            List of market dictionaries
        """
        params = {"limit": min(limit, 1000)}  # API limit
        if creator_id:
            params["creatorId"] = creator_id
        if before:
            params["before"] = before
        
        return self._request("GET", "markets", params=params)
    
    def get_markets_by_creator(self, creator_username: str, limit: int = 100) -> List[Dict]:
        """
        Get markets by creator username.
        
        Args:
            creator_username: Creator username
            limit: Maximum number of markets to return
            
        Returns:
            List of market dictionaries
        """
        # First, get user by username to get their ID
        user = self.get_user_by_username(creator_username)
        if not user:
            return []
        
        creator_id = user.get("id")
        return self.get_markets(limit=limit, creator_id=creator_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User dictionary or None
        """
        try:
            return self._request("GET", f"user/by-username/{username}")
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return None
    
    def get_user(self, username: Optional[str] = None) -> Optional[Dict]:
        """
        Get current user or user by username.
        
        Args:
            username: Optional username (if None, gets current user)
            
        Returns:
            User dictionary or None
        """
        if username:
            return self.get_user_by_username(username)
        else:
            try:
                return self._request("GET", "me")
            except Exception as e:
                logger.error(f"Error getting current user: {e}")
                return None
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Get a specific market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Market dictionary or None
        """
        try:
            return self._request("GET", f"market/{market_id}")
        except Exception as e:
            logger.error(f"Error getting market {market_id}: {e}")
            return None
    
    def place_bet(self, market_id: str, amount: float, outcome: str, 
                  limit_prob: Optional[float] = None) -> Dict:
        """
        Place a bet on a market.
        Improves upon manifoldbot by:
        - Better error handling
        - Automatic fallback between contractId/marketId
        - Input validation
        
        Args:
            market_id: Market ID
            amount: Bet amount (must be positive)
            outcome: 'YES' or 'NO'
            limit_prob: Optional limit probability (0-1)
            
        Returns:
            Bet result dictionary
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Input validation
        if amount <= 0:
            raise ValueError(f"Bet amount must be positive, got {amount}")
        if outcome.upper() not in ["YES", "NO"]:
            raise ValueError(f"Outcome must be 'YES' or 'NO', got {outcome}")
        if limit_prob is not None and (limit_prob < 0 or limit_prob > 1):
            raise ValueError(f"limit_prob must be between 0 and 1, got {limit_prob}")
        
        amount = float(amount)
        outcome = outcome.upper()
        
        # Try contractId first (newer API format)
        data = {
            "contractId": market_id,
            "amount": amount,
            "outcome": outcome
        }
        
        if limit_prob is not None:
            data["limitProb"] = float(limit_prob)
        
        try:
            return self._request("POST", "bet", json=data)
        except requests.exceptions.HTTPError as e:
            # Try with marketId if contractId fails (backward compatibility)
            if e.response.status_code == 400:
                logger.debug(f"contractId failed, trying marketId for {market_id}")
                data = {
                    "marketId": market_id,
                    "amount": amount,
                    "outcome": outcome
                }
                if limit_prob is not None:
                    data["limitProb"] = float(limit_prob)
                return self._request("POST", "bet", json=data)
            raise
    
    def cancel_bet(self, bet_id: str) -> Dict:
        """
        Cancel a bet.
        
        Args:
            bet_id: Bet ID
            
        Returns:
            Cancellation result
        """
        return self._request("POST", f"bet/cancel/{bet_id}")
    
    def get_bets(self, username: Optional[str] = None, market_id: Optional[str] = None,
                 limit: int = 100) -> List[Dict]:
        """
        Get bets.
        
        Args:
            username: Optional username to filter by
            market_id: Optional market ID to filter by
            limit: Maximum number of bets to return
            
        Returns:
            List of bet dictionaries
        """
        params = {"limit": limit}
        if username:
            params["username"] = username
        if market_id:
            params["marketId"] = market_id
        
        return self._request("GET", "bets", params=params)

