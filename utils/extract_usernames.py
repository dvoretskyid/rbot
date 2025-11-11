#!/usr/bin/env python3
"""
Script to extract all usernames (starting with @) from text.txt
Usage: python utils/extract_usernames.py
"""
import re
from pathlib import Path
from prettytable import PrettyTable


def extract_usernames():
    """Extract all usernames from text.txt file."""

    # Read the file
    file_path = Path(__file__).parent / "text.txt"

    if not file_path.exists():
        print(f"Error: {file_path} not found")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all usernames (pattern: @username)
    # Username can contain letters, numbers, underscores
    usernames = re.findall(r'@([a-zA-Z0-9_]+)', content)

    # Remove duplicates and sort
    unique_usernames = sorted(set(usernames))

    print(f"\nFound {len(usernames)} total usernames ({len(unique_usernames)} unique)\n")

    # Create pretty table
    table = PrettyTable()
    table.field_names = ["#", "Username", "Count"]
    table.align["#"] = "r"
    table.align["Username"] = "l"
    table.align["Count"] = "r"

    # Count occurrences
    for i, username in enumerate(unique_usernames, 1):
        count = usernames.count(username)
        table.add_row([i, f"@{username}", count])

    print(table)

    # Print all usernames as a list (for easy copying)
    print("\n" + "="*60)
    print("All unique usernames (copy-paste ready):")
    print("="*60)
    for username in unique_usernames:
        print(f"@{username}")

    # Save to file
    output_file = Path(__file__).parent / "usernames.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for username in unique_usernames:
            f.write(f"@{username}\n")

    print(f"\n✓ Usernames saved to: {output_file}")


if __name__ == "__main__":
    extract_usernames()
