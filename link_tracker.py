import logging
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class LinkTracker:
    """Class to track and count Steam links shared in Discord"""
    
    def __init__(self):
        # Structure:
        # {
        #   game_id: {
        #     "count": 5,
        #     "url": "https://store.steampowered.com/app/570/Dota_2/",
        #     "first_timestamp": 1625097600,
        #     "first_user_id": "123456789",
        #     "users": set()
        #   }
        # }
        self.links = defaultdict(lambda: {
            "count": 0,
            "url": "",
            "first_timestamp": 0,
            "first_user_id": None,
            "users": set()
        })
    
    def increment_link(self, game_id, url, user_id):
        """Increment the counter for a specific Steam link"""
        if not game_id:
            return
        
        # Update the link data
        self.links[game_id]["count"] += 1
        self.links[game_id]["url"] = url
        self.links[game_id]["users"].add(user_id)
        
        # Set first timestamp and user if not already set
        if not self.links[game_id]["first_timestamp"]:
            self.links[game_id]["first_timestamp"] = int(time.time())
            self.links[game_id]["first_user_id"] = user_id
        
        logger.debug(f"Incremented count for game {game_id} to {self.links[game_id]['count']}")
    
    def get_link_count(self, game_id):
        """Get the count for a specific game ID"""
        if game_id in self.links:
            return self.links[game_id]["count"]
        return 0
    
    def get_top_links(self, limit=10):
        """Get the top shared links sorted by count"""
        # Sort by count in descending order
        sorted_links = sorted(
            self.links.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )
        
        # Return the top N links
        return sorted_links[:limit]
    
    def get_unique_sharers(self, game_id):
        """Get the number of unique users who have shared a specific game"""
        if game_id in self.links:
            return len(self.links[game_id]["users"])
        return 0
    
    def get_total_links_shared(self):
        """Get the total number of all shared links"""
        return sum(item["count"] for item in self.links.values())
