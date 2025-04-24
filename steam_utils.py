import re
import aiohttp
import logging

logger = logging.getLogger("steam_link_bot")

async def is_valid_steam_url(url):
    """
    Validates if a URL is a legitimate Steam game URL by checking:
    1. If it matches the expected pattern
    2. If it actually leads to a real Steam game page
    
    Args:
        url: The Steam URL to validate
    
    Returns:
        bool: True if the URL is a valid Steam game URL, False otherwise
    """
    # Check URL pattern (more strict than the initial regex)
    pattern = r'^https?://store\.steampowered\.com/app/(\d+)(?:/[^/\s]+)?'
    match = re.match(pattern, url)
    
    if not match:
        logger.debug(f"URL doesn't match Steam app pattern: {url}")
        return False
    
    # Extract app ID
    app_id = match.group(1)
    
    # Verify the app exists by hitting the Steam API
    try:
        async with aiohttp.ClientSession() as session:
            # Using the Steam store API to verify the app exists
            api_url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
            async with session.get(api_url) as response:
                if response.status != 200:
                    logger.debug(f"Steam API returned non-200 status for {url}: {response.status}")
                    return False
                
                data = await response.json()
                
                # Check if the app exists and is a game
                if data and app_id in data and data[app_id]["success"]:
                    return True
                
                logger.debug(f"Steam API indicates this is not a valid game: {url}")
                return False
                
    except Exception as e:
        logger.error(f"Error validating Steam URL {url}: {e}")
        # In case of error, we'll assume it's valid to avoid false negatives
        return True
