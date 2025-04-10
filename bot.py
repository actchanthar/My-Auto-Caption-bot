import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
import config
from db import db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = f'Hi! I am Auto Captain Bot. Add me to a group and I can help assign {config.CAPTAIN_TITLE}s.'
    if config.ENABLE_WELCOME_MESSAGE:
        welcome_message += '\n\nUse /help to see available commands.'
        
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = f"""
    Available commands:
    /{config.CMD_START} - Start the bot
    /{config.CMD_HELP} - Show this help message
    /{config.CMD_MAKE_CAPTAIN} - Make the replying user a {config.CAPTAIN_TITLE}
    /{config.CMD_SHOW_CAPTAINS} - Show all {config.CAPTAIN_TITLE}s in the group
    """
    
    # Add admin commands if available
    if hasattr(config, 'CMD_REMOVE_CAPTAIN') and hasattr(config, 'CMD_CLEAR_CAPTAINS'):
        help_text += f"""
    Admin commands:
    /{config.CMD_REMOVE_CAPTAIN} - Remove {config.CAPTAIN_TITLE} status from a user
    /{config.CMD_CLEAR_CAPTAINS} - Remove all {config.CAPTAIN_TITLE}s from the group
    """
    
    await update.message.reply_text(help_text)

async def make_captain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Make a user captain by replying to their message."""
    # Check if message is a reply
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user = update.message.reply_to_message.from_user
        
        # Check if the user who issued the command has admin rights or is a global admin
        user_id = update.effective_user.id
        is_global_admin = user_id in config.ADMIN_IDS
        
        if not is_global_admin:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            is_chat_admin = chat_member.status in ['creator', 'administrator']
        else:
            is_chat_admin = True
            
        if is_chat_admin or is_global_admin:
            # Store captain in the database
            result = db.add_captain(
                chat_id=chat_id,
                user_id=user.id,
                user_name=user.first_name,
                username=user.username
            )
            
            if result:
                await update.message.reply_text(f"{user.first_name} is now a {config.CAPTAIN_TITLE}!")
            else:
                await update.message.reply_text(f"Error making {user.first_name} a {config.CAPTAIN_TITLE}. Please try again.")
        else:
            await update.message.reply_text(f"Only group admins can make {config.CAPTAIN_TITLE}s!")
    else:
        await update.message.reply_text(f"Please reply to a message from the user you want to make {config.CAPTAIN_TITLE}.")

async def show_captains(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all captains in the group."""
    chat_id = update.effective_chat.id
    
    # Get captains from database
    captains = db.get_captains(chat_id)
    
    if not captains:
        await update.message.reply_text(f"There are no {config.CAPTAIN_TITLE}s in this group yet.")
        return
    
    captains_text = f"{config.CAPTAIN_TITLE}s in this group:\n"
    
    for captain in captains:
        captains_text += f"- {captain['user_name']}"
        if captain.get('username'):
            captains_text += f" (@{captain['username']})"
                
        # Add stats if enabled
        if config.ENABLE_CAPTAIN_STATS:
            stats = db.get_user_stats(chat_id, captain['user_id'])
            if stats and 'message_count' in stats:
                captains_text += f" ({stats['message_count']} messages)"
                    
        captains_text += "\n"
    
    await update.message.reply_text(captains_text)

