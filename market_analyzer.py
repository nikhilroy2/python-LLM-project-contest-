"""
Market analysis and filtering module.
Filters markets created by target creator and evaluates trading opportunities.
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analyzes and filters Manifold markets."""
    
    def __init__(self, target_creator: str, min_liquidity: float = 50.0):
        """
        Initialize market analyzer.
        
        Args:
            target_creator: Username of market creator to filter for
            min_liquidity: Minimum market liquidity to consider
        """
        self.target_creator = target_creator
        self.min_liquidity = min_liquidity
    
    def filter_target_markets(self, markets: List[Dict]) -> List[Dict]:
        """
        Filter markets created by target creator.
        
        Args:
            markets: List of market dictionaries from Manifold API
            
        Returns:
            Filtered list of markets
        """
        filtered = [
            market for market in markets
            if self._is_target_market(market)
        ]
        logger.info(f"Filtered {len(filtered)} markets from {len(markets)} total markets")
        return filtered
    
    def _is_target_market(self, market: Dict) -> bool:
        """Check if market is created by target creator."""
        creator = market.get("creatorUsername") or market.get("creatorId")
        return creator == self.target_creator
    
    def evaluate_market(self, market: Dict) -> Dict[str, float]:
        """
        Evaluate a market for trading opportunities.
        
        Args:
            market: Market dictionary from Manifold API
            
        Returns:
            Dictionary with evaluation scores and metrics
        """
        scores = {
            "liquidity_score": self._calculate_liquidity_score(market),
            "time_score": self._calculate_time_score(market),
            "volatility_score": self._calculate_volatility_score(market),
            "volume_score": self._calculate_volume_score(market),
        }
        
        # Overall score (weighted average)
        weights = {
            "liquidity_score": 0.3,
            "time_score": 0.25,
            "volatility_score": 0.25,
            "volume_score": 0.2,
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores)
        scores["overall_score"] = overall_score
        
        return scores
    
    def _calculate_liquidity_score(self, market: Dict) -> float:
        """Calculate liquidity score (0-1)."""
        total_liquidity = market.get("totalLiquidity", 0)
        if total_liquidity < self.min_liquidity:
            return 0.0
        
        # Normalize liquidity score (higher is better, capped at 1.0)
        # Consider markets with 200+ liquidity as fully scored
        return min(1.0, total_liquidity / 200.0)
    
    def _calculate_time_score(self, market: Dict) -> float:
        """Calculate time-to-resolution score (0-1)."""
        close_time = market.get("closeTime")
        if not close_time:
            return 0.5  # No close time, neutral score
        
        try:
            close_dt = datetime.fromtimestamp(close_time / 1000)
            now = datetime.now()
            time_remaining = (close_dt - now).total_seconds()
            
            # Prefer markets closing in 1-7 days
            if time_remaining < 0:
                return 0.0  # Already closed
            elif time_remaining < 86400:  # Less than 1 day
                return 0.3  # Too soon
            elif time_remaining < 604800:  # 1-7 days
                return 1.0  # Optimal
            elif time_remaining < 2592000:  # 7-30 days
                return 0.7  # Good
            else:
                return 0.4  # Too far out
        except Exception as e:
            logger.warning(f"Error calculating time score: {e}")
            return 0.5
    
    def _calculate_volatility_score(self, market: Dict) -> float:
        """Calculate volatility/activity score (0-1)."""
        # Higher volatility suggests more trading opportunities
        # Use recent volume or price movement as proxy
        volume_24h = market.get("volume24Hours", 0)
        
        # Normalize based on liquidity
        liquidity = market.get("totalLiquidity", 1)
        turnover_rate = volume_24h / liquidity if liquidity > 0 else 0
        
        # Higher turnover is better (more active market)
        return min(1.0, turnover_rate * 2)  # Cap at 1.0
    
    def _calculate_volume_score(self, market: Dict) -> float:
        """Calculate volume score (0-1)."""
        volume_24h = market.get("volume24Hours", 0)
        
        # Normalize volume (consider 100+ volume as fully scored)
        return min(1.0, volume_24h / 100.0)
    
    def get_market_metadata(self, market: Dict) -> Dict:
        """Extract useful metadata from market."""
        return {
            "id": market.get("id"),
            "question": market.get("question"),
            "creator": market.get("creatorUsername"),
            "probability": market.get("probability"),
            "liquidity": market.get("totalLiquidity", 0),
            "volume_24h": market.get("volume24Hours", 0),
            "is_resolved": market.get("isResolved", False),
            "close_time": market.get("closeTime"),
            "url": market.get("url"),
        }

