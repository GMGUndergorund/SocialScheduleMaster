import re
import logging
import urllib.parse
import urllib.request
import json

logger = logging.getLogger(__name__)

class SteamLinkDetector:
    """Class to detect and validate Steam store links"""
    
    def __init__(self):
        # Regex pattern for Steam store URLs
        # Matches patterns like:
        # - https://store.steampowered.com/app/570/
        # - http://store.steampowered.com/app/570/Dota_2/
        # - https://steamcommunity.com/app/570
        self.steam_url_pattern = re.compile(
            r'https?://(?:store\.steampowered\.com/app/\d+|steamcommunity\.com/app/\d+)[^\s]*'
        )
        
        self.game_id_pattern = re.compile(r'/app/(\d+)')
    
    def extract_steam_links(self, text):
        """Extract Steam store links from text"""
        if not text:
            return []
        
        # Find all matches
        matches = self.steam_url_pattern.findall(text)
        
        # Validate each match
        valid_links = []
        for match in matches:
            if self.is_valid_steam_link(match):
                valid_links.append(match)
        
        return valid_links
    
    def is_valid_steam_link(self, url):
        """Check if a URL is a valid Steam store link"""
        try:
            # Basic validation with regex
            match = self.game_id_pattern.search(url)
            if not match:
                return False
            
            # For more advanced validation, we could make a HEAD request to verify
            # the URL exists, but we'll skip that for now to avoid rate limiting
            return True
        except Exception as e:
            logger.error(f"Error validating Steam link {url}: {e}")
            return False
    
    def extract_game_id(self, url):
        """Extract the game ID from a Steam URL"""
        match = self.game_id_pattern.search(url)
        if match:
            return match.group(1)
        return None
    
    def get_game_info(self, game_id):
        """Retrieve game information from Steam API (for future use)"""
        # This would require a Steam API key and would be implemented
        # if we wanted to display game titles, prices, etc.
        pass
