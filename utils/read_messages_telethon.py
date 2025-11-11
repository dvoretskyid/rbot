#!/usr/bin/env python3
"""
Script to read all messages from a group topic using Telethon.
Usage: python utils/read_messages_telethon.py
"""
import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from telethon import TelegramClient
from telethon.tl.types import Message
from dotenv import load_dotenv
from prettytable import PrettyTable
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
GROUP_ID = -1002927311793
USER_TOPIC_ID = 41

# You need to get these from https://my.telegram.org
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")  # Your phone number


async def read_topic_messages():
    """Read all messages from specified topic."""

    if not API_ID or not API_HASH:
        print("Error: API_ID and API_HASH not found in .env file")
        print("Get them from https://my.telegram.org")
        return

    # Create client
    client = TelegramClient('session_name', API_ID, API_HASH)

    try:
        await client.start()
        print(f"Reading messages from Group ID: {GROUP_ID}, Topic ID: {USER_TOPIC_ID}\n")

        # Create pretty table
        table = PrettyTable()
        table.field_names = ["ID", "From", "Date", "Text Preview"]
        table.align["ID"] = "r"
        table.align = "l"
        table.max_width["Text Preview"] = 60

        message_count = 0

        # Read messages from topic
        async for message in client.iter_messages(
            GROUP_ID,
            reply_to=USER_TOPIC_ID,  # Filter by topic
            limit=None  # Get all messages
        ):
            if isinstance(message, Message):
                message_count += 1

                # Get sender name
                sender = "Unknown"
                if message.sender:
                    if hasattr(message.sender, 'first_name'):
                        sender = message.sender.first_name or "Unknown"
                        if hasattr(message.sender, 'last_name') and message.sender.last_name:
                            sender += f" {message.sender.last_name}"
                    elif hasattr(message.sender, 'title'):
                        sender = message.sender.title

                # Get message text preview
                text = message.text or "[Media/Other]"
                if len(text) > 60:
                    text = text[:57] + "..."

                # Format date
                date_str = message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else "Unknown"

                table.add_row([
                    message.id,
                    sender,
                    date_str,
                    text
                ])

                # Print full message details for first few messages
                if message_count <= 5:
                    print(f"\n{'='*80}")
                    print(f"Message ID: {message.id}")
                    print(f"From: {sender}")
                    print(f"Date: {date_str}")
                    print(f"Text: {message.text or '[No text]'}")
                    print('='*80)

        # Display table
        print(f"\n\nAll Messages Summary:")
        print(table)
        print(f"\nTotal messages in topic: {message_count}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(read_topic_messages())
