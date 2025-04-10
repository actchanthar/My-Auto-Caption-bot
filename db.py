import pymongo
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.captains_collection = None
        self.stats_collection = None
        self.connected = False
        
    def connect(self):
        """Connect to MongoDB database"""
        try:
            # Use the MongoDB URI from config
            self.client = MongoClient(config.MONGODB_URI)
            
            # Ping the server to check connection
            self.client.admin.command('ping')
            
            # Set up database and collections
            self.db = self.client.telegram_captain_bot
            self.captains_collection = self.db.captains
            self.stats_collection = self.db.stats
            
            # Create indexes
            self.captains_collection.create_index([("chat_id", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], unique=True)
            self.stats_collection.create_index([("chat_id", pymongo.ASCENDING), ("user_id", pymongo.ASCENDING)], unique=True)
            
            self.connected = True
            logger.info("Successfully connected to MongoDB")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
            return False
            
    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB connection closed")
            
    # Captain management functions
    def add_captain(self, chat_id, user_id, user_name, username=None):
        """Add a captain to the database"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            # Using upsert to handle both insert and update cases
            result = self.captains_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {
                    "user_name": user_name,
                    "username": username,
                    "is_captain": True
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding captain: {e}")
            return False
            
    def remove_captain(self, chat_id, user_id):
        """Remove a captain from the database"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            result = self.captains_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"is_captain": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error removing captain: {e}")
            return False
            
    def clear_captains(self, chat_id):
        """Remove all captains from a chat"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            result = self.captains_collection.update_many(
                {"chat_id": chat_id},
                {"$set": {"is_captain": False}}
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing captains: {e}")
            return False
            
    def get_captains(self, chat_id):
        """Get all captains for a chat"""
        if not self.connected:
            if not self.connect():
                return []
                
        try:
            captains = self.captains_collection.find(
                {"chat_id": chat_id, "is_captain": True}
            )
            return list(captains)
        except Exception as e:
            logger.error(f"Error getting captains: {e}")
            return []
            
    def is_captain(self, chat_id, user_id):
        """Check if a user is a captain"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            captain = self.captains_collection.find_one(
                {"chat_id": chat_id, "user_id": user_id, "is_captain": True}
            )
            return captain is not None
        except Exception as e:
            logger.error(f"Error checking if user is captain: {e}")
            return False
            
    # Stats functions
    def update_message_count(self, chat_id, user_id, user_name, username=None):
        """Increment message count for a user"""
        if not self.connected:
            if not self.connect():
                return False
                
        try:
            result = self.stats_collection.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$inc": {"message_count": 1},
                    "$set": {
                        "user_name": user_name,
                        "username": username
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating message count: {e}")
            return False
            
    def get_user_stats(self, chat_id, user_id):
        """Get stats for a user"""
        if not self.connected:
            if not self.connect():
                return None
                
        try:
            stats = self.stats_collection.find_one(
                {"chat_id": chat_id, "user_id": user_id}
            )
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
            
    def get_top_users(self, chat_id, limit=5):
        """Get top users by message count"""
        if not self.connected:
            if not self.connect():
                return []
                
        try:
            top_users = self.stats_collection.find(
                {"chat_id": chat_id}
            ).sort("message_count", pymongo.DESCENDING).limit(limit)
            return list(top_users)
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []

# Create a singleton instance
db = Database()