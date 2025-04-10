import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am Auto Captain Bot. Add me to a group and I can help assign captains.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    /makecaptain - Make the replying user a captain
    /showcaptains - Show all captains in the group
    """
    await update.message.reply_text(help_text)

async def make_captain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Make a user captain by replying to their message."""
    # Check if message is a reply
    if update.message.reply_to_message:
        chat_id = update.effective_chat.id
        user = update.message.reply_to_message.from_user
        
        # Check if the user who issued the command has admin rights
        user_id = update.effective_user.id
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        
        if chat_member.status in ['creator', 'administrator']:
            # Store captain info in bot_data
            if 'captains' not in context.bot_data:
                context.bot_data['captains'] = {}
            
            if chat_id not in context.bot_data['captains']:
                context.bot_data['captains'][chat_id] = []
            
            # Add user to captains list if not already there
            if user.id not in context.bot_data['captains'][chat_id]:
                context.bot_data['captains'][chat_id].append(user.id)
                await update.message.reply_text(f"{user.first_name} is now a captain!")
            else:
                await update.message.reply_text(f"{user.first_name} is already a captain!")
        else:
            await update.message.reply_text("Only group admins can make captains!")
    else:
        await update.message.reply_text("Please reply to a message from the user you want to make captain.")

async def show_captains(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all captains in the group."""
    chat_id = update.effective_chat.id
    
    if 'captains' not in context.bot_data or chat_id not in context.bot_data['captains'] or not context.bot_data['captains'][chat_id]:
        await update.message.reply_text("There are no captains in this group yet.")
        return
    
    captain_list = context.bot_data['captains'][chat_id]
    captains_text = "Captains in this group:\n"
    
    for captain_id in captain_list:
        try:
            captain = await context.bot.get_chat_member(chat_id, captain_id)
            captains_text += f"- {captain.user.first_name}"
            if captain.user.username:
                captains_text += f" (@{captain.user.username})"
            captains_text += "\n"
        except Exception as e:
            logger.error(f"Error getting captain info: {e}")
    
    await update.message.reply_text(captains_text)

def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        logger.error("No TELEGRAM_TOKEN found in environment variables")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("makecaptain", make_captain))
    application.add_handler(CommandHandler("showcaptains", show_captains))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()