#!/usr/bin/env python3
"""
Script to send messages to users from usernames.txt file.
Usage: python utils/send_message_to_users.py [--test] [--send-all]
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from dotenv import load_dotenv
from prettytable import PrettyTable
from sqlalchemy import select
from database.models import AsyncSessionLocal, PopUp

# Load environment variables
load_dotenv()

# Message to send
MESSAGE = """Початок POP UP о 18:00.
Я чекаю на тебе у The Naked Room.🪽"""


async def get_usernames_from_db():
    """Get usernames from database of users who started the bot."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PopUp))
        popups = result.scalars().all()
        usernames = [f"@{p.username}" for p in popups if p.username]
        return usernames


async def send_messages(test_mode=True, send_all=False, use_db=False):
    """Send messages to users from usernames.txt."""

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN not found in .env file")
        return

    bot = Bot(token=token)

    # Read usernames from file
    usernames_file = Path(__file__).parent / "usernames.txt"

    if not usernames_file.exists():
        print(f"Error: {usernames_file} not found")
        await bot.session.close()
        return

    with open(usernames_file, 'r', encoding='utf-8') as f:
        usernames = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    # Filter out @None
    usernames = [u for u in usernames if u != "@None"]

    print(f"\nFound {len(usernames)} usernames in file\n")

    # Create results table
    table = PrettyTable()
    table.field_names = ["Username", "Status", "Details"]
    table.align = "l"

    success_count = 0
    error_count = 0
    skipped_count = 0

    for username in usernames:
        try:
            # Skip if not dvoretskyid and not in send-all mode
            if not send_all and username != "@dvoretskyid":
                table.add_row([username, "⏭ SKIPPED", "Use --send-all to send to everyone"])
                skipped_count += 1
                continue

            # Test mode - only show what would be sent
            if test_mode and username == "@dvoretskyid":
                print(f"\n{'='*60}")
                print(f"TEST MODE - Would send to {username}:")
                print(f"{'='*60}")
                print(MESSAGE)
                print(f"{'='*60}\n")
                table.add_row([username, "🧪 TEST", "Message preview shown (not sent)"])
                skipped_count += 1
                continue

            # Get chat (remove @ if present for get_chat call)
            username_clean = username.lstrip('@')
            chat = await bot.get_chat(username_clean)

            # Send message
            await bot.send_message(
                chat_id=chat.id,
                text=MESSAGE
            )

            table.add_row([username, "✅ SENT", f"Chat ID: {chat.id}"])
            success_count += 1
            print(f"✅ Message sent to {username}")

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        except TelegramForbiddenError:
            table.add_row([username, "❌ ERROR", "User blocked the bot"])
            error_count += 1
            print(f"❌ {username}: User blocked the bot")

        except TelegramBadRequest as e:
            error_msg = str(e)
            if "chat not found" in error_msg.lower():
                table.add_row([username, "❌ ERROR", "Chat not found (username invalid/changed)"])
                print(f"❌ {username}: Chat not found")
            elif "user not found" in error_msg.lower():
                table.add_row([username, "❌ ERROR", "User not found"])
                print(f"❌ {username}: User not found")
            elif "can't initiate conversation" in error_msg.lower():
                table.add_row([username, "❌ ERROR", "Can't start conversation (user must start bot first)"])
                print(f"❌ {username}: User must start bot first")
            else:
                table.add_row([username, "❌ ERROR", f"{error_msg[:50]}"])
                print(f"❌ {username}: {error_msg}")
            error_count += 1

        except Exception as e:
            table.add_row([username, "❌ ERROR", str(e)[:40]])
            error_count += 1
            print(f"❌ {username}: {e}")

    # Display results
    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    print(table)
    print(f"\n📊 Summary:")
    print(f"  ✅ Sent: {success_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  ⏭ Skipped: {skipped_count}")
    print(f"  📝 Total: {len(usernames)}")

    if not send_all:
        print(f"\n⚠️  Use --send-all flag to send to all users")
    if test_mode:
        print(f"\n⚠️  You are in TEST MODE. Use --send flag to actually send messages")

    await bot.session.close()


if __name__ == "__main__":
    # Check flags
    test_mode = "--send" not in sys.argv
    send_all = "--send-all" in sys.argv

    print("\n" + "="*80)
    print("📨 MESSAGE SENDER SCRIPT")
    print("="*80)

    if test_mode:
        print("🧪 TEST MODE: Messages will NOT be sent (preview only)")
        print("   Use --send flag to actually send messages")
    else:
        print("🚀 LIVE MODE: Messages WILL be sent!")

    if send_all:
        print("📢 SEND TO ALL: Will send to ALL users in the file")
    else:
        print("🎯 SEND TO ONE: Will only send to @dvoretskyid")
        print("   Use --send-all flag to send to everyone")

    print("="*80 + "\n")

    # Ask for confirmation if in live mode
    if not test_mode:
        user_count = "ALL USERS" if send_all else "@dvoretskyid ONLY"
        response = input(f"⚠️  Are you sure you want to send messages to {user_count}? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled")
            sys.exit(0)

    asyncio.run(send_messages(test_mode=test_mode, send_all=send_all))
