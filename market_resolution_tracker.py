"""
Market resolution tracking and P&L calculation.
Tracks when markets resolve and calculates actual profit/loss.
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MarketResolutionTracker:
    """Tracks market resolutions and calculates P&L."""
    
    def __init__(self):
        """Initialize resolution tracker."""
        self.resolved_markets: Dict[str, Dict] = {}
        self.pending_positions: Dict[str, Dict] = {}
    
    def track_position(self, market_id: str, side: str, amount: float, 
                      entry_prob: float, market_question: str):
        """Track a position waiting for resolution."""
        self.pending_positions[market_id] = {
            "side": side,
            "amount": amount,
            "entry_prob": entry_prob,
            "market_question": market_question,
            "entry_time": datetime.now().isoformat(),
        }
        logger.debug(f"Tracking position: {market_id} {side} {amount:.2f}")
    
    def check_resolution(self, market: Dict) -> Optional[Dict]:
        """
        Check if a market has resolved and calculate P&L.
        
        Args:
            market: Market dictionary from API
            
        Returns:
            Resolution data with P&L if resolved, None otherwise
        """
        market_id = market.get("id")
        is_resolved = market.get("isResolved", False)
        resolution = market.get("resolution")
        
        if not is_resolved or not resolution:
            return None
        
        if market_id not in self.pending_positions:
            return None
        
        position = self.pending_positions[market_id]
        side = position["side"]
        amount = position["amount"]
        entry_prob = position["entry_prob"]
        
        # Determine if we won
        # Resolution can be "YES", "NO", "MKT", "CANCEL", or a number
        won = False
        if resolution == "YES" and side == "YES":
            won = True
        elif resolution == "NO" and side == "NO":
            won = True
        elif isinstance(resolution, (int, float)):
            # Numeric resolution - check if our side won
            if side == "YES" and resolution > 0.5:
                won = True
            elif side == "NO" and resolution <= 0.5:
                won = True
        
        # Calculate P&L
        # If we won: profit = amount * (1 / entry_prob - 1)
        # If we lost: loss = -amount
        if won:
            # Calculate profit based on odds
            profit = amount * (1.0 / entry_prob - 1.0) if entry_prob > 0 else 0
            pnl = profit
        else:
            # Lost the bet
            pnl = -amount
        
        resolution_data = {
            "market_id": market_id,
            "market_question": position["market_question"],
            "side": side,
            "amount": amount,
            "entry_prob": entry_prob,
            "resolution": resolution,
            "won": won,
            "pnl": pnl,
            "resolved_at": datetime.now().isoformat(),
        }
        
        # Move from pending to resolved
        self.resolved_markets[market_id] = resolution_data
        del self.pending_positions[market_id]
        
        logger.info(f"Market resolved: {market_id} - {'WON' if won else 'LOST'} - P&L: {pnl:.2f}")
        
        return resolution_data
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics from resolved markets."""
        if not self.resolved_markets:
            return {
                "total_resolved": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "total_invested": 0.0,
                "roi": 0.0,
            }
        
        resolved = list(self.resolved_markets.values())
        wins = sum(1 for r in resolved if r["won"])
        losses = len(resolved) - wins
        total_pnl = sum(r["pnl"] for r in resolved)
        total_invested = sum(r["amount"] for r in resolved)
        
        win_rate = (wins / len(resolved) * 100) if resolved else 0.0
        roi = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
        
        return {
            "total_resolved": len(resolved),
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_invested": total_invested,
            "roi": roi,
        }
    
    def get_pending_count(self) -> int:
        """Get number of pending positions."""
        return len(self.pending_positions)

