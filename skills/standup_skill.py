"""Standup Draft Skill — Generates standup reports from activity data."""

from __future__ import annotations

from typing import Any


class StandupSkill:
    """Skill that generates a standup report from GitHub activity + Notion tasks.

    Trigger phrases: "standup", "daily report", "morning update"
    Input: Recent commits, completed tasks, blockers
    Output: Formatted standup text (Yesterday/Today/Blockers)
    """

    name = "standup_draft"
    trigger_phrases = ["standup", "daily report", "morning update", "daily standup"]

    def execute(self, data: dict[str, Any], llm: Any) -> str:
        """Generate a standup report from activity data."""
        issues = data.get("issues", [])
        tasks = data.get("tasks", [])
        commits = data.get("commits", [])

        issues_text = "\n".join(
            f"  - #{i['number']}: {i['title']}" for i in issues[:5]
        ) if issues else "  None"

        tasks_text = "\n".join(
            f"  - {t['title']} ({t.get('status', 'unknown')})" for t in tasks[:5]
        ) if tasks else "  None"

        commits_text = "\n".join(
            f"  - {c.get('sha', '?')}: {c.get('message', '')}" for c in commits[:5]
        ) if commits else "  None"

        prompt = (
            "Write a professional standup report for a software engineer.\n\n"
            f"Recent commits:\n{commits_text}\n\n"
            f"Open issues:\n{issues_text}\n\n"
            f"Notion tasks:\n{tasks_text}\n\n"
            "Format strictly as:\n"
            "**Yesterday:** (what was accomplished)\n"
            "**Today:** (what's planned)\n"
            "**Blockers:** (any impediments)\n\n"
            "Keep it under 150 words. Be specific and actionable."
        )
        return llm.complete(prompt)
