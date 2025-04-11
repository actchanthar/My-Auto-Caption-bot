import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Channel Configuration
CHANNEL_ID = os.getenv('CHANNEL_ID')
if not CHANNEL_ID:
    raise ValueError("No CHANNEL_ID found in environment variables")

# Caption Configuration
CUSTOM_CAPTION_PREFIX = os.getenv('CUSTOM_CAPTION_PREFIX', '📢 ')
CUSTOM_CAPTION_SUFFIX = os.getenv('CUSTOM_CAPTION_SUFFIX', '\n\n👉 @YourChannelName')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Webhook Configuration (for production)
PORT = int(os.getenv('PORT', 8443))
WEBHOOK_URL = os.getenv('WEBHOOK_URL', None)  # Set in production

# Development mode flag
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'