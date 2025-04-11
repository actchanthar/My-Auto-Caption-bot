import logging
from telegram import Update
from telegram.ext import ContextTypes
import config
from utils.persistence import save_setting, get_setting
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(f"Start command received from {update.effective_user.id}")
    
    welcome_message = (
        "👋 Welcome to the Telegram Auto Caption Bot!\n\n"
        "I can automatically add custom prefixes and suffixes to messages posted "
        "in your channel.\n\n"
        "To get started, add me to your channel as an admin with edit message permissions.\n\n"
        "Type /help to see all available commands."
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info(f"Help command received from {update.effective_user.id}")
    
    help_text = (
        "📝 *Auto Caption Bot Help* 📝\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/setprefix <text> - Set custom prefix for captions\n"
        "/setsuffix <text> - Set custom suffix for captions\n"
        "/status - Show current bot settings\n\n"
        
        "*How to use:*\n"
        "1. Add this bot to your channel as an admin\n"
        "2. Ensure the bot has permission to edit messages\n"
        "3. Post content to your channel\n"
        "4. I'll automatically add your custom prefix and suffix to the caption\n\n"
        
        "*Current Settings:*\n"
        f"Prefix: `{config.CUSTOM_CAPTION_PREFIX}`\n"
        f"Suffix: `{config.CUSTOM_CAPTION_SUFFIX}`\n"
        f"Target Channel: `{config.CHANNEL_ID}`"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_prefix_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set custom prefix for captions."""
    logger.info(f"Set prefix command received from {update.effective_user.id}")
    
    # Check if user is authorized (you may want to implement better auth)
    if not await _is_authorized(update):
        await update.message.reply_text("❌ You are not authorized to change bot settings.")
        return
    
    # Get the prefix from arguments
    if not context.args:
        await update.message.reply_text(
            "Please provide a prefix text.\n"
            "Example: `/setprefix 📢 `"
        )
        return
    
    new_prefix = ' '.join(context.args)
    
    # Save the new prefix
    save_setting('CUSTOM_CAPTION_PREFIX', new_prefix)
    config.CUSTOM_CAPTION_PREFIX = new_prefix
    
    await update.message.reply_text(f"✅ Prefix updated to: `{new_prefix}`", parse_mode='Markdown')

async def set_suffix_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set custom suffix for captions."""
    logger.info(f"Set suffix command received from {update.effective_user.id}")
    
    # Check if user is authorized
    if not await _is_authorized(update):
        await update.message.reply_text("❌ You are not authorized to change bot settings.")
        return
    
    # Get the suffix from arguments
    if not context.args:
        await update.message.reply_text(
            "Please provide a suffix text.\n"
            "Example: `/setsuffix \n\n👉 @MyChannel`"
        )
        return
    
    new_suffix = ' '.join(context.args)
    
    # Save the new suffix
    save_setting('CUSTOM_CAPTION_SUFFIX', new_suffix)
    config.CUSTOM_CAPTION_SUFFIX = new_suffix
    
    await update.message.reply_text(f"✅ Suffix updated to: `{new_suffix}`", parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current bot settings."""
    logger.info(f"Status command received from {update.effective_user.id}")
    
    status_text = (
        "📊 *Current Bot Settings* 📊\n\n"
        f"Prefix: `{config.CUSTOM_CAPTION_PREFIX}`\n"
        f"Suffix: `{config.CUSTOM_CAPTION_SUFFIX}`\n"
        f"Target Channel: `{config.CHANNEL_ID}`\n"
        f"Debug Mode: `{'Enabled' if config.DEBUG else 'Disabled'}`\n"
        f"Bot Version: `1.0.0`"
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def _is_authorized(update: Update) -> bool:
    """Check if the user is authorized to change bot settings."""
    # This is a simple implementation - you should improve this with proper authorization
    # For now, we'll just check if the user is the one who started the bot
    # In a real application, you would maintain a list of admin users or check channel admins
    
    # Get the bot admin user ID (this should be stored securely)
    admin_id = get_setting('ADMIN_USER_ID', 0)
    
    # If no admin is set yet, set the first user who tries to change settings as admin
    if admin_id == 0:
        admin_id = update.effective_user.id
        save_setting('ADMIN_USER_ID', admin_id)
        logger.info(f"Set user {admin_id} as bot admin")
        return True
    
    return update.effective_user.id == admin_id