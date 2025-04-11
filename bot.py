import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
from handlers import command_handlers, message_handlers
from utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

class TelegramCaptionBot:
    """Main bot class for handling Telegram caption operations"""
    
    def __init__(self):
        """Initialize the bot with configuration"""
        logger.info("Initializing Telegram Caption Bot")
        
        # Initialize bot instance
        self.bot = Bot(config.TOKEN)
        
        # Create application
        self.application = Application.builder().token(config.TOKEN).build()
        
        # Register all handlers
        self._register_handlers()
        
        logger.info("Bot initialization complete")
    
    def _register_handlers(self):
        """Register all command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", command_handlers.start_command))
        self.application.add_handler(CommandHandler("help", command_handlers.help_command))
        self.application.add_handler(CommandHandler("setprefix", command_handlers.set_prefix_command))
        self.application.add_handler(CommandHandler("setsuffix", command_handlers.set_suffix_command))
        self.application.add_handler(CommandHandler("status", command_handlers.status_command))
        
        # Channel post handler
        self.application.add_handler(MessageHandler(filters.ChatType.CHANNEL, message_handlers.handle_channel_post))
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
        
        logger.info("All handlers registered")
    
    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors caused by updates"""
        logger.error(f"Update {update} caused error {context.error}")
    
    def run_polling(self):
        """Run the bot in polling mode (development)"""
        logger.info("Starting bot in polling mode")
        self.application.run_polling()
    
    def run_webhook(self):
        """Run the bot in webhook mode (production)"""
        logger.info(f"Starting bot in webhook mode on port {config.PORT}")
        self.application.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            url_path=config.TOKEN,
            webhook_url=f"{config.WEBHOOK_URL}/{config.TOKEN}"
        )

if __name__ == "__main__":
    # Create the bot
    caption_bot = TelegramCaptionBot()
    
    # Run in appropriate mode based on configuration
    if config.DEBUG:
        caption_bot.run_polling()
    else:
        caption_bot.run_webhook()
