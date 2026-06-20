"""Task Extraction Skill — Extracts actionable tasks from free-form text."""

from __future__ import annotations

from typing import Any


class TaskExtractionSkill:
    """Skill that reads free-form text and extracts actionable task items.

    Trigger phrases: "extract tasks", "parse tasks", "meeting notes"
    Input: Raw text string (e.g., meeting notes, emails, chat logs)
    Output: Numbered list of actionable tasks
    """

    name = "task_extraction"
    trigger_phrases = ["extract tasks", "parse tasks", "meeting notes", "action items"]

    def execute(self, raw_text: str, llm: Any) -> list[str]:
        """Extract actionable tasks from unstructured text."""
        if not raw_text.strip():
            return []

        prompt = (
            "Extract all actionable tasks from this text as a numbered list.\n"
            "Each task should be:\n"
            "- Specific and actionable (starts with a verb)\n"
            "- Assigned to someone if mentioned\n"
            "- Include deadline if mentioned\n\n"
            f"Text:\n{raw_text}"
        )

        result = llm.complete(prompt)
        # Parse numbered list into individual items
        tasks = [
            line.strip()
            for line in result.split("\n")
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-"))
        ]
        return tasks
