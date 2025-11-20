"""
Configuration management for the judgmental prediction bot.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Config(BaseModel):
    """Bot configuration."""
    
    # Manifold API
    manifold_api_key: str = Field(..., description="Manifold Markets API key")
    manifold_username: str = Field(..., description="Bot username on Manifold")
    
    # Target market creator
    target_creator: str = Field(default="MikhailTal", description="Only trade in markets by this creator")
    
    # LLM Configuration
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key for LLM analysis")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for LLM analysis (optional)")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key for LLM analysis (optional)")
    llm_provider: str = Field(default="gemini", description="LLM provider: 'gemini', 'openai', or 'anthropic'")
    
    # Risk Management
    max_position_size: float = Field(default=100.0, description="Maximum position size per market")
    max_portfolio_risk: float = Field(default=0.3, description="Maximum portfolio risk (0-1)")
    min_market_liquidity: float = Field(default=50.0, description="Minimum market liquidity to trade")
    max_markets_open: int = Field(default=10, description="Maximum number of open positions")
    
    # Trading Parameters
    check_interval: int = Field(default=300, description="Seconds between market checks")
    min_confidence: float = Field(default=0.6, description="Minimum confidence to place a bet (0-1)")
    max_bet_amount: float = Field(default=50.0, description="Maximum bet amount")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="bot.log", description="Log file path")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            manifold_api_key=os.getenv("MANIFOLD_API_KEY", ""),
            manifold_username=os.getenv("MANIFOLD_USERNAME", ""),
            target_creator=os.getenv("TARGET_CREATOR", "MikhailTal"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            llm_provider=os.getenv("LLM_PROVIDER", "gemini"),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "100")),
            max_portfolio_risk=float(os.getenv("MAX_PORTFOLIO_RISK", "0.3")),
            min_market_liquidity=float(os.getenv("MIN_MARKET_LIQUIDITY", "50")),
            max_markets_open=int(os.getenv("MAX_MARKETS_OPEN", "10")),
            check_interval=int(os.getenv("CHECK_INTERVAL", "300")),
            min_confidence=float(os.getenv("MIN_CONFIDENCE", "0.6")),
            max_bet_amount=float(os.getenv("MAX_BET_AMOUNT", "50")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "bot.log"),
        )
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.manifold_api_key:
            raise ValueError("MANIFOLD_API_KEY is required")
        if not self.manifold_username:
            raise ValueError("MANIFOLD_USERNAME is required")
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when using Gemini")
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")

