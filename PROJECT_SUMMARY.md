# Project Summary: Judgmental Prediction Bot

## Overview

This is a sophisticated Python bot for trading on Manifold Markets, specifically designed to participate in markets created by user "MikhailTal". The bot improves upon the base [manifoldbot](https://github.com/microprediction/manifoldbot) package with advanced features for intelligent trading.

## Key Features

### 1. Intelligent Market Analysis
- **LLM-Powered Predictions**: Uses Google Gemini (with optional OpenAI/Anthropic support) to analyze market questions
- **Multi-Factor Scoring**: Evaluates markets on liquidity, time-to-resolution, volatility, and volume
- **Confidence-Based Trading**: Only trades when LLM confidence exceeds threshold

### 2. Advanced Trading Strategies
- **LLM Strategy**: Trades based on LLM predictions with high confidence
- **Market Maker Strategy**: Identifies mispriced markets for arbitrage
- **Kelly Criterion**: Optimal position sizing based on edge
- **Composite Strategy**: Combines multiple strategies for robust decisions

### 3. Risk Management
- **Portfolio-Level Controls**: Tracks total risk across all positions
- **Position Limits**: Enforces maximum positions per market and portfolio
- **Dynamic Sizing**: Adjusts bet sizes based on available capital

### 4. Performance Tracking
- **Comprehensive Logging**: Records all trades with metadata
- **P&L Tracking**: Monitors profit and loss over time
- **Statistics**: Calculates ROI, win rate, and other metrics

## Architecture

```
judgmental_prediction_script_python/
├── bot.py                 # Main bot orchestrator
├── config.py              # Configuration management
├── market_analyzer.py     # Market filtering and evaluation
├── llm_analyzer.py        # LLM-powered analysis
├── strategies.py          # Trading strategies
├── risk_manager.py        # Risk management
├── performance_tracker.py # Performance tracking
├── manifold_client.py    # Manifold API wrapper
├── main.py                # Entry point
├── example.py             # Example usage
├── requirements.txt       # Dependencies
├── README.md              # Main documentation
├── SETUP.md               # Setup guide
├── CONTRIBUTING.md        # Contribution guidelines
└── LICENSE                # MIT License
```

## Design Decisions

### 1. Modular Architecture
Each component is independently testable and can be improved separately. This makes it easy to:
- Test individual components
- Swap out strategies
- Contribute improvements back to manifoldbot

### 2. LLM Integration
The bot uses LLMs for intelligent market analysis, but gracefully degrades to rule-based strategies if LLM APIs are unavailable. This ensures the bot always works.

### 3. Risk-First Approach
All trading decisions go through risk management checks before execution. This prevents over-leveraging and protects capital.

### 4. Async/Await Pattern
Uses async/await for I/O operations, allowing the bot to handle multiple markets efficiently.

## Improvements Over Manifoldbot

1. **Market Filtering**: Sophisticated filtering and scoring system
2. **LLM Integration**: First-class LLM support for intelligent analysis
3. **Risk Management**: Portfolio-level risk controls
4. **Performance Tracking**: Comprehensive analytics
5. **Multiple Strategies**: Flexible strategy system
6. **Better Error Handling**: Comprehensive error handling and logging

## Potential Contributions to Manifoldbot

The following components could be valuable additions:

1. `MarketAnalyzer` class for market filtering
2. `RiskManager` class for portfolio risk management
3. `PerformanceTracker` class for standardized tracking
4. Enhanced API client with better error handling

## Usage

```python
from config import Config
from bot import JudgmentalPredictionBot

config = Config.from_env()
bot = JudgmentalPredictionBot(config)
await bot.run()
```

## Configuration

All configuration is done via environment variables (see `.env.example`):
- Manifold API credentials
- LLM API keys (optional)
- Risk parameters
- Trading parameters

## Testing

Run the example script to test:
```bash
python example.py
```

## Performance Metrics

The bot tracks:
- Total trades
- Total invested
- P&L
- ROI
- Win rate (when markets resolve)

## Future Enhancements

Potential improvements:
- Backtesting framework
- Machine learning models
- More sophisticated strategies
- Real-time market monitoring
- Web dashboard for monitoring

## License

MIT License - open source and free to use/modify.

