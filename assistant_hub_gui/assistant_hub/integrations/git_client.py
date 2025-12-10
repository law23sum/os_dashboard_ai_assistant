"""
Git API Client for GitHub and local Git operations
"""
import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

import git
from github import Github
from github.GithubException import GithubException

from config import get_api_config
from ..logging_config import setup_logger


class GitClient:
    """Git client for GitHub and local Git operations"""

    def __init__(self):
        self.config = get_api_config()
        self.logger = setup_logger("GitClient")
        self.github_client = None
        self.local_repos = {}

    async def initialize(self) -> bool:
        """Initialize Git client"""
        try:
            # Initialize GitHub client
            if self.config.github_token:
                self.github_client = Github(self.config.github_token)

                # Test connection
                user = self.github_client.get_user()
                self.logger.info(f"Connected to GitHub as: {user.login}")

            self.logger.info("Git client initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize Git client: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if GitHub API is accessible"""
        try:
            if self.github_client:
                user = self.github_client.get_user()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Git health check failed: {e}")
            return False

    # GitHub Operations
    async def get_repositories(self, username: str = None) -> List[Dict[str, Any]]:
        """Get list of repositories"""
        try:
            if username:
                user = self.github_client.get_user(username)
                repos = user.get_repos()
            else:
                repos = self.github_client.get_user().get_repos()

            return [
                {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "ssh_url": repo.ssh_url,
                    "private": repo.private,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                }
                for repo in repos
            ]

        except Exception as e:
            self.logger.error(f"Failed to get repositories: {e}")
            raise

    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True,
    ) -> Dict[str, Any]:
        """Create a new repository"""
        try:
            user = self.github_client.get_user()
            repo = user.create_repo(
                name=name, description=description, private=private, auto_init=auto_init
            )

            return {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
            }

        except Exception as e:
            self.logger.error(f"Failed to create repository: {e}")
            raise

    async def get_repository_contents(
        self, repo_name: str, path: str = ""
    ) -> List[Dict[str, Any]]:
        """Get repository contents"""
        try:
            repo = self.github_client.get_repo(repo_name)
            contents = repo.get_contents(path)

            if not isinstance(contents, list):
                contents = [contents]

            return [
                {
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "size": content.size,
                    "download_url": content.download_url,
                    "html_url": content.html_url,
                }
                for content in contents
            ]

        except Exception as e:
            self.logger.error(f"Failed to get repository contents: {e}")
            raise

    async def create_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Create a file in repository"""
        try:
            repo = self.github_client.get_repo(repo_name)
            result = repo.create_file(
                path=file_path, message=commit_message, content=content, branch=branch
            )

            return {
                "commit_sha": result["commit"].sha,
                "content_sha": result["content"].sha,
                "html_url": result["content"].html_url,
            }

        except Exception as e:
            self.logger.error(f"Failed to create file: {e}")
            raise

    async def update_file(
        self,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Update a file in repository"""
        try:
            repo = self.github_client.get_repo(repo_name)

            # Get current file to get its SHA
            current_file = repo.get_contents(file_path, ref=branch)

            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=current_file.sha,
                branch=branch,
            )

            return {
                "commit_sha": result["commit"].sha,
                "content_sha": result["content"].sha,
                "html_url": result["content"].html_url,
            }

        except Exception as e:
            self.logger.error(f"Failed to update file: {e}")
            raise

    async def create_pull_request(
        self, repo_name: str, title: str, body: str, head: str, base: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            repo = self.github_client.get_repo(repo_name)
            pr = repo.create_pull(title=title, body=body, head=head, base=base)

            return {
                "id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "state": pr.state,
            }

        except Exception as e:
            self.logger.error(f"Failed to create pull request: {e}")
            raise

    async def get_issues(
        self, repo_name: str, state: str = "open"
    ) -> List[Dict[str, Any]]:
        """Get repository issues"""
        try:
            repo = self.github_client.get_repo(repo_name)
            issues = repo.get_issues(state=state)

            return [
                {
                    "id": issue.id,
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "url": issue.html_url,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "labels": [label.name for label in issue.labels],
                    "assignees": [assignee.login for assignee in issue.assignees],
                }
                for issue in issues
            ]

        except Exception as e:
            self.logger.error(f"Failed to get issues: {e}")
            raise

    async def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str = "",
        labels: List[str] = None,
        assignees: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a new issue"""
        try:
            repo = self.github_client.get_repo(repo_name)
            issue = repo.create_issue(
                title=title, body=body, labels=labels or [], assignees=assignees or []
            )

            return {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
            }

        except Exception as e:
            self.logger.error(f"Failed to create issue: {e}")
            raise

    # Local Git Operations
    async def clone_repository(self, repo_url: str, local_path: str) -> Dict[str, Any]:
        """Clone a repository locally"""
        try:
            repo = git.Repo.clone_from(repo_url, local_path)
            self.local_repos[local_path] = repo

            return {
                "path": local_path,
                "url": repo_url,
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha,
            }

        except Exception as e:
            self.logger.error(f"Failed to clone repository: {e}")
            raise

    async def commit_changes(
        self, repo_path: str, message: str, files: List[str] = None
    ) -> Dict[str, Any]:
        """Commit changes to local repository"""
        try:
            if repo_path not in self.local_repos:
                self.local_repos[repo_path] = git.Repo(repo_path)

            repo = self.local_repos[repo_path]

            # Add files
            if files:
                repo.index.add(files)
            else:
                repo.git.add(A=True)  # Add all changes

            # Commit
            commit = repo.index.commit(message)

            return {
                "commit_sha": commit.hexsha,
                "message": commit.message,
                "author": str(commit.author),
                "committed_date": commit.committed_date,
            }

        except Exception as e:
            self.logger.error(f"Failed to commit changes: {e}")
            raise

    async def push_changes(
        self, repo_path: str, remote: str = "origin", branch: str = None
    ) -> bool:
        """Push changes to remote repository"""
        try:
            if repo_path not in self.local_repos:
                self.local_repos[repo_path] = git.Repo(repo_path)

            repo = self.local_repos[repo_path]

            if not branch:
                branch = repo.active_branch.name

            origin = repo.remote(remote)
            origin.push(branch)

            return True

        except Exception as e:
            self.logger.error(f"Failed to push changes: {e}")
            raise

    async def pull_changes(
        self, repo_path: str, remote: str = "origin", branch: str = None
    ) -> Dict[str, Any]:
        """Pull changes from remote repository"""
        try:
            if repo_path not in self.local_repos:
                self.local_repos[repo_path] = git.Repo(repo_path)

            repo = self.local_repos[repo_path]

            if not branch:
                branch = repo.active_branch.name

            origin = repo.remote(remote)
            pull_info = origin.pull(branch)[0]

            return {
                "commit_sha": pull_info.commit.hexsha,
                "message": pull_info.commit.message,
                "flags": pull_info.flags,
            }

        except Exception as e:
            self.logger.error(f"Failed to pull changes: {e}")
            raise

    async def get_repository_status(self, repo_path: str) -> Dict[str, Any]:
        """Get repository status"""
        try:
            if repo_path not in self.local_repos:
                self.local_repos[repo_path] = git.Repo(repo_path)

            repo = self.local_repos[repo_path]

            return {
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
                "untracked_files": repo.untracked_files,
                "is_dirty": repo.is_dirty(),
            }

        except Exception as e:
            self.logger.error(f"Failed to get repository status: {e}")
            raise

    # Unified operation method
    async def execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute Git operation"""
        operations = {
            "get_repos": self.get_repositories,
            "create_repo": self.create_repository,
            "clone": self.clone_repository,
            "commit": self.commit_changes,
            "push": self.push_changes,
            "pull": self.pull_changes,
            "status": self.get_repository_status,
            "create_issue": self.create_issue,
            "get_issues": self.get_issues,
            "create_pr": self.create_pull_request,
            "create_file": self.create_file,
            "update_file": self.update_file,
        }

        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")

        return await operations[operation](**kwargs)

    async def shutdown(self):
        """Shutdown Git client"""
        self.local_repos.clear()
        self.github_client = None
        self.logger.info("Git client shutdown complete")
