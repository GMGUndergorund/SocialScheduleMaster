import discord
from discord.ext import commands
import os
import logging
import re
from collections import Counter
import asyncio
from config import load_config
from steam_utils import is_valid_steam_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("steam_link_bot")

# Load configuration
config = load_config()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True  # This is required to read message content
bot = commands.Bot(command_prefix=config["COMMAND_PREFIX"], intents=intents)

# In-memory storage for game link counter
game_links_counter = Counter()

@bot.event
async def on_ready():
    """Event handler for when the bot has connected to Discord."""
    logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    logger.info(f"Target channel for game links: #{await get_target_channel_name()}")
    
    # Set bot activity
    activity = discord.Activity(type=discord.ActivityType.watching, name="for Steam links")
    await bot.change_presence(activity=activity)

async def get_target_channel_name():
    """Helper to get the target channel name for logging purposes."""
    try:
        channel = bot.get_channel(config["TARGET_CHANNEL_ID"])
        return channel.name if channel else "Unknown"
    except:
        return "Unknown"

@bot.event
async def on_message(message):
    """Event handler for when a message is received."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Ignore messages in the target channel to prevent loops
    if message.channel.id == config["TARGET_CHANNEL_ID"]:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check for Steam links in the message
    steam_urls = extract_steam_urls(message.content)
    
    if steam_urls:
        logger.info(f"Found Steam URLs in message: {message.id}")
        
        # Get target channel
        target_channel = bot.get_channel(config["TARGET_CHANNEL_ID"])
        if not target_channel:
            logger.error(f"Target channel {config['TARGET_CHANNEL_ID']} not found!")
            return
            
        for url in steam_urls:
            # Validate if this is a legitimate Steam game URL
            if await is_valid_steam_url(url):
                # Increment counter for this game URL
                game_links_counter[url] += 1
                
                # Create an embed for the shared game
                embed = create_game_embed(message, url)
                
                # Send the embed to the target channel
                try:
                    await target_channel.send(embed=embed)
                    logger.info(f"Successfully forwarded Steam link from {message.author.name} to #{target_channel.name}")
                except discord.HTTPException as e:
                    logger.error(f"Failed to send message to target channel: {e}")

def extract_steam_urls(content):
    """Extract Steam store URLs from message content."""
    # Regular expression for matching Steam store URLs
    steam_url_pattern = r'https?://store\.steampowered\.com/app/\d+(?:/[^/\s]+)?'
    return re.findall(steam_url_pattern, content)

def create_game_embed(message, url):
    """Create a Discord embed for the game link."""
    embed = discord.Embed(
        title="Steam Game Shared",
        description=f"**Link:** {url}",
        color=0x1b2838  # Steam's dark blue color
    )
    
    # Add author information
    embed.set_author(
        name=f"Shared by {message.author.display_name}",
        icon_url=message.author.display_avatar.url if message.author.display_avatar else None
    )
    
    # Add share count
    embed.add_field(name="Times Shared", value=str(game_links_counter[url]), inline=True)
    
    # Add original message link
    jump_url = message.jump_url
    embed.add_field(name="Original Message", value=f"[Jump to message]({jump_url})", inline=True)
    
    # Add timestamp
    embed.timestamp = message.created_at
    
    # Add footer
    embed.set_footer(text=f"From #{message.channel.name} | {message.guild.name}")
    
    return embed

@bot.command(name="stats")
async def show_stats(ctx):
    """Command to show statistics about shared game links."""
    if not game_links_counter:
        await ctx.send("No games have been shared yet.")
        return
    
    # Create an embed for the stats
    embed = discord.Embed(
        title="Steam Game Sharing Statistics",
        description="Most frequently shared Steam games:",
        color=0x1b2838
    )
    
    # Get the top 10 most shared games
    most_common = game_links_counter.most_common(10)
    
    for i, (url, count) in enumerate(most_common):
        embed.add_field(
            name=f"{i+1}. Shared {count} times",
            value=f"[Steam Link]({url})",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="help_steam")
async def help_command(ctx):
    """Custom help command for the bot."""
    embed = discord.Embed(
        title="Steam Link Bot Help",
        description="This bot detects Steam game links and shares them in a designated channel.",
        color=0x1b2838
    )
    
    embed.add_field(
        name=f"{config['COMMAND_PREFIX']}stats",
        value="Show statistics about the most shared Steam games",
        inline=False
    )
    
    embed.add_field(
        name=f"{config['COMMAND_PREFIX']}help_steam",
        value="Show this help message",
        inline=False
    )
    
    await ctx.send(embed=embed)

def start_bot():
    """Start the Discord bot."""
    token = config["DISCORD_TOKEN"]
    if not token:
        logger.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Failed to login. Check if your Discord token is correct.")
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
