#!/usr/bin/env python3
"""
Script to send messages directly to users by username.
Note: This only works if users have already interacted with your bot.
Usage: python utils/send_direct.py [--send] [--send-all]
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

# Load environment variables
load_dotenv()

# Message to send
MESSAGE = """Початок POP UP о 18:00.
Я чекаю на тебе у The Naked Room.🪽"""


async def send_messages_direct(test_mode=True, send_all=False):
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
            if not send_all and username.lower() not in ["@dvoretskyid", "dvoretskyid"]:
                table.add_row([username, "⏭ SKIPPED", "Use --send-all to send to everyone"])
                skipped_count += 1
                continue

            # Clean username
            username_clean = username.lstrip('@')

            # Test mode - only show what would be sent
            if test_mode:
                if username.lower() in ["@dvoretskyid", "dvoretskyid"]:
                    print(f"\n{'='*60}")
                    print(f"TEST MODE - Would send to @{username_clean}:")
                    print(f"{'='*60}")
                    print(MESSAGE)
                    print(f"{'='*60}\n")
                table.add_row([f"@{username_clean}", "🧪 TEST", "Message preview shown (not sent)"])
                skipped_count += 1
                continue

            # Try to send message directly by username
            # Note: This works only with users who have started your bot before
            try:
                # First, try to get chat info
                chat = await bot.get_chat(f"@{username_clean}")
                chat_id = chat.id
            except TelegramBadRequest:
                # If get_chat fails, we cannot send message
                raise TelegramBadRequest(method="get_chat", message="User hasn't started the bot yet or username is invalid")

            # Send message
            await bot.send_message(
                chat_id=chat_id,
                text=MESSAGE
            )

            table.add_row([f"@{username_clean}", "✅ SENT", f"Chat ID: {chat_id}"])
            success_count += 1
            print(f"✅ Message sent to @{username_clean}")

            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)

        except TelegramForbiddenError:
            table.add_row([f"@{username_clean}", "❌ BLOCKED", "User blocked the bot"])
            error_count += 1
            print(f"❌ @{username_clean}: User blocked the bot")

        except TelegramBadRequest as e:
            error_msg = str(e)
            if "chat not found" in error_msg.lower():
                details = "User hasn't started the bot yet"
            elif "user not found" in error_msg.lower():
                details = "Username not found or invalid"
            elif "can't initiate conversation" in error_msg.lower() or "user hasn't started" in error_msg.lower():
                details = "User must start bot first"
            else:
                details = error_msg[:50]

            table.add_row([f"@{username_clean}", "❌ ERROR", details])
            error_count += 1
            print(f"❌ @{username_clean}: {details}")

        except Exception as e:
            table.add_row([f"@{username_clean}", "❌ ERROR", str(e)[:40]])
            error_count += 1
            print(f"❌ @{username_clean}: {e}")

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

    print(f"\nℹ️  Note: Messages can only be sent to users who have already started your bot!")

    await bot.session.close()


if __name__ == "__main__":
    # Check flags
    test_mode = "--send" not in sys.argv
    send_all = "--send-all" in sys.argv

    print("\n" + "="*80)
    print("📨 DIRECT MESSAGE SENDER (Username-based)")
    print("="*80)

    if test_mode:
        print("🧪 TEST MODE: Messages will NOT be sent (preview only)")
        print("   Use --send flag to actually send messages")
    else:
        print("🚀 LIVE MODE: Messages WILL be sent!")

    if send_all:
        print("📢 SEND TO ALL: Will send to ALL users in usernames.txt")
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

    asyncio.run(send_messages_direct(test_mode=test_mode, send_all=send_all))
