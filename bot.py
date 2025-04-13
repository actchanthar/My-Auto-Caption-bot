import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from telegram.constants import ParseMode
import asyncio
import pymongo
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Import config values
from config import API_ID, API_HASH

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(MONGO_URI)
db = client["caption_bot_db"]
channels_collection = db["channels"]
captions_collection = db["captions"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n"
        f"I'm an Auto Caption Bot. I can add custom captions to your channel posts.\n\n"
        f"Commands:\n"
        f"/start - Start the bot\n"
        f"/addchannel - Add a channel for auto captioning\n"
        f"/addcaption - Set a custom caption\n"
        f"/listchannels - List all your channels\n"
        f"/removechannel - Remove a channel\n"
        f"/help - Show help message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Commands:\n"
        "/start - Start the bot\n"
        "/addchannel - Add a channel for auto captioning\n"
        "/addcaption - Set a custom caption\n"
        "/listchannels - List all your channels\n"
        "/removechannel - Remove a channel\n"
        "/help - Show this help message\n\n"
        "How to use:\n"
        "1. Add this bot as an admin to your channel with edit permissions\n"
        "2. Use /addchannel to register your channel\n"
        "3. Use /addcaption to set your custom caption\n"
        "4. Post anything to your channel, and I will automatically add your custom caption!"
    )

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a channel for auto captioning."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "Please provide your channel username or ID.\n"
            "Example: /addchannel @your_channel"
        )
        return
    
    channel_id = context.args[0]
    
    # Check if the channel already exists
    existing_channel = channels_collection.find_one({"user_id": user_id, "channel_id": channel_id})
    if existing_channel:
        await update.message.reply_text(f"Channel {channel_id} is already registered.")
        return
    
    try:
        # Try to get channel info to verify bot has access
        chat = await context.bot.get_chat(channel_id)
        
        # Add channel to database
        channels_collection.insert_one({
            "user_id": user_id,
            "channel_id": channel_id,
            "channel_title": chat.title
        })
        
        await update.message.reply_text(
            f"Channel '{chat.title}' has been successfully added!\n"
            f"Now use /addcaption to set your custom caption."
        )
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await update.message.reply_text(
            "Failed to add the channel. Make sure:\n"
            "1. The channel ID/username is correct\n"
            "2. This bot is an admin in the channel\n"
            "3. The bot has permission to edit messages"
        )

