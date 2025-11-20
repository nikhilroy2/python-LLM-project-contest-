"""
Example usage of the judgmental prediction bot.
"""
import asyncio
import logging
from config import Config
from bot import JudgmentalPredictionBot

logging.basicConfig(level=logging.INFO)


async def example_run_once():
    """Example of running the bot once."""
    config = Config.from_env()
    config.validate()
    
    bot = JudgmentalPredictionBot(config)
    await bot.run_once()
    
    # Print performance summary
    bot.performance_tracker.print_summary()


async def example_analyze_market():
    """Example of analyzing a single market."""
    from market_analyzer import MarketAnalyzer
    from llm_analyzer import LLMAnalyzer
    
    # Example market data
    example_market = {
        "id": "example123",
        "question": "Will AI achieve AGI by 2025?",
        "description": "A question about artificial general intelligence",
        "creatorUsername": "MikhailTal",
        "probability": 0.35,
        "totalLiquidity": 150.0,
        "volume24Hours": 50.0,
        "isResolved": False,
        "closeTime": 1735689600000,  # Example timestamp
    }
    
    # Analyze market
    analyzer = MarketAnalyzer(target_creator="MikhailTal")
    analysis = analyzer.evaluate_market(example_market)
    
    print("Market Analysis:")
    print(f"  Liquidity Score: {analysis['liquidity_score']:.2f}")
    print(f"  Time Score: {analysis['time_score']:.2f}")
    print(f"  Volatility Score: {analysis['volatility_score']:.2f}")
    print(f"  Overall Score: {analysis['overall_score']:.2f}")
    
    # LLM analysis (if API key is configured)
    llm_analyzer = LLMAnalyzer(provider="gemini", gemini_key=None)  # Set your Gemini API key
    if llm_analyzer._client:
        prob, confidence, reasoning = llm_analyzer.analyze_market(example_market)
        print("\nLLM Analysis:")
        print(f"  Predicted Probability: {prob:.2%}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Reasoning: {reasoning}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_analyze_market())

