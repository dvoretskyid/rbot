#!/usr/bin/env python3
"""
Simple script to read all messages from a group topic.
Usage: python utils/read_messages.py
"""
import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot
from dotenv import load_dotenv
from prettytable import PrettyTable

# Load environment variables
load_dotenv()

# Configuration
GROUP_ID = -1002927311793
USER_TOPIC_ID = 41


async def read_topic_messages():
    """Read all messages from specified topic."""
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("Error: BOT_TOKEN not found in .env file")
        return

    bot = Bot(token=token)

    try:
        print(f"Reading messages from Group ID: {GROUP_ID}, Topic ID: {USER_TOPIC_ID}\n")

        # Create pretty table
        table = PrettyTable()
        table.field_names = ["Message ID", "From", "Date", "Text Preview"]
        table.align["Message ID"] = "r"
        table.align = "l"
        table.max_width["Text Preview"] = 50

        message_count = 0
        offset_id = 0

        # Read messages (note: this requires bot to be admin or member of the group)
        # We'll try to get chat history
        try:
            # Get some recent messages from the topic
            # Note: Regular bots have limited access to message history
            # You might need to use MTProto (Telethon/Pyrogram) for full history access

            print("Note: Telegram Bot API has limited access to message history.")
            print("For full message history, you might need to use MTProto library (Telethon/Pyrogram).\n")

            # Try to get chat info first
            chat = await bot.get_chat(GROUP_ID)
            print(f"Chat info:")
            print(f"  Title: {chat.title}")
            print(f"  Type: {chat.type}")
            print(f"  ID: {chat.id}\n")

            print("To read message history, the bot needs to:")
            print("  1. Be a member of the group")
            print("  2. Have appropriate permissions")
            print("  3. Or use MTProto API (Telethon/Pyrogram) instead of Bot API\n")

        except Exception as e:
            print(f"Error accessing chat: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(read_topic_messages())
