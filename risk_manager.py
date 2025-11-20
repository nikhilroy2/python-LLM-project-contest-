"""
Risk management module.
Manages position sizing, portfolio risk, and position limits.
"""
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk and position sizing."""
    
    def __init__(self, max_position_size: float, max_portfolio_risk: float, 
                 max_markets_open: int):
        """
        Initialize risk manager.
        
        Args:
            max_position_size: Maximum position size per market
            max_portfolio_risk: Maximum portfolio risk (0-1)
            max_markets_open: Maximum number of open positions
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.max_markets_open = max_markets_open
        self.open_positions: Dict[str, Dict] = {}
    
    def can_trade(self, market_id: str, proposed_bet: float, 
                  current_balance: float) -> Tuple[bool, Optional[str]]:
        """
        Check if a trade is allowed given risk constraints.
        
        Args:
            market_id: Market ID
            proposed_bet: Proposed bet amount
            current_balance: Current account balance
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Check if we already have a position in this market
        if market_id in self.open_positions:
            logger.debug(f"Already have position in market {market_id}")
            return False, "Already have position"
        
        # Check position size limit
        if proposed_bet > self.max_position_size:
            logger.debug(f"Bet {proposed_bet} exceeds max position size {self.max_position_size}")
            return False, f"Exceeds max position size {self.max_position_size}"
        
        # Check portfolio risk
        total_at_risk = sum(pos.get("amount", 0) for pos in self.open_positions.values())
        total_at_risk += proposed_bet
        
        if current_balance > 0:
            risk_ratio = total_at_risk / current_balance
            if risk_ratio > self.max_portfolio_risk:
                logger.debug(f"Risk ratio {risk_ratio:.2%} exceeds max {self.max_portfolio_risk:.2%}")
                return False, f"Exceeds portfolio risk limit {self.max_portfolio_risk:.2%}"
        
        # Check maximum number of open positions
        if len(self.open_positions) >= self.max_markets_open:
            logger.debug(f"Already at max open positions {self.max_markets_open}")
            return False, f"At max open positions {self.max_markets_open}"
        
        return True, None
    
    def adjust_bet_size(self, proposed_bet: float, current_balance: float, 
                       market_id: str) -> float:
        """
        Adjust bet size to comply with risk limits.
        
        Args:
            proposed_bet: Proposed bet amount
            current_balance: Current account balance
            market_id: Market ID
            
        Returns:
            Adjusted bet amount
        """
        # Start with proposed bet
        adjusted = proposed_bet
        
        # Cap at max position size
        adjusted = min(adjusted, self.max_position_size)
        
        # Cap at portfolio risk limit
        total_at_risk = sum(pos.get("amount", 0) for pos in self.open_positions.values())
        if current_balance > 0:
            max_total_risk = current_balance * self.max_portfolio_risk
            max_bet = max_total_risk - total_at_risk
            adjusted = min(adjusted, max_bet)
        
        # Ensure positive
        adjusted = max(0.0, adjusted)
        
        if adjusted != proposed_bet:
            logger.info(f"Adjusted bet from {proposed_bet:.2f} to {adjusted:.2f}")
        
        return adjusted
    
    def record_position(self, market_id: str, amount: float, side: str, 
                       market_prob: float):
        """Record a new position."""
        self.open_positions[market_id] = {
            "amount": amount,
            "side": side,
            "market_prob": market_prob,
            "timestamp": None,  # Will be set by bot
        }
        logger.info(f"Recorded position: {market_id} {side} {amount:.2f}")
    
    def remove_position(self, market_id: str):
        """Remove a closed position."""
        if market_id in self.open_positions:
            del self.open_positions[market_id]
            logger.info(f"Removed position: {market_id}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get summary of current portfolio."""
        total_at_risk = sum(pos.get("amount", 0) for pos in self.open_positions.values())
        return {
            "num_positions": len(self.open_positions),
            "total_at_risk": total_at_risk,
            "positions": self.open_positions.copy(),
        }

