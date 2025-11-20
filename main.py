"""
Main entry point for the judgmental prediction bot.
"""
import asyncio
import logging
import sys
from config import Config
from bot import JudgmentalPredictionBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        
        # Create and run bot
        bot = JudgmentalPredictionBot(config)
        
        # Run bot
        asyncio.run(bot.run())
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

