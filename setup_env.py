"""
Interactive setup script for .env file configuration.
"""
import os

def setup_env():
    """Interactively set up .env file."""
    print("=" * 60)
    print("Judgmental Prediction Bot - Environment Setup")
    print("=" * 60)
    print()
    
    env_vars = {}
    
    # Required variables
    print("Required Configuration:")
    print("-" * 60)
    
    manifold_key = input("Enter your Manifold API key (or press Enter to skip): ").strip()
    if manifold_key:
        env_vars["MANIFOLD_API_KEY"] = manifold_key
    
    username = input("Enter your bot username on Manifold (or press Enter to skip): ").strip()
    if username:
        env_vars["MANIFOLD_USERNAME"] = username
    
    # LLM Configuration
    print("\nLLM Configuration:")
    print("-" * 60)
    print("Current LLM provider options: gemini (default), openai, anthropic")
    provider = input("Enter LLM provider [gemini]: ").strip().lower() or "gemini"
    env_vars["LLM_PROVIDER"] = provider
    
    if provider == "gemini":
        gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
        if gemini_key:
            env_vars["GEMINI_API_KEY"] = gemini_key
    elif provider == "openai":
        openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if openai_key:
            env_vars["OPENAI_API_KEY"] = openai_key
    elif provider == "anthropic":
        anthropic_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
        if anthropic_key:
            env_vars["ANTHROPIC_API_KEY"] = anthropic_key
    
    # Optional settings
    print("\nOptional Settings (press Enter to use defaults):")
    print("-" * 60)
    
    target_creator = input("Target market creator [MikhailTal]: ").strip() or "MikhailTal"
    env_vars["TARGET_CREATOR"] = target_creator
    
    # Read existing .env if it exists
    existing_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_vars[key.strip()] = value.strip()
    
    # Merge with existing, keeping user input
    for key, value in env_vars.items():
        existing_vars[key] = value
    
    # Write .env file
    env_template = """# Manifold Markets Configuration
MANIFOLD_API_KEY={MANIFOLD_API_KEY}
MANIFOLD_USERNAME={MANIFOLD_USERNAME}

# Target Market Creator
TARGET_CREATOR={TARGET_CREATOR}

# LLM Configuration
GEMINI_API_KEY={GEMINI_API_KEY}
LLM_PROVIDER={LLM_PROVIDER}

# Optional: Alternative LLM providers
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=

# Risk Management
MAX_POSITION_SIZE=100
MAX_PORTFOLIO_RISK=0.3
MIN_MARKET_LIQUIDITY=50
MAX_MARKETS_OPEN=10

# Trading Parameters
CHECK_INTERVAL=300
MIN_CONFIDENCE=0.6
MAX_BET_AMOUNT=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
"""
    
    # Fill in defaults for missing values
    defaults = {
        "MANIFOLD_API_KEY": existing_vars.get("MANIFOLD_API_KEY", "your_manifold_api_key_here"),
        "MANIFOLD_USERNAME": existing_vars.get("MANIFOLD_USERNAME", "your_bot_username_here"),
        "TARGET_CREATOR": existing_vars.get("TARGET_CREATOR", "MikhailTal"),
        "GEMINI_API_KEY": existing_vars.get("GEMINI_API_KEY", "your_gemini_api_key_here"),
        "LLM_PROVIDER": existing_vars.get("LLM_PROVIDER", "gemini"),
    }
    
    env_content = env_template.format(**defaults)
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("\n✓ .env file updated successfully!")
        print("\nNext steps:")
        print("1. Review the .env file to ensure all values are correct")
        print("2. Run: python check_config.py to verify configuration")
        print("3. Run: python main.py to start the bot")
    except Exception as e:
        print(f"\n✗ Error writing .env file: {e}")

if __name__ == "__main__":
    setup_env()

