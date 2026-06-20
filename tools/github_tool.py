"""GitHub Tool — Wrapper around PyGithub for Hermes routing."""

from __future__ import annotations

import os
from typing import Any, Optional

from github import Github


class GitHubTool:
    """Tool for interacting with GitHub API.

    Provides methods for fetching issues, PRs, commits, and repository info.
    Used by GitHubAgent and can be called directly by the workflow router.
    """

    name = "github_tool"
    description = "Interacts with GitHub API for issues, PRs, and commits"

    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        self.gh = Github(token)
        self.default_repo = os.getenv("GITHUB_DEFAULT_REPO", "")

    def get_issues(self, repo_name: Optional[str] = None, state: str = "open", limit: int = 10) -> list[dict[str, Any]]:
        """Fetch issues from a repository."""
        repo = self.gh.get_repo(repo_name or self.default_repo)
        return [
            {
                "title": issue.title,
                "number": issue.number,
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "assignee": issue.assignee.login if issue.assignee else None,
                "created_at": issue.created_at.isoformat(),
                "url": issue.html_url,
            }
            for issue in repo.get_issues(state=state)
        ][:limit]

    def get_pulls(self, repo_name: Optional[str] = None, state: str = "open", limit: int = 10) -> list[dict[str, Any]]:
        """Fetch pull requests from a repository."""
        repo = self.gh.get_repo(repo_name or self.default_repo)
        return [
            {
                "title": pr.title,
                "number": pr.number,
                "state": pr.state,
                "author": pr.user.login,
                "created_at": pr.created_at.isoformat(),
                "url": pr.html_url,
            }
            for pr in repo.get_pulls(state=state)
        ][:limit]

    def get_commits(self, repo_name: Optional[str] = None, limit: int = 10) -> list[dict[str, str]]:
        """Fetch recent commits from the default branch."""
        repo = self.gh.get_repo(repo_name or self.default_repo)
        return [
            {
                "sha": commit.sha[:7],
                "message": commit.commit.message.split("\n")[0],
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat(),
            }
            for commit in repo.get_commits()[:limit]
        ]

    def get_repo_info(self, repo_name: Optional[str] = None) -> dict[str, Any]:
        """Get basic repository information."""
        repo = self.gh.get_repo(repo_name or self.default_repo)
        return {
            "name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "open_issues": repo.open_issues_count,
            "language": repo.language,
            "url": repo.html_url,
        }