async def add_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a custom caption for channels."""
    user_id = update.effective_user.id
    
    # Check if the user has any channels
    user_channels = list(channels_collection.find({"user_id": user_id}))
    if not user_channels:
        await update.message.reply_text(
            "You haven't added any channels yet. Use /addchannel first."
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "Please provide your custom caption text.\n"
            "Example: /addcaption Your custom caption here"
        )
        return
    
    custom_caption = " ".join(context.args)
    
    # If user has only one channel, set caption for that
    if len(user_channels) == 1:
        channel_id = user_channels[0]["channel_id"]
        
        # Update or insert the caption
        captions_collection.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"custom_caption": custom_caption}},
            upsert=True
        )
        
        await update.message.reply_text(
            f"Custom caption has been set for channel {channel_id}:\n\n{custom_caption}"
        )
    else:
        # If user has multiple channels, ask which one to set caption for
        keyboard = []
        for channel in user_channels:
            channel_id = channel["channel_id"]
            channel_title = channel.get("channel_title", channel_id)
            callback_data = f"set_caption_{channel_id}_{custom_caption}"
            # Truncate callback_data if too long
            if len(callback_data) > 64:
                # Save the full caption in context.user_data
                if not context.user_data.get("captions"):
                    context.user_data["captions"] = {}
                context.user_data["captions"][channel_id] = custom_caption
                callback_data = f"set_caption_{channel_id}"
            
            keyboard.append([InlineKeyboardButton(channel_title, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a channel to set this caption for:", reply_markup=reply_markup)

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all channels registered by the user."""
    user_id = update.effective_user.id
    
    user_channels = list(channels_collection.find({"user_id": user_id}))
    if not user_channels:
        await update.message.reply_text("You haven't added any channels yet.")
        return
    
    channels_text = "Your registered channels:\n\n"
    for i, channel in enumerate(user_channels, 1):
        channel_id = channel["channel_id"]
        channel_title = channel.get("channel_title", channel_id)
        
        # Get the caption for this channel
        caption_doc = captions_collection.find_one({"user_id": user_id, "channel_id": channel_id})
        caption = caption_doc.get("custom_caption", "No caption set") if caption_doc else "No caption set"
        
        channels_text += f"{i}. {channel_title} ({channel_id})\n   Caption: {caption}\n\n"
    
    await update.message.reply_text(channels_text)

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a channel from auto captioning."""
    user_id = update.effective_user.id
    
    user_channels = list(channels_collection.find({"user_id": user_id}))
    if not user_channels:
        await update.message.reply_text("You haven't added any channels yet.")
        return
    
    keyboard = []
    for channel in user_channels:
        channel_id = channel["channel_id"]
        channel_title = channel.get("channel_title", channel_id)
        keyboard.append([InlineKeyboardButton(channel_title, callback_data=f"remove_{channel_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a channel to remove:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle callback queries."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data.startswith("set_caption_"):
        parts = query.data.split("_", 2)
        if len(parts) == 3:
            channel_id = parts[2]
            custom_caption = context.user_data.get("captions", {}).get(channel_id)
        else:
            channel_id = parts[1]
            custom_caption = context.user_data.get("captions", {}).get(channel_id)
        
        if custom_caption:
            # Update or insert the caption
            captions_collection.update_one(
                {"user_id": user_id, "channel_id": channel_id},
                {"$set": {"custom_caption": custom_caption}},
                upsert=True
            )
            
            await query.edit_message_text(
                f"Custom caption has been set for channel {channel_id}:\n\n{custom_caption}"
            )
        else:
            await query.edit_message_text("Error: Could not retrieve caption data.")
    
    elif query.data.startswith("remove_"):
        channel_id = query.data.split("_", 1)[1]
        
        # Remove the channel from the database
        channels_collection.delete_one({"user_id": user_id, "channel_id": channel_id})
        captions_collection.delete_one({"user_id": user_id, "channel_id": channel_id})
        
        await query.edit_message_text(f"Channel {channel_id} has been removed.")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle posts in channels."""
    chat_id = update.channel_post.chat_id
    message_id = update.channel_post.message_id
    
    # Find channel in the database
    channel = channels_collection.find_one({"channel_id": str(chat_id)})
    if not channel:
        channel = channels_collection.find_one({"channel_id": f"@{update.channel_post.chat.username}"})
        if not channel:
            return
    
    # Find custom caption for this channel
    caption_doc = captions_collection.find_one({"channel_id": channel["channel_id"]})
    if not caption_doc or not caption_doc.get("custom_caption"):
        return
    
    custom_caption = caption_doc["custom_caption"]
    
    try:
        # Get original caption (if any)
        original_caption = update.channel_post.caption or ""
        
        # Create new caption with original + custom caption
        if original_caption:
            new_caption = f"{original_caption}\n\n{custom_caption}"
        else:
            new_caption = custom_caption
        
        # Edit the message to add the custom caption
        if len(new_caption) <= 1024:  # Telegram caption length limit
            await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=new_caption,
                parse_mode=ParseMode.HTML
            )
        else:
            logger.warning(f"Caption too long ({len(new_caption)} chars) for message {message_id} in {chat_id}")
    except Exception as e:
        logger.error(f"Error editing caption: {e}")

def main() -> None:
    """Run the bot."""
    # Get the token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create the Application with API_ID and API_HASH if available
    builder = Application.builder().token(token)
    
    # Add API_ID and API_HASH if available
    if API_ID and API_HASH:
        logger.info("Using API_ID and API_HASH for enhanced functionality")
        # Store these values for potential future use with MTProto
        
    application = builder.build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addchannel", add_channel))
    application.add_handler(CommandHandler("addcaption", add_caption))
    application.add_handler(CommandHandler("listchannels", list_channels))
    application.add_handler(CommandHandler("removechannel", remove_channel))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add handler for channel posts
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
