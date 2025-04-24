# Steam Link Discord Bot

A Discord bot that detects Steam game links in messages and copies them to a designated channel with attribution and tracking.

## Features

- Automatically detects and validates Steam store links in messages
- Forwards validated links to a designated channel with attribution
- Keeps track of how many times each game has been shared
- Provides commands to view game sharing statistics
- Configurable via environment variables

## Setup

### Prerequisites

- Python 3.8 or higher
- A Discord bot token (create one at [Discord Developer Portal](https://discord.com/developers/applications))
- The channel ID where you want to forward Steam links

### Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and edit it with your Discord bot token and target channel ID

```bash
cp .env.example .env
# Then edit .env with your details
```

4. Run the bot:

```bash
python main.py
```

## Configuration

Configure the bot by setting these environment variables in a `.env` file:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| DISCORD_TOKEN | Your Discord bot token | Yes | None |
| TARGET_CHANNEL_ID | ID of the channel where Steam links will be forwarded | Yes | None |
| COMMAND_PREFIX | Prefix for bot commands | No | ! |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | No | INFO |

## Bot Commands

- `!stats` - Display statistics about the most shared Steam games
- `!help_steam` - Show help information about the bot

## How to Get Channel ID

To get a Discord channel ID:

1. Enable Developer Mode in Discord:
   - Go to User Settings > App Settings > Advanced
   - Toggle "Developer Mode" on

2. Right-click on the channel you want to use as the target and select "Copy ID"

3. Paste this ID as the TARGET_CHANNEL_ID in your .env file

## Bot Permissions

When adding the bot to your server, it needs these permissions:
- Read Messages/View Channels
- Send Messages
- Embed Links
- Read Message History

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Navigate to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable "Message Content Intent"
5. Copy the token and add it to your .env file as DISCORD_TOKEN
6. Go to the "OAuth2 > URL Generator" tab
7. Check "bot" under Scopes
8. Select the required permissions (listed above)
9. Copy the generated URL and open it in your browser to add the bot to your server
   