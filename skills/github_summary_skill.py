"""GitHub Summary Skill — Summarizes GitHub issues into concise reports."""

from __future__ import annotations

from typing import Any


class GitHubSummarySkill:
    """Skill that takes a list of GitHub issues and produces a concise summary.

    Trigger phrases: "github issues", "open issues", "what's on github"
    Input: List of issue dicts (title, number, labels)
    Output: Markdown-formatted summary string
    """

    name = "github_summary"
    trigger_phrases = ["github issues", "open issues", "what's on github", "github summary"]

    def execute(self, issues: list[dict[str, Any]], llm: Any) -> str:
        """Summarize a list of GitHub issues using the LLM."""
        if not issues:
            return "No open issues found."

        text = "\n".join(
            f"- #{i['number']}: {i['title']} [{', '.join(i.get('labels', []))}]"
            for i in issues
        )

        prompt = (
            "Summarize these GitHub issues concisely. "
            "Group by theme if possible. Highlight critical/urgent items first:\n\n"
            f"{text}"
        )
        return llm.complete(prompt)
