import logging
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import config
from database import db
import datetime

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== COMMAND HANDLERS ==========

async def start(update, context):
    """Send welcome message"""
    await update.message.reply_text(
        "🤖 Auto-Caption Bot\n\n"
        "I automatically add captions to your channel posts!\n"
        "Commands:\n"
        "/help - Show all commands\n"
        "/setcaption [text] - Change default caption\n"
        "/toggle [on/off] - Enable/disable auto-captioning"
    )

async def help_cmd(update, context):
    """Show help"""
    await update.message.reply_text(
        "🛠 <b>Available Commands:</b>\n\n"
        "• /setcaption [text] - Change default caption\n"
        "• /sethashtags [tags] - Update hashtags\n"
        "• /toggle [on/off] - Enable/disable bot\n"
        "• /stats - Show usage statistics\n\n"
        "<i>Admin-only:</i>\n"
        "• /addadmin [user_id] - Grant admin access",
        parse_mode='HTML'
    )

async def set_caption(update, context):
    """Change caption template"""
    if update.effective_user.id not in config.ADMINS:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    new_template = ' '.join(context.args)
    if not new_template:
        await update.message.reply_text(f"Current template:\n\n{config.CAPTION_TEMPLATE}")
        return
    
    config.CAPTION_TEMPLATE = new_template
    await update.message.reply_text("✅ Caption template updated!")

async def toggle_bot(update, context):
    """Enable/disable auto-captioning"""
    if update.effective_user.id not in config.ADMINS:
        await update.message.reply_text("🚫 Admin only!")
        return
    
    arg = context.args[0].lower() if context.args else ''
    if arg in ['on', 'true', 'enable']:
        config.ENABLED = True
        await update.message.reply_text("🟢 Auto-captioning ENABLED")
    elif arg in ['off', 'false', 'disable']:
        config.ENABLED = False
        await update.message.reply_text("🔴 Auto-captioning DISABLED")
    else:
        await update.message.reply_text(f"Current status: {'ENABLED' if config.ENABLED else 'DISABLED'}")

# ========== MAIN BOT LOGIC ==========

async def process_post(update, context):
    """Auto-caption new channel posts"""
    if not config.ENABLED or not update.channel_post:
        return
        
    post = update.channel_post
    if post.caption or post.forward_from:
        return
    
    try:
        media_type = next(
            (mt for mt in ['photo', 'video', 'document'] 
            if getattr(post, mt, None)), None)
        
        caption = config.CAPTION_TEMPLATE.format(
            text=post.text or f"{media_type.capitalize()} post",
            date=datetime.date.today().strftime("%Y-%m-%d")
        )
        
        if config.DEFAULT_HASHTAGS:
            caption += f"\n\n{config.DEFAULT_HASHTAGS}"
        
        await context.bot.edit_message_caption(
            chat_id=post.chat.id,
            message_id=post.message_id,
            caption=caption
        )
        await db.log_post(post.message_id, caption)
    except Exception as e:
        logger.error(f"Failed to process post: {e}")

def main():
    updater = Updater(config.BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("setcaption", set_caption))
    dp.add_handler(CommandHandler("toggle", toggle_bot))
    
    # Channel post handler
    dp.add_handler(MessageHandler(Filters.update.channel_post, process_post))
    
    logger.info("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()