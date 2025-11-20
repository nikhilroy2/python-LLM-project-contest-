"""
Manifold API client wrapper.
Handles both sync and async operations with the Manifold API.
"""
import logging
import requests
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)


class ManifoldClient:
    """Wrapper for Manifold API interactions."""
    
    BASE_URL = "https://api.manifold.markets/v0"
    
    def __init__(self, api_key: str):
        """
        Initialize Manifold client.
        
        Args:
            api_key: Manifold API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make a request to the Manifold API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response JSON
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_markets(self, limit: int = 100, creator_id: Optional[str] = None) -> List[Dict]:
        """
        Get markets from Manifold.
        
        Args:
            limit: Maximum number of markets to return
            creator_id: Optional creator ID to filter by
            
        Returns:
            List of market dictionaries
        """
        params = {"limit": limit}
        if creator_id:
            params["creatorId"] = creator_id
        
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
        
        Args:
            market_id: Market ID
            amount: Bet amount
            outcome: 'YES' or 'NO'
            limit_prob: Optional limit probability
            
        Returns:
            Bet result dictionary
        """
        # Ensure amount is a number (not string)
        amount = float(amount)
        
        data = {
            "contractId": market_id,  # Try contractId instead of marketId
            "amount": amount,
            "outcome": outcome.upper()
        }
        
        if limit_prob is not None:
            data["limitProb"] = float(limit_prob)
        
        try:
            return self._request("POST", "bet", json=data)
        except Exception as e:
            # Try with marketId if contractId fails
            if "contractId" in str(e) or "400" in str(e):
                data = {
                    "marketId": market_id,
                    "amount": amount,
                    "outcome": outcome.upper()
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

