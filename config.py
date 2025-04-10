import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Config
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    ADMINS = [int(id) for id in os.getenv('ADMINS', '').split(',') if id]  # Add your user ID
    
    # MongoDB Config
    MONGO_URI = os.getenv('MONGO_URI')
    DB_NAME = os.getenv('DB_NAME', 'caption_bot')
    
    # Caption Settings
    CAPTION_TEMPLATE = os.getenv('CAPTION_TEMPLATE', "📢 {text}\n\n🔔 @ChannelName")
    DEFAULT_HASHTAGS = os.getenv('DEFAULT_HASHTAGS', "#Update #News")
    ENABLED = os.getenv('ENABLED', 'true').lower() == 'true'

config = Config()