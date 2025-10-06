#!/usr/bin/env python3
"""
Simple script to sync TODOs from morning reports to Notion.

OPTIONAL - Manual sync is fine for now. Use this later if needed.

Requirements:
    pip install notion-client

Setup:
    export NOTION_API_KEY="secret_..."
    export NOTION_DATABASE_ID="..."

Usage:
    python scripts/sync_todos_to_notion.py docs/MORNING_REPORT_2025-10-06.md
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Optional dependency - only import if needed
try:
    from notion_client import Client

    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    print("⚠️  notion-client not installed. Install with: pip install notion-client")


def parse_todo_from_markdown(markdown_path: Path) -> List[Dict]:
    """
    Parse TODO items from markdown file.

    Returns list of tasks with metadata:
        [
            {
                "task": "Fix patient education wizard",
                "status": "completed" | "in_progress" | "not_started",
                "category": "Bug Fix",
                "notes": "...",
                "files": ["file1.py", "file2.tsx"]
            },
            ...
        ]
    """
    with open(markdown_path, "r") as f:
        content = f.read()

    tasks = []

    # Match checkbox patterns: - [ ], - [x], - [~]
    todo_pattern = r"-\s+\[([ x~])\]\s+(.+?)(?=\n|$)"

    for match in re.finditer(todo_pattern, content, re.MULTILINE):
        checkbox, task_text = match.groups()

        # Determine status
        if checkbox == "x":
            status = "Completed"
        elif checkbox == "~":
            status = "In Progress"
        else:
            status = "Not Started"

        # Try to categorize based on keywords
        task_lower = task_text.lower()
        if "test" in task_lower:
            category = "Testing"
        elif "doc" in task_lower or "README" in task_text:
            category = "Documentation"
        elif "fix" in task_lower or "bug" in task_lower:
            category = "Bug Fix"
        elif "router" in task_lower or "service" in task_lower:
            category = "Infrastructure"
        else:
            category = "Feature"

        tasks.append(
            {
                "task": task_text.strip(),
                "status": status,
                "category": category,
                "session_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )

    return tasks


def create_notion_task(client: Client, database_id: str, task: Dict) -> Optional[str]:
    """
    Create a task in Notion database.

    Returns:
        Page ID if created successfully, None otherwise
    """
    if not NOTION_AVAILABLE:
        print("❌ Notion client not available")
        return None

    try:
        response = client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Task": {"title": [{"text": {"content": task["task"]}}]},
                "Status": {"select": {"name": task["status"]}},
                "Category": {"select": {"name": task["category"]}},
                "Session": {"date": {"start": task["session_date"]}},
            },
        )

        return response["id"]

    except Exception as e:
        print(f"❌ Failed to create task '{task['task']}': {e}")
        return None


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/sync_todos_to_notion.py <markdown_file>")
        print(
            "Example: python scripts/sync_todos_to_notion.py docs/MORNING_REPORT_2025-10-06.md"
        )
        sys.exit(1)

    markdown_path = Path(sys.argv[1])
    if not markdown_path.exists():
        print(f"❌ File not found: {markdown_path}")
        sys.exit(1)

    # Check for Notion credentials
    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    if not api_key or not database_id:
        print("❌ Missing Notion credentials!")
        print("Set environment variables:")
        print("  export NOTION_API_KEY='secret_...'")
        print("  export NOTION_DATABASE_ID='...'")
        sys.exit(1)

    if not NOTION_AVAILABLE:
        sys.exit(1)

    print(f"📖 Parsing TODOs from: {markdown_path}")
    tasks = parse_todo_from_markdown(markdown_path)

    print(f"✅ Found {len(tasks)} tasks")

    # Preview tasks
    print("\n📋 Tasks to sync:")
    for i, task in enumerate(tasks, 1):
        status_emoji = (
            "✅"
            if task["status"] == "Completed"
            else "🔄" if task["status"] == "In Progress" else "⭕"
        )
        print(f"  {i}. {status_emoji} [{task['category']}] {task['task'][:60]}...")

    # Ask for confirmation
    response = input("\nSync these tasks to Notion? (y/n): ")
    if response.lower() != "y":
        print("Cancelled")
        sys.exit(0)

    # Sync to Notion
    print("\n🔄 Syncing to Notion...")
    client = Client(auth=api_key)

    created_count = 0
    for task in tasks:
        page_id = create_notion_task(client, database_id, task)
        if page_id:
            created_count += 1
            print(f"  ✅ Created: {task['task'][:50]}...")

    print(f"\n✨ Done! Created {created_count}/{len(tasks)} tasks in Notion")


if __name__ == "__main__":
    main()
