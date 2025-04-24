import os
import threading
from bot import start_bot
from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
from config import load_config
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("steam_link_bot")

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "steam_link_bot_secret_key")

# Global variable to track if bot is running
bot_thread = None
bot_running = False

# Load configuration
config = load_config()

@app.route('/')
def index():
    """
    Display the bot status and configuration page
    """
    return render_template('index.html', 
                          bot_running=bot_running,
                          config=config)

@app.route('/start_bot', methods=['POST'])
def start_bot_route():
    """
    Start the Discord bot in a separate thread
    """
    global bot_thread, bot_running
    
    if not bot_running:
        # Check if token and channel are set
        if not config["DISCORD_TOKEN"]:
            flash("Discord token is not set. Please configure it first.", "danger")
            return redirect(url_for('index'))
            
        if config["TARGET_CHANNEL_ID"] == 0:
            flash("Target channel ID is not set. Please configure it first.", "danger")
            return redirect(url_for('index'))
        
        # Start bot in a new thread
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        bot_running = True
        flash("Bot started successfully!", "success")
    else:
        flash("Bot is already running.", "info")
        
    return redirect(url_for('index'))

@app.route('/update_config', methods=['POST'])
def update_config():
    """
    Update the bot configuration from the web form
    """
    # Get form data
    discord_token = request.form.get('discord_token')
    target_channel_id = request.form.get('target_channel_id')
    command_prefix = request.form.get('command_prefix')
    log_level = request.form.get('log_level')
    
    # Update .env file
    with open('.env', 'w') as f:
        f.write(f"# Discord Bot Token (required)\n")
        f.write(f"DISCORD_TOKEN={discord_token}\n\n")
        f.write(f"# Channel ID where Steam links will be forwarded (required)\n")
        f.write(f"TARGET_CHANNEL_ID={target_channel_id}\n\n")
        f.write(f"# Command prefix for bot commands (optional, default: !)\n")
        f.write(f"COMMAND_PREFIX={command_prefix}\n\n")
        f.write(f"# Logging level (optional, default: INFO)\n")
        f.write(f"# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL\n")
        f.write(f"LOG_LEVEL={log_level}\n")
    
    # Reload config
    global config
    config = load_config()
    
    flash("Configuration updated successfully! Restart the bot for changes to take effect.", "success")
    return redirect(url_for('index'))

# Run the discord bot if executed directly
if __name__ == "__main__":
    # Check if we're running in a Flask development server
    if os.environ.get('FLASK_APP'):
        app.run(host="0.0.0.0", port=5000)
    else:
        # Start bot directly
        start_bot()