async def remove_captain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove captain status from a user by replying to their message."""
    # Check if message is a reply
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user = update.message.reply_to_message.from_user
        
        # Check if the user who issued the command has admin rights or is a global admin
        user_id = update.effective_user.id
        is_global_admin = user_id in config.ADMIN_IDS
        
        if not is_global_admin:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            is_chat_admin = chat_member.status in ['creator', 'administrator']
        else:
            is_chat_admin = True
            
        if is_chat_admin or is_global_admin:
            # Remove captain from database
            result = db.remove_captain(chat_id, user.id)
            
            if result:
                await update.message.reply_text(f"{user.first_name} is no longer a {config.CAPTAIN_TITLE}.")
            else:
                await update.message.reply_text(f"{user.first_name} is not a {config.CAPTAIN_TITLE}.")
        else:
            await update.message.reply_text(f"Only group admins can remove {config.CAPTAIN_TITLE}s!")
    else:
        await update.message.reply_text(f"Please reply to a message from the {config.CAPTAIN_TITLE} you want to remove.")

async def clear_captains(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all captains in the current group."""
    chat_id = update.effective_chat.id
    
    # Check if the user who issued the command has admin rights or is a global admin
    user_id = update.effective_user.id
    is_global_admin = user_id in config.ADMIN_IDS
    
    if not is_global_admin:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        is_chat_admin = chat_member.status in ['creator', 'administrator']
    else:
        is_chat_admin = True
        
    if is_chat_admin or is_global_admin:
        # Clear captains in database
        result = db.clear_captains(chat_id)
        
        if result:
            await update.message.reply_text(f"All {config.CAPTAIN_TITLE}s have been removed from this group.")
        else:
            await update.message.reply_text(f"Error clearing {config.CAPTAIN_TITLE}s. Please try again.")
    else:
        await update.message.reply_text(f"Only group admins can clear {config.CAPTAIN_TITLE}s!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages and track stats if enabled."""
    if not config.ENABLE_CAPTAIN_STATS:
        return
        
    # Only track messages in groups
    if update.effective_chat.type not in ['group', 'supergroup']:
        return
        
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Update message count in database
    db.update_message_count(
        chat_id=chat_id,
        user_id=user.id,
        user_name=user.first_name,
        username=user.username
    )
    
    # Auto-promote to captain if enabled
    if config.CAPTAIN_AUTO_PROMOTE:
        stats = db.get_user_stats(chat_id, user.id)
        
        if stats and stats.get('message_count', 0) >= config.CAPTAIN_MIN_MESSAGES:
            # Check if already a captain
            if not db.is_captain(chat_id, user.id):
                # Make user a captain
                db.add_captain(
                    chat_id=chat_id,
                    user_id=user.id,
                    user_name=user.first_name,
                    username=user.username
                )
                
                await update.message.reply_text(
                    f"Congratulations {user.first_name}! You've sent {stats['message_count']} messages and are now a {config.CAPTAIN_TITLE}!"
                )

def main() -> None:
    """Start the bot."""
    # Ensure database connection
    if config.MONGODB_URI:
        db.connect()
    
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler(config.CMD_START, start))
    application.add_handler(CommandHandler(config.CMD_HELP, help_command))
    application.add_handler(CommandHandler(config.CMD_MAKE_CAPTAIN, make_captain))
    application.add_handler(CommandHandler(config.CMD_SHOW_CAPTAINS, show_captains))
    application.add_handler(CommandHandler(config.CMD_REMOVE_CAPTAIN, remove_captain))
    application.add_handler(CommandHandler(config.CMD_CLEAR_CAPTAINS, clear_captains))
    
    # Add message handler for stats tracking
    if config.ENABLE_CAPTAIN_STATS:
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Log startup
    logger.info(f"Starting Auto {config.CAPTAIN_TITLE} Bot")
    if config.BOT_USERNAME:
        logger.info(f"Bot username: @{config.BOT_USERNAME}")
    
    # Start the Bot (use webhook if configured, otherwise polling)
    if config.USE_WEBHOOK and config.WEBHOOK_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=config.WEBHOOK_PORT,
            url_path=config.TELEGRAM_TOKEN,
            webhook_url=f"{config.WEBHOOK_URL}/{config.TELEGRAM_TOKEN}"
        )
        logger.info(f"Started webhook on port {config.WEBHOOK_PORT}")
    else:
        application.run_polling()
        logger.info("Started polling")

if __name__ == '__main__':
    main()