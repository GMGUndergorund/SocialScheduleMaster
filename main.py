from bot import bot
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logging.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        exit(1)
    
    # Run the bot
    bot.run(token)
