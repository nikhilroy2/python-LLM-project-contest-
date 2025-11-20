# Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Get Manifold API Key**
   - Go to https://manifold.markets
   - Create an account or log in
   - Go to Settings > API
   - Generate an API key
   - Copy it to your `.env` file

4. **Set Bot Username**
   - Use a unique username for your bot (e.g., "JudgmentalBot2024")
   - This allows tracking performance separately

5. **Configure LLM (Required for intelligent analysis)**
   - For Google Gemini (default): Get API key from https://makersuite.google.com/app/apikey
   - For OpenAI (optional): Get API key from https://platform.openai.com
   - For Anthropic (optional): Get API key from https://console.anthropic.com
   - Add to `.env` file (GEMINI_API_KEY is required by default)

6. **Run the Bot**
   ```bash
   python main.py
   ```

## Configuration Options

### Required
- `MANIFOLD_API_KEY`: Your Manifold Markets API key
- `MANIFOLD_USERNAME`: Your bot's username on Manifold

### Required for LLM Analysis
- `GEMINI_API_KEY`: Google Gemini API key (default LLM provider)
- `LLM_PROVIDER`: Set to 'gemini' (default), 'openai', or 'anthropic'

### Optional
- `OPENAI_API_KEY`: For OpenAI LLM (if using OpenAI instead of Gemini)
- `ANTHROPIC_API_KEY`: For Anthropic LLM (if using Anthropic instead of Gemini)
- `TARGET_CREATOR`: Defaults to "MikhailTal" (the target creator)

### Risk Management
- `MAX_POSITION_SIZE`: Maximum bet per market (default: 100)
- `MAX_PORTFOLIO_RISK`: Maximum portfolio risk ratio (default: 0.3 = 30%)
- `MAX_MARKETS_OPEN`: Maximum concurrent positions (default: 10)

### Trading Parameters
- `MIN_CONFIDENCE`: Minimum LLM confidence to trade (default: 0.6)
- `MAX_BET_AMOUNT`: Maximum bet amount (default: 50)
- `CHECK_INTERVAL`: Seconds between market checks (default: 300 = 5 minutes)

## Testing

Test the bot with a single run:
```bash
python example.py
```

Or run the full bot:
```bash
python main.py
```

## Troubleshooting

### "Manifold client not initialized"
- Check that your API key is correct in `.env`
- Verify the API key has proper permissions

### "No markets found"
- Check that `TARGET_CREATOR` is set correctly
- Verify the creator has active markets

### "LLM analysis not available"
- This is normal if you haven't configured LLM API keys
- The bot will still work using non-LLM strategies

### Import errors
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

## Monitoring

The bot logs to:
- Console (stdout)
- `bot.log` file
- Performance data in `performance.json`

Check these files to monitor bot activity and performance.

