"""
Performance tracking and analytics module.
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks bot performance and generates reports."""
    
    def __init__(self, log_file: str = "performance.json"):
        """
        Initialize performance tracker.
        
        Args:
            log_file: File to store performance data
        """
        self.log_file = log_file
        self.trades: List[Dict] = []
        self.starting_balance: Optional[float] = None
        self.current_balance: Optional[float] = None
        self._load_history()
    
    def _load_history(self):
        """Load performance history from file."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.trades = data.get("trades", [])
                    self.starting_balance = data.get("starting_balance")
                    self.current_balance = data.get("current_balance")
            except Exception as e:
                logger.warning(f"Error loading performance history: {e}")
                self.trades = []
    
    def _save_history(self):
        """Save performance history to file."""
        try:
            data = {
                "trades": self.trades,
                "starting_balance": self.starting_balance,
                "current_balance": self.current_balance,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving performance history: {e}")
    
    def record_trade(self, market_id: str, market_question: str, side: str, 
                    amount: float, probability: float, reasoning: str = ""):
        """Record a trade."""
        trade = {
            "timestamp": datetime.now().isoformat(),
            "market_id": market_id,
            "market_question": market_question,
            "side": side,
            "amount": amount,
            "probability": probability,
            "reasoning": reasoning,
        }
        self.trades.append(trade)
        self._save_history()
        logger.info(f"Recorded trade: {market_question[:50]}... {side} {amount:.2f}")
    
    def update_balance(self, balance: float):
        """Update current balance."""
        if self.starting_balance is None:
            self.starting_balance = balance
        self.current_balance = balance
        self._save_history()
    
    def get_statistics(self) -> Dict:
        """Get performance statistics."""
        total_trades = len(self.trades) if self.trades else 0
        total_invested = sum(trade["amount"] for trade in self.trades) if self.trades else 0.0
        
        # Calculate P&L (this would need market resolution data in real implementation)
        # For now, we'll track open positions
        total_pnl = 0.0
        if self.starting_balance is not None and self.current_balance is not None:
            total_pnl = self.current_balance - self.starting_balance
        
        roi = (total_pnl / self.starting_balance * 100) if self.starting_balance else 0.0
        
        return {
            "total_trades": total_trades,
            "total_invested": total_invested,
            "win_rate": 0.0,
            "total_pnl": total_pnl,
            "roi": roi,
            "current_balance": self.current_balance,
            "starting_balance": self.starting_balance,
        }
    
    def get_recent_trades(self, n: int = 10) -> List[Dict]:
        """Get most recent trades."""
        return self.trades[-n:] if self.trades else []
    
    def print_summary(self):
        """Print performance summary."""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Total Invested: {stats['total_invested']:.2f}")
        starting_bal = stats.get('starting_balance')
        current_bal = stats.get('current_balance')
        print(f"Starting Balance: {starting_bal:.2f}" if starting_bal is not None else "Starting Balance: N/A")
        print(f"Current Balance: {current_bal:.2f}" if current_bal is not None else "Current Balance: N/A")
        print(f"Total P&L: {stats['total_pnl']:.2f}")
        print(f"ROI: {stats['roi']:.2f}%")
        print("="*50 + "\n")

