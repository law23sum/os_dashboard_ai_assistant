"""GitHub integration."""

import os
from typing import Dict, List, Optional
import sqlite3

import requests

from .base import BaseIntegration, IntegrationStatus


class GitHubIntegration(BaseIntegration):
    """Integration for GitHub."""

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "GitHub", "github")
        self.token = os.getenv("GITHUB_TOKEN")
        self.username = os.getenv("GITHUB_USERNAME")
        self.repository = os.getenv("GITHUB_REPO")  # format: owner/repo
        self._api_base = "https://api.github.com"

    def authenticate(self) -> bool:
        """Authenticate with GitHub API."""
        if not self.token:
            self.update_status(False, "GITHUB_TOKEN environment variable not set.")
            return False

        if not self.repository:
            self.update_status(False, "GITHUB_REPO not set (expected owner/repo).")
            return False

        try:
            resp = requests.get(
                f"{self._api_base}/user",
                headers=self._headers,
                timeout=8,
            )
            if resp.status_code != 200:
                self.update_status(False, f"Auth failed: {resp.text[:120]}")
                return False

            if not self.username:
                self.username = resp.json().get("login")
        except requests.RequestException as exc:
            self.update_status(
                False, f"Auth check failed: {self._safe_truncate(str(exc))}"
            )
            return False

        self.update_status(True)
        return True

    def sync(self) -> int:
        """Sync GitHub issues, PRs, and commits."""
        if not self.authenticate():
            return 0

        try:
            count = 0
            for issue in self._fetch_issues():
                issue_id = issue.get("id")
                number = issue.get("number")
                if not issue_id or not number:
                    continue

                kind = "pull_request" if "pull_request" in issue else "issue"
                title = issue.get("title") or f"{kind.title()} #{number}"
                self.record_item(
                    external_id=str(issue_id),
                    item_kind=kind,
                    title=title,
                    data={
                        "number": number,
                        "state": issue.get("state"),
                        "author": issue.get("user", {}).get("login"),
                        "created_at": issue.get("created_at"),
                        "updated_at": issue.get("updated_at"),
                        "url": issue.get("html_url"),
                    },
                )
                count += 1

            for commit in self._fetch_commits():
                sha = commit.get("sha")
                if not sha:
                    continue

                commit_info = commit.get("commit", {})
                message = commit_info.get("message", "(No message)").split("\n")[0]
                self.record_item(
                    external_id=sha,
                    item_kind="commit",
                    title=message,
                    data={
                        "author": commit_info.get("author", {}).get("name"),
                        "date": commit_info.get("author", {}).get("date"),
                        "url": commit.get("html_url"),
                    },
                )
                count += 1

            self.update_status(True, item_count=count)
            return count
        except Exception as e:
            self.logger.exception("GitHub sync failed")
            self.update_status(False, self._safe_truncate(str(e)))
            return 0

    def get_status(self) -> IntegrationStatus:
        """Get current status."""
        if not hasattr(self, "_status") or not self._status:
            self._status = IntegrationStatus()
        return self._status

    @property
    def _headers(self) -> Dict[str, str]:
        token = self.token or ""
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def _fetch_issues(self) -> List[Dict]:
        """Fetch open issues and pull requests."""
        resp = requests.get(
            f"{self._api_base}/repos/{self.repository}/issues",
            headers=self._headers,
            params={"state": "open", "per_page": 50},
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"GitHub issues error: {resp.status_code} {resp.text}")

        return resp.json()

    def _fetch_commits(self) -> List[Dict]:
        """Fetch recent commits."""
        resp = requests.get(
            f"{self._api_base}/repos/{self.repository}/commits",
            headers=self._headers,
            params={"per_page": 20},
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"GitHub commits error: {resp.status_code} {resp.text}")

        return resp.json()
