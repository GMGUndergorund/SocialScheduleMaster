import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("steam_link_bot")

def load_config():
    """
    Load configuration from environment variables with fallbacks
    
    Returns:
        dict: Configuration dictionary
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Bot configuration
    config = {
        "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN", ""),
        "TARGET_CHANNEL_ID": int(os.getenv("TARGET_CHANNEL_ID", "0")),
        "COMMAND_PREFIX": os.getenv("COMMAND_PREFIX", "!"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
    
    # Validate required configuration
    if not config["DISCORD_TOKEN"]:
        logger.warning("DISCORD_TOKEN is not set in environment variables")
    
    if config["TARGET_CHANNEL_ID"] == 0:
        logger.warning("TARGET_CHANNEL_ID is not set or invalid in environment variables")
    
    # Set log level
    numeric_level = getattr(logging, config["LOG_LEVEL"].upper(), None)
    if isinstance(numeric_level, int):
        logging.getLogger("steam_link_bot").setLevel(numeric_level)
    else:
        logging.getLogger("steam_link_bot").setLevel(logging.INFO)
        logger.warning(f"Invalid log level: {config['LOG_LEVEL']}")
    
    return config
