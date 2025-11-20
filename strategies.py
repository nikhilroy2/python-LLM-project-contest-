"""
Trading strategies for the judgmental prediction bot.
"""
from typing import Dict, Optional, Tuple
import logging
import math

logger = logging.getLogger(__name__)


class TradingStrategy:
    """Base class for trading strategies."""
    
    def should_trade(self, market: Dict, analysis: Dict, llm_prediction: Optional[Tuple[float, float, str]] = None) -> Tuple[bool, float, str]:
        """
        Determine if we should trade this market.
        
        Args:
            market: Market dictionary
            analysis: Market analysis scores
            llm_prediction: Optional LLM prediction (prob, confidence, reasoning)
            
        Returns:
            Tuple of (should_trade, bet_amount, side)
            - should_trade: Boolean
            - bet_amount: Amount to bet (if should_trade)
            - side: 'YES' or 'NO'
        """
        raise NotImplementedError


class LLMStrategy(TradingStrategy):
    """Strategy based on LLM predictions."""
    
    def __init__(self, min_confidence: float = 0.6, max_bet: float = 50.0):
        """
        Initialize LLM strategy.
        
        Args:
            min_confidence: Minimum LLM confidence to trade
            max_bet: Maximum bet amount
        """
        self.min_confidence = min_confidence
        self.max_bet = max_bet
    
    def should_trade(self, market: Dict, analysis: Dict, 
                    llm_prediction: Optional[Tuple[float, float, str]] = None) -> Tuple[bool, float, str]:
        """Trade based on LLM prediction if confidence is high enough."""
        if not llm_prediction:
            return False, 0.0, "NO"
        
        llm_prob, confidence, reasoning = llm_prediction
        current_prob = market.get("probability", 0.5)
        
        if confidence < self.min_confidence:
            logger.debug(f"LLM confidence {confidence:.2f} below threshold {self.min_confidence}")
            return False, 0.0, "NO"
        
        # Calculate expected value
        edge = abs(llm_prob - current_prob)
        
        # Only trade if there's a meaningful edge
        if edge < 0.05:  # Less than 5% edge
            logger.debug(f"Edge too small: {edge:.2%}")
            return False, 0.0, "NO"
        
        # Determine side
        if llm_prob > current_prob:
            side = "YES"
        else:
            side = "NO"
        
        # Calculate bet size based on edge and confidence
        bet_amount = min(self.max_bet, edge * confidence * 100)
        
        logger.info(f"LLM Strategy: {side} bet of {bet_amount:.2f} (edge: {edge:.2%}, confidence: {confidence:.2%})")
        return True, bet_amount, side


class MarketMakerStrategy(TradingStrategy):
    """Strategy that identifies mispriced markets."""
    
    def __init__(self, max_bet: float = 50.0, min_edge: float = 0.1):
        """
        Initialize market maker strategy.
        
        Args:
            max_bet: Maximum bet amount
            min_edge: Minimum edge required (as probability difference)
        """
        self.max_bet = max_bet
        self.min_edge = min_edge
    
    def should_trade(self, market: Dict, analysis: Dict, 
                    llm_prediction: Optional[Tuple[float, float, str]] = None) -> Tuple[bool, float, str]:
        """Trade when market is mispriced relative to fundamentals."""
        current_prob = market.get("probability", 0.5)
        
        # Use LLM prediction if available, otherwise use market analysis
        if llm_prediction:
            fair_prob, confidence, _ = llm_prediction
        else:
            # Use market analysis scores as proxy for fair value
            # Higher overall score suggests market should be higher probability
            overall_score = analysis.get("overall_score", 0.5)
            fair_prob = overall_score
            confidence = 0.5
        
        edge = abs(fair_prob - current_prob)
        
        if edge < self.min_edge:
            return False, 0.0, "NO"
        
        # Determine side
        if fair_prob > current_prob:
            side = "YES"
        else:
            side = "NO"
        
        # Bet size proportional to edge
        bet_amount = min(self.max_bet, edge * 200)
        
        logger.info(f"Market Maker Strategy: {side} bet of {bet_amount:.2f} (edge: {edge:.2%})")
        return True, bet_amount, side


class KellyStrategy(TradingStrategy):
    """Kelly Criterion-based position sizing."""
    
    def __init__(self, max_bet: float = 50.0, kelly_fraction: float = 0.25):
        """
        Initialize Kelly strategy.
        
        Args:
            max_bet: Maximum bet amount
            kelly_fraction: Fraction of Kelly bet to use (for safety)
        """
        self.max_bet = max_bet
        self.kelly_fraction = kelly_fraction
    
    def should_trade(self, market: Dict, analysis: Dict, 
                    llm_prediction: Optional[Tuple[float, float, str]] = None) -> Tuple[bool, float, str]:
        """Use Kelly Criterion to size bets."""
        if not llm_prediction:
            return False, 0.0, "NO"
        
        llm_prob, confidence, _ = llm_prediction
        current_prob = market.get("probability", 0.5)
        
        # Calculate Kelly bet
        if llm_prob > current_prob:
            # Bet YES
            p = llm_prob  # Our probability estimate
            q = current_prob  # Market probability (odds)
            edge = p - q
            if edge <= 0:
                return False, 0.0, "NO"
            
            # Kelly fraction: f = (p - q) / (1 - q)
            kelly = edge / (1 - q) if q < 1 else 0
            side = "YES"
        else:
            # Bet NO
            p = 1 - llm_prob  # Our probability estimate for NO
            q = 1 - current_prob  # Market probability for NO
            edge = p - q
            if edge <= 0:
                return False, 0.0, "NO"
            
            # Kelly fraction: f = (p - q) / (1 - q)
            kelly = edge / (1 - q) if q < 1 else 0
            side = "NO"
        
        # Apply fractional Kelly and convert to bet amount
        bet_amount = min(self.max_bet, kelly * self.kelly_fraction * 100)
        
        if bet_amount < 1.0:  # Minimum bet threshold
            return False, 0.0, "NO"
        
        logger.info(f"Kelly Strategy: {side} bet of {bet_amount:.2f} (Kelly: {kelly:.2%})")
        return True, bet_amount, side


class CompositeStrategy(TradingStrategy):
    """Combines multiple strategies."""
    
    def __init__(self, strategies: list, weights: Optional[list] = None):
        """
        Initialize composite strategy.
        
        Args:
            strategies: List of strategy instances
            weights: Optional weights for each strategy (default: equal weights)
        """
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)
    
    def should_trade(self, market: Dict, analysis: Dict, 
                    llm_prediction: Optional[Tuple[float, float, str]] = None) -> Tuple[bool, float, str]:
        """Combine recommendations from multiple strategies."""
        recommendations = []
        
        for strategy, weight in zip(self.strategies, self.weights):
            should_trade, bet_amount, side = strategy.should_trade(market, analysis, llm_prediction)
            if should_trade:
                recommendations.append((bet_amount * weight, side))
        
        if not recommendations:
            return False, 0.0, "NO"
        
        # Aggregate recommendations
        yes_bets = sum(amt for amt, side in recommendations if side == "YES")
        no_bets = sum(amt for amt, side in recommendations if side == "NO")
        
        if yes_bets > no_bets:
            return True, yes_bets, "YES"
        elif no_bets > yes_bets:
            return True, no_bets, "NO"
        else:
            return False, 0.0, "NO"

