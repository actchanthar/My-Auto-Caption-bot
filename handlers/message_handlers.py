import logging
from telegram import Update, Bot
from telegram.ext import ContextTypes
import config
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new channel posts and modify captions."""
    # Get the message from the update
    message = update.channel_post
    
    # Check if this post is from our target channel
    if str(message.chat.id) != config.CHANNEL_ID:
        logger.debug(f"Ignoring post from non-target channel: {message.chat.id}")
        return
    
    logger.info(f"Processing new post in channel {message.chat.title} ({message.chat.id})")
    
    # Initialize bot instance for editing messages
    bot = Bot(config.TOKEN)
    
    # Process based on message type
    if message.text:
        await _process_text_message(bot, message)
    elif message.caption is not None:
        await _process_captioned_message(bot, message)
    else:
        logger.debug("Message has no text or caption to process")

async def _process_text_message(bot: Bot, message):
    """Process text messages by adding prefix and suffix."""
    try:
        original_text = message.text
        
        # Skip processing if the message already has our prefix
        # This prevents duplicate processing and infinite loops
        if original_text.startswith(config.CUSTOM_CAPTION_PREFIX):
            logger.debug("Message already has prefix, skipping")
            return
        
        # Create new text with prefix and suffix
        new_text = f"{config.CUSTOM_CAPTION_PREFIX}{original_text}{config.CUSTOM_CAPTION_SUFFIX}"
        
        # Edit the message
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=new_text
        )
        
        logger.info(f"Successfully edited text message in {message.chat.title}")
        
    except Exception as e:
        logger.error(f"Error editing text message: {e}")

async def _process_captioned_message(bot: Bot, message):
    """Process messages with captions (photos, videos, etc.) by adding prefix and suffix."""
    try:
        original_caption = message.caption or ""
        
        # Skip if already processed
        if original_caption.startswith(config.CUSTOM_CAPTION_PREFIX):
            logger.debug("Caption already has prefix, skipping")
            return
        
        # Create new caption with prefix and suffix
        new_caption = f"{config.CUSTOM_CAPTION_PREFIX}{original_caption}{config.CUSTOM_CAPTION_SUFFIX}"
        
        # Edit the caption
        await bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message.message_id,
            caption=new_caption
        )
        
        logger.info(f"Successfully edited caption in {message.chat.title}")
        
    except Exception as e:
        logger.error(f"Error editing caption: {e}")