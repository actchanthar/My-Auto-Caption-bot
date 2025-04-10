import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is useful for local development
load_dotenv()

# Bot Configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# Bot Settings
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")  # Your bot's username without @
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "").split(","))) if os.environ.get("ADMIN_IDS") else []

# Captain Settings
CAPTAIN_TITLE = os.environ.get("CAPTAIN_TITLE", "Captain")
CAPTAIN_AUTO_PROMOTE = os.environ.get("CAPTAIN_AUTO_PROMOTE", "False").lower() == "true"
CAPTAIN_MIN_MESSAGES = int(os.environ.get("CAPTAIN_MIN_MESSAGES", "50"))

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
MONGODB_URI = os.environ.get("MONGODB_URI", "")

# Webhook Settings (if you decide to use webhooks instead of polling)
USE_WEBHOOK = os.environ.get("USE_WEBHOOK", "False").lower() == "true"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.environ.get("PORT", 8443))

# Logging Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Feature Flags
ENABLE_WELCOME_MESSAGE = os.environ.get("ENABLE_WELCOME_MESSAGE", "True").lower() == "true"
ENABLE_CAPTAIN_STATS = os.environ.get("ENABLE_CAPTAIN_STATS", "False").lower() == "true"

# Captain Commands
CMD_START = "start"
CMD_HELP = "help"
CMD_MAKE_CAPTAIN = "makecaptain"
CMD_SHOW_CAPTAINS = "showcaptains"
CMD_REMOVE_CAPTAIN = "removecaptain"
CMD_CLEAR_CAPTAINS = "clearcaptains"