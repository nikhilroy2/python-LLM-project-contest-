# Judgmental Prediction Bot for Manifold Markets

An intelligent Python bot that participates in Manifold Markets, specifically targeting markets created by user "MikhailTal". This bot improves upon the [manifoldbot](https://github.com/microprediction/manifoldbot) package with advanced features including:

- **Intelligent Market Analysis**: Uses LLM-powered analysis to evaluate market opportunities
- **Risk Management**: Sophisticated position sizing and risk controls
- **Performance Tracking**: Comprehensive logging and analytics
- **Market Filtering**: Automatically filters and trades only in MikhailTal markets
- **Adaptive Strategies**: Multiple trading strategies that adapt to market conditions

## Features

### 🧠 Intelligent Decision Making
- LLM-powered market analysis using Google Gemini (with optional OpenAI/Anthropic support)
- Multi-factor market evaluation (liquidity, time to resolution, market maker activity)
- Sentiment analysis and pattern recognition

### 🎯 Targeted Trading
- Automatically filters markets created by "MikhailTal"
- Real-time market monitoring and opportunity detection
- Smart entry and exit timing

### 💰 Risk Management
- Kelly Criterion-based position sizing
- Maximum position limits per market
- Portfolio-level risk controls
- Stop-loss mechanisms

### 📊 Performance Analytics
- Real-time P&L tracking
- Trade history and analysis
- Performance metrics and reporting
- Rich console output with progress tracking

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd judgmental_prediction_script_python
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your environment:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Create a `.env` file with the following variables:

```env
MANIFOLD_API_KEY=your_manifold_api_key
MANIFOLD_USERNAME=your_bot_username
GEMINI_API_KEY=your_gemini_api_key  # Required for LLM analysis (default)
OPENAI_API_KEY=your_openai_api_key  # Optional, alternative to Gemini
ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional, alternative to Gemini
LLM_PROVIDER=gemini  # Options: 'gemini', 'openai', or 'anthropic'
TARGET_CREATOR=MikhailTal
MAX_POSITION_SIZE=100
MAX_PORTFOLIO_RISK=0.3
LOG_LEVEL=INFO
```

## Usage

### Basic Usage

Run the bot:
```bash
python main.py
```

### Advanced Usage

```python
from bot import JudgmentalPredictionBot
from config import Config

config = Config.from_env()
bot = JudgmentalPredictionBot(config)
bot.run()
```

## Architecture

```
judgmental_prediction_script_python/
├── bot.py                 # Main bot class
├── market_analyzer.py     # Market analysis and filtering
├── strategies.py          # Trading strategies
├── risk_manager.py        # Risk management
├── performance_tracker.py # Performance tracking
├── llm_analyzer.py        # LLM-powered analysis
├── config.py              # Configuration management
├── main.py                # Entry point
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Strategy Details

The bot employs multiple strategies:

1. **LLM Analysis Strategy**: Uses language models to analyze market questions and make predictions
2. **Market Maker Strategy**: Identifies mispriced markets and arbitrage opportunities
3. **Trend Following**: Tracks market momentum and follows trends
4. **Value Investing**: Identifies markets with favorable risk/reward ratios

## Improvements Over Manifoldbot

This bot extends and improves upon the base manifoldbot package in several key ways:

### 1. Enhanced Market Filtering (`market_analyzer.py`)
- **Multi-factor scoring**: Evaluates markets on liquidity, time-to-resolution, volatility, and volume
- **Creator filtering**: Efficiently filters markets by creator username
- **Market metadata extraction**: Provides structured market information for decision-making

### 2. LLM Integration (`llm_analyzer.py`)
- **Intelligent analysis**: Uses Google Gemini (with optional OpenAI/Anthropic support) to analyze market questions and make predictions
- **Confidence scoring**: LLMs provide confidence levels for their predictions
- **Reasoning extraction**: Captures LLM reasoning for audit trails

### 3. Advanced Risk Management (`risk_manager.py`)
- **Portfolio-level controls**: Tracks total portfolio risk across all positions
- **Position limits**: Enforces maximum positions per market and total open positions
- **Dynamic position sizing**: Adjusts bet sizes based on available capital and risk limits

### 4. Multiple Trading Strategies (`strategies.py`)
- **LLM Strategy**: Trades based on LLM predictions when confidence is high
- **Market Maker Strategy**: Identifies mispriced markets
- **Kelly Criterion**: Uses optimal position sizing based on edge
- **Composite Strategy**: Combines multiple strategies for robust decision-making

### 5. Performance Tracking (`performance_tracker.py`)
- **Trade history**: Records all trades with metadata
- **P&L tracking**: Monitors profit and loss over time
- **Statistics**: Calculates ROI, win rate, and other metrics
- **Persistent storage**: Saves performance data to JSON

### 6. Clean Architecture
- **Modular design**: Each component is independently testable
- **Type hints**: Full type annotations for better IDE support
- **Configuration management**: Centralized config with validation
- **Error handling**: Comprehensive error handling and logging

## Potential Pull Requests to Manifoldbot

The following components could be valuable additions to the upstream manifoldbot package:

1. **MarketAnalyzer class**: Reusable market filtering and scoring
2. **RiskManager class**: Portfolio risk management utilities
3. **PerformanceTracker class**: Standardized performance tracking
4. **Enhanced API client**: Better error handling and async support

## Contributing

This bot is designed to contribute improvements back to the manifoldbot package. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - feel free to use and modify as needed.

## Disclaimer

This bot is for educational and research purposes. Trading in prediction markets involves risk. Use at your own discretion. The bot uses play money on Manifold Markets, but strategies should be tested thoroughly before deployment.

