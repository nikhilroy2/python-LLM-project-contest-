"""
Main bot class that orchestrates market analysis, trading, and risk management.
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from config import Config
from market_analyzer import MarketAnalyzer
from llm_analyzer import LLMAnalyzer
from strategies import LLMStrategy, CompositeStrategy, KellyStrategy
from risk_manager import RiskManager
from performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class JudgmentalPredictionBot:
    """Main bot class for trading on Manifold Markets."""
    
    def __init__(self, config: Config):
        """
        Initialize the bot.
        
        Args:
            config: Bot configuration
        """
        self.config = config
        self.config.validate()
        
        # Initialize components
        self.market_analyzer = MarketAnalyzer(
            target_creator=config.target_creator,
            min_liquidity=config.min_market_liquidity
        )
        
        self.llm_analyzer = LLMAnalyzer(
            provider=config.llm_provider,
            gemini_key=config.gemini_api_key,
            openai_key=config.openai_api_key,
            anthropic_key=config.anthropic_api_key
        )
        
        # Initialize strategies
        llm_strategy = LLMStrategy(
            min_confidence=config.min_confidence,
            max_bet=config.max_bet_amount
        )
        kelly_strategy = KellyStrategy(max_bet=config.max_bet_amount)
        
        self.strategy = CompositeStrategy([llm_strategy, kelly_strategy])
        
        self.risk_manager = RiskManager(
            max_position_size=config.max_position_size,
            max_portfolio_risk=config.max_portfolio_risk,
            max_markets_open=config.max_markets_open
        )
        
        self.performance_tracker = PerformanceTracker()
        
        # Initialize Manifold API client
        self._init_manifold_client()
        
        self.running = False
    
    def _init_manifold_client(self):
        """Initialize Manifold API client."""
        try:
            # Try to use our custom client first
            from manifold_client import ManifoldClient
            self.manifold = ManifoldClient(api_key=self.config.manifold_api_key)
            logger.info("Manifold client initialized (custom)")
        except ImportError:
            try:
                # Fallback to manifoldbot if available
                from manifoldbot import ManifoldClient as MBClient
                self.manifold = MBClient(api_key=self.config.manifold_api_key)
                logger.info("Manifold client initialized (manifoldbot)")
            except ImportError:
                logger.error("Neither custom client nor manifoldbot available. Using custom client.")
                from manifold_client import ManifoldClient
                self.manifold = ManifoldClient(api_key=self.config.manifold_api_key)
        except Exception as e:
            logger.error(f"Error initializing Manifold client: {e}")
            raise
    
    async def get_markets(self) -> List[Dict]:
        """Fetch markets from Manifold."""
        try:
            # Use asyncio to run sync API calls in executor
            loop = asyncio.get_event_loop()
            # Fetch all markets and filter by creator username
            markets = await loop.run_in_executor(
                None,
                lambda: self.manifold.get_markets(limit=500)  # Get more markets to filter
            )
            # Filter markets by creator username
            filtered_markets = [
                market for market in markets
                if market.get("creatorUsername") == self.config.target_creator
            ]
            return filtered_markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    async def get_user_balance(self) -> float:
        """Get current user balance."""
        try:
            loop = asyncio.get_event_loop()
            user = await loop.run_in_executor(
                None,
                lambda: self.manifold.get_user(self.config.manifold_username)
            )
            if user:
                return user.get("balance", 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0
    
    async def place_bet(self, market_id: str, amount: float, side: str) -> bool:
        """
        Place a bet on a market.
        
        Args:
            market_id: Market ID
            amount: Bet amount
            side: 'YES' or 'NO'
            
        Returns:
            True if bet was placed successfully
        """
        try:
            outcome = "YES" if side == "YES" else "NO"
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.manifold.place_bet(
                    market_id=market_id,
                    amount=amount,
                    outcome=outcome
                )
            )
            logger.info(f"Placed {side} bet of {amount:.2f} on market {market_id}")
            return True
        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            return False
    
    async def process_markets(self):
        """Process markets and make trading decisions."""
        logger.info("Fetching markets...")
        markets = await self.get_markets()
        
        if not markets:
            logger.warning("No markets fetched")
            return
        
        # Filter for target creator
        target_markets = self.market_analyzer.filter_target_markets(markets)
        
        if not target_markets:
            logger.info(f"No markets found for creator: {self.config.target_creator}")
            return
        
        logger.info(f"Found {len(target_markets)} markets from {self.config.target_creator}")
        
        # Get current balance
        balance = await self.get_user_balance()
        self.performance_tracker.update_balance(balance)
        
        # Process each market
        for market in target_markets:
            if not self.running:
                break
            
            await self.process_market(market, balance)
    
    async def process_market(self, market: Dict, balance: float):
        """
        Process a single market and decide whether to trade.
        
        Args:
            market: Market dictionary
            balance: Current account balance
        """
        market_id = market.get("id")
        market_question = market.get("question", "Unknown")
        
        # Skip if already resolved
        if market.get("isResolved", False):
            return
        
        # Skip if we already have a position
        if market_id in self.risk_manager.open_positions:
            return
        
        logger.info(f"Analyzing market: {market_question[:60]}...")
        
        # Analyze market
        analysis = self.market_analyzer.evaluate_market(market)
        
        # Get LLM prediction
        llm_prediction = None
        if self.llm_analyzer._client:
            llm_prediction = self.llm_analyzer.analyze_market(market)
            logger.info(f"LLM prediction: prob={llm_prediction[0]:.2%}, confidence={llm_prediction[1]:.2%}")
        
        # Check if we should trade
        should_trade, bet_amount, side = self.strategy.should_trade(
            market, analysis, llm_prediction
        )
        
        if not should_trade:
            logger.debug(f"Skipping market {market_id}: strategy says no trade")
            return
        
        # Check risk constraints
        can_trade, reason = self.risk_manager.can_trade(market_id, bet_amount, balance)
        
        if not can_trade:
            logger.info(f"Cannot trade market {market_id}: {reason}")
            return
        
        # Adjust bet size if needed
        bet_amount = self.risk_manager.adjust_bet_size(bet_amount, balance, market_id)
        
        if bet_amount < 1.0:  # Minimum bet threshold
            logger.debug(f"Bet amount {bet_amount:.2f} too small")
            return
        
        # Place bet
        success = await self.place_bet(market_id, bet_amount, side)
        
        if success:
            # Record position and trade
            current_prob = market.get("probability", 0.5)
            self.risk_manager.record_position(market_id, bet_amount, side, current_prob)
            
            reasoning = llm_prediction[2] if llm_prediction else "Strategy-based"
            self.performance_tracker.record_trade(
                market_id=market_id,
                market_question=market_question,
                side=side,
                amount=bet_amount,
                probability=current_prob,
                reasoning=reasoning
            )
    
    async def run_once(self):
        """Run one iteration of market processing."""
        try:
            await self.process_markets()
        except Exception as e:
            logger.error(f"Error in run_once: {e}", exc_info=True)
    
    async def run(self):
        """Run the bot continuously."""
        logger.info("Starting judgmental prediction bot...")
        logger.info(f"Target creator: {self.config.target_creator}")
        logger.info(f"Bot username: {self.config.manifold_username}")
        
        self.running = True
        
        try:
            while self.running:
                await self.run_once()
                
                # Print performance summary
                self.performance_tracker.print_summary()
                
                # Wait before next iteration
                logger.info(f"Waiting {self.config.check_interval} seconds before next check...")
                await asyncio.sleep(self.config.check_interval)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("Bot shutdown complete")
    
    def stop(self):
        """Stop the bot."""
        self.running = False

