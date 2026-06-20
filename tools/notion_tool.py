"""Notion Tool — Wrapper around Notion API for task management."""

from __future__ import annotations

import os
from typing import Any, Optional

from notion_client import Client


class NotionTool:
    """Tool for interacting with Notion API.

    Provides methods for reading and creating tasks in a Notion database.
    Used by PlanningAgent and the workflow router.
    """

    name = "notion_tool"
    description = "Manages tasks in Notion databases"

    def __init__(self) -> None:
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise ValueError("NOTION_API_KEY environment variable is required")
        self.client = Client(auth=api_key)
        self.db_id = os.getenv("NOTION_DATABASE_ID", "")

    def get_tasks(self, status_filter: Optional[str] = None) -> list[dict[str, Any]]:
        """Fetch tasks from the Notion database."""
        query_params: dict[str, Any] = {"database_id": self.db_id}

        if status_filter:
            query_params["filter"] = {
                "property": "Status",
                "select": {"equals": status_filter},
            }

        response = self.client.databases.query(**query_params)
        tasks = []
        for page in response["results"]:
            props = page["properties"]
            title_prop = props.get("Name", {}).get("title", [])
            status_prop = props.get("Status", {}).get("select")

            title = title_prop[0]["text"]["content"] if title_prop else "Untitled"
            status = status_prop["name"] if status_prop else "Unknown"

            tasks.append({
                "id": page["id"],
                "title": title,
                "status": status,
                "url": page["url"],
            })
        return tasks

    def add_task(self, title: str, status: str = "To Do") -> dict[str, str]:
        """Create a new task in the Notion database."""
        page = self.client.pages.create(
            parent={"database_id": self.db_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "Status": {"select": {"name": status}},
            },
        )
        return {"id": page["id"], "url": page["url"]}

    def update_task_status(self, page_id: str, status: str) -> None:
        """Update the status of an existing task."""
        self.client.pages.update(
            page_id=page_id,
            properties={"Status": {"select": {"name": status}}},
        )
