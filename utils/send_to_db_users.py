#!/usr/bin/env python3
"""
Script to send messages to users from database (using their telegram_id).
Usage: python utils/send_to_db_users.py [--send] [--send-all]
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

# Test user telegram_id for @dvoretskyid
TEST_USER_ID = None  # Will be determined from username


async def get_users_from_db():
    """Get all users from database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PopUp))
        return result.scalars().all()


async def send_messages(test_mode=True, send_all=False):
    """Send messages to users from database."""

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN not found in .env file")
        return

    bot = Bot(token=token)

    try:
        # Get users from database
        print("\nFetching users from database...")
        users = await asyncio.wait_for(get_users_from_db(), timeout=10.0)

        if not users:
            print("No users found in database")
            await bot.session.close()
            return

        print(f"Found {len(users)} users in database\n")

        # Find test user
        test_user = None
        for user in users:
            if user.username and user.username.lower() == "dvoretskyid":
                test_user = user
                break

        # Create results table
        table = PrettyTable()
        table.field_names = ["Name", "Username", "Telegram ID", "Status", "Details"]
        table.align = "l"

        success_count = 0
        error_count = 0
        skipped_count = 0

        for user in users:
            username_display = f"@{user.username}" if user.username else "No username"
            name_display = user.name or "No name"

            try:
                # Skip if not test user and not in send-all mode
                if not send_all and (not test_user or user.id != test_user.id):
                    table.add_row([
                        name_display,
                        username_display,
                        user.telegram_id,
                        "⏭ SKIPPED",
                        "Use --send-all to send to everyone"
                    ])
                    skipped_count += 1
                    continue

                # Test mode - only show what would be sent
                if test_mode:
                    if test_user and user.id == test_user.id:
                        print(f"\n{'='*60}")
                        print(f"TEST MODE - Would send to {username_display}:")
                        print(f"Name: {name_display}")
                        print(f"Telegram ID: {user.telegram_id}")
                        print(f"{'='*60}")
                        print(MESSAGE)
                        print(f"{'='*60}\n")
                    table.add_row([
                        name_display,
                        username_display,
                        user.telegram_id,
                        "🧪 TEST",
                        "Message preview shown (not sent)"
                    ])
                    skipped_count += 1
                    continue

                # Send message using telegram_id
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=MESSAGE
                )

                table.add_row([
                    name_display,
                    username_display,
                    user.telegram_id,
                    "✅ SENT",
                    "Message delivered"
                ])
                success_count += 1
                print(f"✅ Message sent to {username_display} ({name_display})")

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            except TelegramForbiddenError:
                table.add_row([
                    name_display,
                    username_display,
                    user.telegram_id,
                    "❌ ERROR",
                    "User blocked the bot"
                ])
                error_count += 1
                print(f"❌ {username_display}: User blocked the bot")

            except TelegramBadRequest as e:
                error_msg = str(e)
                if "chat not found" in error_msg.lower():
                    details = "Chat not found"
                elif "user is deactivated" in error_msg.lower():
                    details = "User account deactivated"
                else:
                    details = error_msg[:50]

                table.add_row([
                    name_display,
                    username_display,
                    user.telegram_id,
                    "❌ ERROR",
                    details
                ])
                error_count += 1
                print(f"❌ {username_display}: {details}")

            except Exception as e:
                table.add_row([
                    name_display,
                    username_display,
                    user.telegram_id,
                    "❌ ERROR",
                    str(e)[:40]
                ])
                error_count += 1
                print(f"❌ {username_display}: {e}")

        # Display results
        print("\n" + "="*80)
        print("RESULTS:")
        print("="*80)
        print(table)
        print(f"\n📊 Summary:")
        print(f"  ✅ Sent: {success_count}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  ⏭ Skipped: {skipped_count}")
        print(f"  📝 Total: {len(users)}")

        if not send_all:
            print(f"\n⚠️  Use --send-all flag to send to all users")
        if test_mode:
            print(f"\n⚠️  You are in TEST MODE. Use --send flag to actually send messages")

    except asyncio.TimeoutError:
        print("✗ Error: Database connection timeout!")
        print("ℹ Make sure your database is accessible")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Check flags
    test_mode = "--send" not in sys.argv
    send_all = "--send-all" in sys.argv

    print("\n" + "="*80)
    print("📨 MESSAGE SENDER SCRIPT (Database Users)")
    print("="*80)

    if test_mode:
        print("🧪 TEST MODE: Messages will NOT be sent (preview only)")
        print("   Use --send flag to actually send messages")
    else:
        print("🚀 LIVE MODE: Messages WILL be sent!")

    if send_all:
        print("📢 SEND TO ALL: Will send to ALL users in database")
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
