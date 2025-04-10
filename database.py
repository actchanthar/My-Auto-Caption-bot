import motor.motor_asyncio
from config import config

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        self.posts = self.db.posts
    
    async def log_post(self, post_id, caption):
        """Store processed posts"""
        await self.posts.insert_one({
            'post_id': post_id,
            'caption': caption,
            'timestamp': datetime.datetime.utcnow()
        })
    
    async def get_stats(self):
        """Get stats for /stats command"""
        return {
            'total_posts': await self.posts.count_documents({}),
            'last_week': await self.posts.count_documents({
                'timestamp': {'$gte': datetime.datetime.utcnow() - datetime.timedelta(days=7)}
            })
        }

db = Database()