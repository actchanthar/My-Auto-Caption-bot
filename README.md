# Telegram Auto Caption Bot

A Telegram bot that automatically edits captions on channel posts. When you post content to your channel, this bot will modify the caption by adding custom prefixes and suffixes.

## Features

- Automatically adds custom prefix and suffix to all channel posts
- Works with both text messages and media posts with captions
- Configurable through commands or environment variables
- Support for both polling mode (development) and webhook mode (production)
- Persistent settings storage
- Detailed logging
- Easy to deploy to Heroku

## Project Structure

```
telegram-auto-caption-bot/
├── bot.py                  # Main entry point
├── config.py               # Configuration management
├── handlers/               # Command and message handlers
│   ├── __init__.py
│   ├── command_handlers.py # Handles bot commands
│   └── message_handlers.py # Handles channel posts
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── logger.py           # Logging setup
│   └── persistence.py      # Settings persistence
├── data/                   # Data storage (created automatically)
│   └── settings.json       # Bot settings
├── requirements.txt        # Python dependencies
├── Procfile               # Heroku process file
├── runtime.txt            # Python version for Heroku
├── .env.example           # Example environment variables
└── README.md              # This file
```

## Setup Instructions

### Prerequisites

- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Your Telegram Channel ID
- Python 3.7 or higher
- Heroku account (for deployment)

### Local Development

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/telegram-auto-caption-bot.git
   cd telegram-auto-caption-bot
   ```

2. Create virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   CHANNEL_ID=your_channel_id_here
   CUSTOM_CAPTION_PREFIX=📢 
   CUSTOM_CAPTION_SUFFIX=\n\n👉 @YourChannelName
   DEBUG=True  # Enable polling mode for development
   ```

4. Run the bot:
   ```
   python bot.py
   ```

### Heroku Deployment

1. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

2. Add environment variables:
   ```
   heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token_here
   heroku config:set CHANNEL_ID=your_channel_id_here
   heroku config:set CUSTOM_CAPTION_PREFIX=📢 
   heroku config:set CUSTOM_CAPTION_SUFFIX="\n\n👉 @YourChannelName"
   heroku config:set DEBUG=False
   heroku config:set WEBHOOK_URL=https://your-app-name.herokuapp.com
   ```

3. Deploy to Heroku:
   ```
   git push heroku main
   ```

4. Ensure at least one dyno is running:
   ```
   heroku ps:scale web=1
   ```

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/setprefix <text>` - Set custom prefix for captions
- `/setsuffix <text>` - Set custom suffix for captions
- `/status` - Show current bot settings

## Getting Your Channel ID

If you don't know your channel ID, you can:

1. Forward a message from your channel to [@username_to_id_bot](https://t.me/username_to_id_bot)
2. The channel ID will be something like `-1001234567890`

## Configuration Options

You can customize the bot's behavior by setting the following environment variables:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required)
- `CHANNEL_ID`: Your channel ID (required)
- `CUSTOM_CAPTION_PREFIX`: Text to add before the original caption (optional)
- `CUSTOM_CAPTION_SUFFIX`: Text to add after the original caption (optional)
- `DEBUG`: Set to `True` for polling mode, `False` for webhook mode (optional)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) (optional)
- `WEBHOOK_URL`: URL for webhook mode (required in production)
- `PORT`: Port for webhook server (optional, default: 8443)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.