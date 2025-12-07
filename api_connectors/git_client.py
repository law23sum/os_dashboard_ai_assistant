"""Git Client - Interfaces with local Git repositories using GitPython."""

import os
from typing import List, Dict, Optional
from git import Repo, GitCommandError


class GitClient:
    """Client for Git repository operations."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.repo = None
        self._initialize_repo()

    def _initialize_repo(self):
        """Initialize or load Git repository."""
        try:
            if os.path.exists(os.path.join(self.repo_path, '.git')):
                self.repo = Repo(self.repo_path)
            else:
                self.repo = Repo.init(self.repo_path)
        except Exception as e:
            raise ValueError(f"Could not initialize Git repository at {self.repo_path}: {e}")

    def get_status(self) -> Dict[str, List[str]]:
        """Get repository status."""
        if not self.repo:
            return {"error": "Repository not initialized"}

        try:
            # Get staged and unstaged changes
            staged = [item.a_path for item in self.repo.index.diff('HEAD', cached=True)]
            unstaged = [item.a_path for item in self.repo.index.diff('HEAD')]

            return {
                "staged": staged,
                "unstaged": unstaged,
                "untracked": self.repo.untracked_files
            }
        except Exception as e:
            return {"error": str(e)}

    def add_files(self, files: List[str] = None):
        """Add files to staging area."""
        if not self.repo:
            raise ValueError("Repository not initialized")

        try:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.index.add('*')
        except GitCommandError as e:
            raise ValueError(f"Could not add files: {e}")

    def commit(self, message: str, author_name: str = None, author_email: str = None):
        """Create a commit."""
        if not self.repo:
            raise ValueError("Repository not initialized")

        try:
            if author_name and author_email:
                self.repo.index.commit(message, author=author_name, author_email=author_email)
            else:
                self.repo.index.commit(message)
        except GitCommandError as e:
            raise ValueError(f"Could not commit: {e}")

    def get_commits(self, limit: int = 10) -> List[Dict]:
        """Get recent commits."""
        if not self.repo:
            return []

        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=limit):
                commits.append({
                    "hash": commit.hexsha,
                    "message": commit.message,
                    "author": commit.author.name,
                    "date": commit.authored_datetime.isoformat(),
                    "stats": {
                        "insertions": commit.stats.total['insertions'],
                        "deletions": commit.stats.total['deletions'],
                        "files": len(commit.stats.files)
                    }
                })
            return commits
        except Exception:
            return []

    def create_branch(self, branch_name: str):
        """Create a new branch."""
        if not self.repo:
            raise ValueError("Repository not initialized")

        try:
            new_branch = self.repo.create_head(branch_name)
            return new_branch
        except GitCommandError as e:
            raise ValueError(f"Could not create branch: {e}")

    def switch_branch(self, branch_name: str):
        """Switch to a branch."""
        if not self.repo:
            raise ValueError("Repository not initialized")

        try:
            branch = self.repo.heads[branch_name]
            branch.checkout()
        except (IndexError, GitCommandError) as e:
            raise ValueError(f"Could not switch to branch {branch_name}: {e}")

    def get_branches(self) -> List[str]:
        """Get list of branches."""
        if not self.repo:
            return []

        return [str(branch) for branch in self.repo.heads]
