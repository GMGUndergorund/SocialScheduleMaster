import discord
from discord.ext import commands
import os
import logging
import re
import asyncio
from steam_link_detector import SteamLinkDetector
from link_tracker import LinkTracker

# Create bot instance with all intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize steam link detector and tracker
steam_detector = SteamLinkDetector()
link_tracker = LinkTracker()

# Get the channel ID from environment variable
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))
logger = logging.getLogger(__name__)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord"""
    logger.info(f"{bot.user.name} has connected to Discord!")
    logger.info(f"Target channel ID: {TARGET_CHANNEL_ID}")
    
    # Check if the target channel exists
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        logger.warning(f"Target channel with ID {TARGET_CHANNEL_ID} not found!")
    else:
        logger.info(f"Successfully connected to target channel: #{channel.name}")
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name="for Steam links"
    ))

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in any visible channel"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Skip processing if the message is in the target channel to avoid loops
    if message.channel.id == TARGET_CHANNEL_ID:
        return
    
    # Process Steam links in the message
    try:
        steam_links = steam_detector.extract_steam_links(message.content)
        
        if steam_links:
            # Get target channel
            target_channel = bot.get_channel(TARGET_CHANNEL_ID)
            if not target_channel:
                logger.error(f"Target channel with ID {TARGET_CHANNEL_ID} not found!")
                return
            
            # Track links found
            for link in steam_links:
                game_id = steam_detector.extract_game_id(link)
                if game_id:
                    link_tracker.increment_link(game_id, link, message.author.id)
            
            # Create an embed to forward the message
            embed = discord.Embed(
                title="Steam Game Shared",
                description=message.content,
                color=discord.Color.blue()
            )
            
            # Add author information
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url
            )
            
            # Add footer with original channel and timestamp
            embed.set_footer(
                text=f"Shared in #{message.channel.name} | ID: {message.id}"
            )
            embed.timestamp = message.created_at
            
            # Add the links count
            for link in steam_links:
                game_id = steam_detector.extract_game_id(link)
                if game_id:
                    count = link_tracker.get_link_count(game_id)
                    embed.add_field(
                        name="Times Shared",
                        value=f"This game has been shared {count} time(s)",
                        inline=False
                    )
            
            # Send the embed to the target channel
            await target_channel.send(embed=embed)
            logger.info(f"Forwarded Steam link from {message.author.name} to #{target_channel.name}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
    
    # Process commands
    await bot.process_commands(message)

@bot.command(name="stats")
async def stats(ctx):
    """Command to display statistics about tracked Steam links"""
    top_links = link_tracker.get_top_links(10)
    
    if not top_links:
        await ctx.send("No Steam links have been shared yet!")
        return
    
    # Create an embed with the stats
    embed = discord.Embed(
        title="Steam Link Statistics",
        description="Most frequently shared Steam games",
        color=discord.Color.green()
    )
    
    # Add the top links to the embed
    for rank, (game_id, data) in enumerate(top_links, 1):
        embed.add_field(
            name=f"{rank}. Game ID: {game_id}",
            value=f"URL: {data['url']}\nShared {data['count']} time(s)\nFirst shared by <@{data['first_user_id']}>",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name="help_steam")
async def help_steam(ctx):
    """Custom help command for the bot"""
    embed = discord.Embed(
        title="Steam Link Tracker Bot Help",
        description="I track Steam game links shared in this server",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="How it works",
        value="When someone shares a Steam game link, I'll copy it to the designated channel.",
        inline=False
    )
    
    embed.add_field(
        name="!stats",
        value="Shows statistics about the most frequently shared games",
        inline=False
    )
    
    embed.add_field(
        name="!help_steam",
        value="Shows this help message",
        inline=False
    )
    
    await ctx.send(embed=embed)
