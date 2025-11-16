#!/usr/bin/env python3
"""
Migration script to add the `event_id` column to the `popup` table and backfill it.
Usage: python migrate_add_popup_event_id.py
"""
import asyncio
from sqlalchemy import text
from database.models import engine


async def add_event_id_column():
    """Add event_id to popup table and backfill existing rows."""
    alter_sql = """
    ALTER TABLE popup
        ADD COLUMN IF NOT EXISTS event_id BIGINT;
    """
    backfill_sql = "UPDATE popup SET event_id = 0 WHERE event_id IS NULL;"

    async with engine.begin() as conn:
        await conn.execute(text(alter_sql))
        await conn.execute(text(backfill_sql))

    print("event_id column added and backfilled successfully.")


if __name__ == "__main__":
    asyncio.run(add_event_id_column())
