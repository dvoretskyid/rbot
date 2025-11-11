#!/usr/bin/env python3
"""
Simple script to get Telegram chat ID by username.
Usage: python utils/view_database.py @username
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def get_chat_id(username: str):
    """Get chat ID by username."""
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("Error: BOT_TOKEN not found in .env file")
        return

    bot = Bot(token=token)

    try:
        # Add @ if not present
        if not username.startswith("@"):
            username = f"@{username}"

        print(f"Fetching chat info for {username}...")
        chat = await bot.get_chat(username)

        print(f"\nChat ID: {chat.id}")
        print(f"Type: {chat.type}")
        if chat.title:
            print(f"Title: {chat.title}")
        if chat.username:
            print(f"Username: @{chat.username}")
        if chat.first_name:
            print(f"First name: {chat.first_name}")
        if chat.last_name:
            print(f"Last name: {chat.last_name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utils/view_database.py @username")
        print("Example: python utils/view_database.py @durov")
        sys.exit(1)

    username = sys.argv[1]
    asyncio.run(get_chat_id(username))
