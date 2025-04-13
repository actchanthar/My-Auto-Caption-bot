# Telegram Auto Caption Bot

This bot automatically adds custom captions to your Telegram channel posts. It preserves the original caption and adds your custom caption below it.

## Features

- Automatically edit captions of posts in your Telegram channels
- Preserve original captions and add custom captions below
- Support for multiple channels
- Easy setup with simple commands
- MongoDB database for storing channel and caption information

## Commands

- `/start` - Start the bot
- `/addchannel` - Add a channel for auto captioning
- `/addcaption` - Set a custom caption
- `/listchannels` - List all your channels
- `/removechannel` - Remove a channel
- `/help` - Show help message

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token (get from @BotFather)
- MongoDB database (local or Atlas)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/telegram-auto-caption-bot.git
   cd telegram-auto-caption-bot
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   MONGO_URI=your_mongodb_uri_here
   ```

### Running the Bot

```
python bot.py
```

### Deploying to Heroku

1. Make sure you have the Heroku CLI installed and are logged in.

2. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

3. Add the MongoDB add-on or set your MongoDB URI:
   ```
   # If using MongoDB Atlas
   heroku config:set MONGO_URI=your_mongodb_uri_here
   
   # If using Heroku add-on
   heroku addons:create mongolab:sandbox
   ```

4. Set your Telegram Bot Token:
   ```
   heroku config:set TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

5. Create a `Procfile` with the following content:
   ```
   web: python bot.py
   ```

6. Deploy to Heroku:
   ```
   git push heroku main
   ```

## How to Use

1. Start a chat with your bot and send the `/start` command
2. Add the bot as an administrator to your channel with edit message permissions
3. Use `/addchannel @your_channel` to register your channel with the bot
4. Use `/addcaption Your custom caption here` to set your custom caption
5. Now when you post in your channel, the bot will automatically add the custom caption below the original caption

## License

This project is licensed under the MIT License - see the LICENSE file for details.