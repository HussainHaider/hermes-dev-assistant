"""GitHub Agent — Fetches open issues, PRs, and commit summaries."""

from __future__ import annotations

import os
import time
from typing import Any, Optional

from github import Github

from observability.logger import log_event
from tools.llm_client import get_llm


class GitHubAgent:
    """Agent responsible for interacting with GitHub repositories.

    Fetches open issues, summarizes recent commits, and creates task plans
    from issue data.
    """

    name = "github_agent"
    description = "Fetches GitHub issues, PRs, and commit summaries"

    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        self.gh = Github(token)
        self.default_repo = os.getenv("GITHUB_DEFAULT_REPO", "")
        self.llm = get_llm()

    def get_open_issues(self, repo_name: str) -> list[dict[str, Any]]:
        """Fetch up to 10 open issues from the specified repository."""
        repo = self.gh.get_repo(repo_name)
        return [
            {
                "title": issue.title,
                "number": issue.number,
                "labels": [label.name for label in issue.labels],
                "assignee": issue.assignee.login if issue.assignee else None,
                "created_at": issue.created_at.isoformat(),
            }
            for issue in repo.get_issues(state="open")
        ][:10]

    def get_recent_commits(self, repo_name: str, limit: int = 5) -> list[dict[str, str]]:
        """Fetch recent commits from the default branch."""
        repo = self.gh.get_repo(repo_name)
        commits = repo.get_commits()[:limit]
        return [
            {
                "sha": c.sha[:7],
                "message": c.commit.message.split("\n")[0],
                "author": c.commit.author.name,
                "date": c.commit.author.date.isoformat(),
            }
            for c in commits
        ]

    def run(self, task: str, context: dict[str, Any]) -> str:
        """Execute the agent's main logic based on task and context."""
        start = time.time()
        repo = context.get("repo", self.default_repo)

        if "commits" in task.lower():
            commits = self.get_recent_commits(repo)
            result = "Recent commits:\n" + "\n".join(
                f"- `{c['sha']}` {c['message']} ({c['author']})" for c in commits
            )
        else:
            issues = self.get_open_issues(repo)
            result = f"Found {len(issues)} open issues:\n" + "\n".join(
                f"- #{i['number']} {i['title']} [{', '.join(i['labels'])}]"
                for i in issues
            )

        latency = int((time.time() - start) * 1000)
        log_event(
            agent=self.name,
            skill="github_fetch",
            tool="github_api",
            model="n/a",
            input_msg=task,
            output=result,
            latency_ms=latency,
        )
        return result
