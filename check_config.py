"""
Configuration checker - validates that all required API keys are set.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_config():
    """Check if all required configuration is set."""
    print("=" * 50)
    print("Configuration Check")
    print("=" * 50)
    
    required = {
        "MANIFOLD_API_KEY": "Manifold Markets API key",
        "MANIFOLD_USERNAME": "Bot username on Manifold",
    }
    
    optional_llm = {
        "GEMINI_API_KEY": "Google Gemini API key (default LLM)",
        "OPENAI_API_KEY": "OpenAI API key (alternative)",
        "ANTHROPIC_API_KEY": "Anthropic API key (alternative)",
    }
    
    llm_provider = os.getenv("LLM_PROVIDER", "gemini")
    
    all_good = True
    
    print("\nRequired Configuration:")
    print("-" * 50)
    for key, description in required.items():
        value = os.getenv(key)
        if value and value != f"your_{key.lower()}_here" and "your_" not in value:
            print(f"✓ {key}: Set")
        else:
            print(f"✗ {key}: NOT SET - {description}")
            all_good = False
    
    print("\nLLM Configuration:")
    print("-" * 50)
    print(f"LLM Provider: {llm_provider}")
    
    if llm_provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here" and "your_" not in gemini_key:
            print("✓ GEMINI_API_KEY: Set")
        else:
            print("✗ GEMINI_API_KEY: NOT SET - Required for Gemini")
            all_good = False
    elif llm_provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_api_key_here" and "your_" not in openai_key:
            print("✓ OPENAI_API_KEY: Set")
        else:
            print("✗ OPENAI_API_KEY: NOT SET - Required for OpenAI")
            all_good = False
    elif llm_provider == "anthropic":
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_api_key_here" and "your_" not in anthropic_key:
            print("✓ ANTHROPIC_API_KEY: Set")
        else:
            print("✗ ANTHROPIC_API_KEY: NOT SET - Required for Anthropic")
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("✓ All required configuration is set!")
        print("You can now run: python main.py")
    else:
        print("✗ Some required configuration is missing.")
        print("\nTo fix:")
        print("1. Open the .env file in this directory")
        print("2. Replace the placeholder values with your actual API keys")
        print("3. Get your API keys from:")
        print("   - Manifold: https://manifold.markets (Settings > API)")
        print("   - Gemini: https://makersuite.google.com/app/apikey")
    print("=" * 50)
    
    return all_good

if __name__ == "__main__":
    check_config()

