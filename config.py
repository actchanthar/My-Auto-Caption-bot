import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "caption_bot_db"

# Telegram API configuration (for MTProto if needed)
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Collections
CHANNELS_COLLECTION = "channels"
CAPTIONS_COLLECTION = "captions"

# Constants
MAX_CAPTION_LENGTH = 1024  # Telegram's caption length limit
