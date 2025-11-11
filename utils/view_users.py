#!/usr/bin/env python3
"""
Simple script to view registered users from database.
Usage: python utils/view_users.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from prettytable import PrettyTable
from database.requests import get_all_users, get_user_count


async def display_users():
    """Retrieve and display all registered users in a pretty table."""
    print("\n📊 Fetching users from database...\n")

    try:
        # Fetch data with timeout
        users = await asyncio.wait_for(get_all_users(), timeout=10.0)

        if not users:
            print("✓ Connected successfully!")
            print("ℹ No users found in database.")
            return

        # Create pretty table
        table = PrettyTable()
        table.field_names = [
            "ID",
            "Telegram ID",
            "Username",
            "First Name",
            "Last Name",
            "Created At",
            "Updated At"
        ]

        # Set alignment
        table.align = "l"
        table.align["ID"] = "r"
        table.align["Telegram ID"] = "r"

        # Add rows
        for user in users:
            table.add_row([
                user.id,
                user.telegram_id,
                f"@{user.username}" if user.username else "N/A",
                user.first_name or "N/A",
                user.last_name or "N/A",
                user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                user.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            ])

        # Display table
        print(table)
        print(f"\n✓ Total users: {len(users)}")

    except asyncio.TimeoutError:
        print("✗ Error: Database connection timeout!")
        print("ℹ Make sure your database is accessible or check your .env configuration.")
    except Exception as e:
        print(f"✗ Error retrieving data: {e}")
        print("\nℹ Troubleshooting:")
        print("  - Check if .env file exists with correct database credentials")
        print("  - Verify database connection (ENDPOINT, MASTER_USERNAME, MASTER_PASSWORD)")
        print("  - Ensure database is running and accessible")
        print("  - Run migration: python migrate_create_users.py")


if __name__ == "__main__":
    asyncio.run(display_users())
