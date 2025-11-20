"""
Demo mode - test the bot without API keys.
This demonstrates the bot's functionality without making actual API calls.
"""
import asyncio
import logging
from market_analyzer import MarketAnalyzer
from llm_analyzer import LLMAnalyzer
from strategies import LLMStrategy, KellyStrategy, CompositeStrategy

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo():
    """Run a demo of the bot's analysis capabilities."""
    print("=" * 60)
    print("Judgmental Prediction Bot - Demo Mode")
    print("=" * 60)
    print()
    
    # Example market data (simulating a MikhailTal market)
    example_market = {
        "id": "demo-market-123",
        "question": "Will AI achieve AGI by 2025?",
        "description": "A question about artificial general intelligence and its timeline",
        "creatorUsername": "MikhailTal",
        "creatorId": "demo-creator-id",
        "probability": 0.35,
        "totalLiquidity": 150.0,
        "volume24Hours": 50.0,
        "isResolved": False,
        "closeTime": 1735689600000,  # Example timestamp
        "url": "https://manifold.markets/demo/market-123"
    }
    
    print("Example Market:")
    print(f"  Question: {example_market['question']}")
    print(f"  Creator: {example_market['creatorUsername']}")
    print(f"  Current Probability: {example_market['probability']:.1%}")
    print(f"  Liquidity: {example_market['totalLiquidity']:.2f}")
    print()
    
    # Market Analysis
    print("Step 1: Market Analysis")
    print("-" * 60)
    analyzer = MarketAnalyzer(target_creator="MikhailTal", min_liquidity=50.0)
    
    # Check if it's a target market
    is_target = analyzer._is_target_market(example_market)
    print(f"  Is target market: {is_target}")
    
    # Evaluate market
    analysis = analyzer.evaluate_market(example_market)
    print(f"  Liquidity Score: {analysis['liquidity_score']:.2f}")
    print(f"  Time Score: {analysis['time_score']:.2f}")
    print(f"  Volatility Score: {analysis['volatility_score']:.2f}")
    print(f"  Volume Score: {analysis['volume_score']:.2f}")
    print(f"  Overall Score: {analysis['overall_score']:.2f}")
    print()
    
    # LLM Analysis (if available)
    print("Step 2: LLM Analysis")
    print("-" * 60)
    llm_analyzer = LLMAnalyzer(provider="gemini", gemini_key=None)
    
    if llm_analyzer._client:
        print("  LLM client available - would analyze market...")
        # In real mode, this would call the LLM
        # prob, confidence, reasoning = llm_analyzer.analyze_market(example_market)
        print("  (Skipping actual LLM call in demo mode)")
    else:
        print("  LLM client not available (no API key)")
        print("  Using simulated prediction: prob=0.65, confidence=0.75")
        prob, confidence, reasoning = 0.65, 0.75, "Simulated analysis"
    print()
    
    # Strategy Evaluation
    print("Step 3: Strategy Evaluation")
    print("-" * 60)
    
    # Create strategies
    llm_strategy = LLMStrategy(min_confidence=0.6, max_bet=50.0)
    kelly_strategy = KellyStrategy(max_bet=50.0)
    composite = CompositeStrategy([llm_strategy, kelly_strategy])
    
    # Simulate LLM prediction
    llm_prediction = (0.65, 0.75, "Market appears undervalued based on current trends")
    
    should_trade, bet_amount, side = composite.should_trade(
        example_market, analysis, llm_prediction
    )
    
    print(f"  Should Trade: {should_trade}")
    if should_trade:
        print(f"  Bet Amount: {bet_amount:.2f}")
        print(f"  Side: {side}")
        print(f"  Reasoning: Market probability ({example_market['probability']:.1%}) differs")
        print(f"            from predicted probability (0.65), creating an edge.")
    else:
        print("  Strategy determined not to trade this market.")
    print()
    
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("To run the full bot:")
    print("1. Add your MANIFOLD_API_KEY and MANIFOLD_USERNAME to .env")
    print("2. Ensure GEMINI_API_KEY is set (already configured)")
    print("3. Run: python main.py")
    print()


if __name__ == "__main__":
    asyncio.run(demo())

