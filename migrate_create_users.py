#!/usr/bin/env python3
"""
Migration script to create users table in database.
Usage: python migrate_create_users.py
"""
import asyncio
from database.models import init_db


async def create_users_table():
    """Create users table if it doesn't exist."""
    print("Creating users table...")
    try:
        await init_db()
        print("✅ Users table created successfully!")
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_users_table())
