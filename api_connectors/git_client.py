"""
Git API Client

Supports GitHub, GitLab, and other Git hosting services
"""

import asyncio
import json
import subprocess
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
import logging

import aiohttp
import git

from .base import BaseAPIConnector, APIResponse, RateLimit

logger = logging.getLogger(__name__)


class GitClient(BaseAPIConnector):
    """Git API client supporting multiple Git hosting services"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Git configuration
        self.provider = config.get("provider", "github")  # github, gitlab, bitbucket
        self.api_token = config.get("api_token")
        self.username = config.get("username")
        self.base_url = self._get_base_url()

        # Local repositories
        self.local_repos: Dict[str, git.Repo] = {}

        # Headers for API requests
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        if self.provider == "gitlab":
            self.headers["Authorization"] = f"Bearer {self.api_token}"

    def _get_base_url(self) -> str:
        """Get API base URL for the provider"""
        urls = {
            "github": "https://api.github.com",
            "gitlab": "https://gitlab.com/api/v4",
            "bitbucket": "https://api.bitbucket.org/2.0"
        }
        return urls.get(self.provider, "https://api.github.com")

    def _setup_rate_limiter(self) -> 'RateLimiter':
        """Setup rate limiter for Git APIs"""
        # GitHub allows 5,000 requests per hour for authenticated users
        rate_limit = RateLimit(
            requests_per_minute=100,   # Conservative limit
            requests_per_hour=1000,
            requests_per_day=5000,
            burst_limit=20
        )
        return super()._setup_rate_limiter(rate_limit)

    async def authenticate(self) -> bool:
        """Authenticate with Git API"""
        try:
            # Test authentication with a simple API call
            test_response = await self.make_request("GET", "/user")
            if test_response.success:
                self._authenticated = True
                self.logger.info(f"{self.provider.title()} authentication successful")
                return True
            else:
                self.logger.error(f"{self.provider.title()} authentication failed")
                return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    async def test_connection(self) -> APIResponse:
        """Test Git API connection"""
        return await self.make_request("GET", "/user")

    async def _make_http_request(self, method: str, endpoint: str,
                               data: Optional[Dict[str, Any]],
                               headers: Optional[Dict[str, str]],
                               params: Optional[Dict[str, Any]]) -> APIResponse:
        """Make HTTP request to Git API"""
        try:
            url = f"{self.base_url}{endpoint}"

            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)

            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=request_headers, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "PUT":
                    async with session.put(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "PATCH":
                    async with session.patch(url, headers=request_headers, json=data, params=params) as response:
                        return await self._process_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=request_headers, params=params) as response:
                        return await self._process_response(response)
                else:
                    return APIResponse(success=False, error=f"Unsupported method: {method}")

        except Exception as e:
            self.logger.error(f"HTTP request failed: {e}")
            return APIResponse(success=False, error=str(e))

    async def _process_response(self, response: aiohttp.ClientResponse) -> APIResponse:
        """Process HTTP response"""
        try:
            status_code = response.status

            if status_code >= 200 and status_code < 300:
                try:
                    data = await response.json()
                except:
                    data = await response.text()

                return APIResponse(
                    success=True,
                    data=data,
                    status_code=status_code,
                    headers=dict(response.headers)
                )
            else:
                error_text = await response.text()
                return APIResponse(
                    success=False,
                    error=error_text,
                    status_code=status_code,
                    headers=dict(response.headers)
                )

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # Repository Operations

    async def list_repositories(self, user: str = None, org: str = None,
                              visibility: str = "all") -> APIResponse:
        """List repositories for user or organization"""
        try:
            if self.provider == "github":
                if org:
                    endpoint = f"/orgs/{org}/repos"
                    params = {"type": visibility}
                else:
                    endpoint = f"/user/repos"
                    params = {"visibility": visibility}
            elif self.provider == "gitlab":
                if org:
                    endpoint = f"/groups/{org}/projects"
                else:
                    endpoint = "/projects"
                params = {"owned": "true"}

            return await self.make_request("GET", endpoint, params=params)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def get_repository(self, owner: str, repo: str) -> APIResponse:
        """Get repository information"""
        try:
            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}"

            return await self.make_request("GET", endpoint)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def create_repository(self, name: str, description: str = "",
                              private: bool = False) -> APIResponse:
        """Create a new repository"""
        try:
            data = {
                "name": name,
                "description": description,
                "private": private
            }

            if self.provider == "github":
                endpoint = "/user/repos"
            elif self.provider == "gitlab":
                endpoint = "/projects"
                data["visibility"] = "private" if private else "public"

            return await self.make_request("POST", endpoint, data)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # Issue/PR Operations

    async def list_issues(self, owner: str, repo: str, state: str = "open",
                         labels: List[str] = None) -> APIResponse:
        """List repository issues"""
        try:
            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}/issues"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}/issues"

            params = {"state": state}
            if labels:
                params["labels"] = ",".join(labels)

            return await self.make_request("GET", endpoint, params=params)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def create_issue(self, owner: str, repo: str, title: str,
                          body: str = "", labels: List[str] = None) -> APIResponse:
        """Create a new issue"""
        try:
            data = {
                "title": title,
                "body": body
            }

            if labels:
                data["labels"] = labels

            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}/issues"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}/issues"

            return await self.make_request("POST", endpoint, data)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> APIResponse:
        """List pull requests"""
        try:
            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}/pulls"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}/merge_requests"

            params = {"state": state}
            return await self.make_request("GET", endpoint, params=params)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # Commit and File Operations

    async def get_commits(self, owner: str, repo: str, branch: str = "main",
                         since: str = None, until: str = None) -> APIResponse:
        """Get repository commits"""
        try:
            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}/commits"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}/repository/commits"

            params = {"sha": branch}
            if since:
                params["since"] = since
            if until:
                params["until"] = until

            return await self.make_request("GET", endpoint, params=params)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    async def get_file_content(self, owner: str, repo: str, path: str,
                             branch: str = "main") -> APIResponse:
        """Get file content from repository"""
        try:
            if self.provider == "github":
                endpoint = f"/repos/{owner}/{repo}/contents/{path}"
            elif self.provider == "gitlab":
                endpoint = f"/projects/{owner}%2F{repo}/repository/files/{path}"

            params = {"ref": branch}
            return await self.make_request("GET", endpoint, params=params)

        except Exception as e:
            return APIResponse(success=False, error=str(e))

    # Local Git Operations

    def clone_repository(self, remote_url: str, local_path: str) -> bool:
        """Clone a repository locally"""
        try:
            repo = git.Repo.clone_from(remote_url, local_path)
            self.local_repos[local_path] = repo
            self.logger.info(f"Repository cloned to {local_path}")
            return True
        except Exception as e:
            self.logger.error(f"Clone failed: {e}")
            return False

    def open_local_repository(self, local_path: str) -> bool:
        """Open an existing local repository"""
        try:
            repo = git.Repo(local_path)
            self.local_repos[local_path] = repo
            return True
        except Exception as e:
            self.logger.error(f"Failed to open repository: {e}")
            return False

    def get_local_repo_status(self, local_path: str) -> Dict[str, Any]:
        """Get status of local repository"""
        try:
            if local_path not in self.local_repos:
                return {"error": "Repository not opened"}

            repo = self.local_repos[local_path]

            # Get status
            status = {
                "is_dirty": repo.is_dirty(),
                "active_branch": str(repo.active_branch),
                "untracked_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
                "ahead": len(list(repo.iter_commits('HEAD..origin/main'))) if repo.remotes else 0,
                "behind": len(list(repo.iter_commits('origin/main..HEAD'))) if repo.remotes else 0
            }

            return status

        except Exception as e:
            return {"error": str(e)}

    def commit_changes(self, local_path: str, message: str,
                      files: List[str] = None) -> bool:
        """Commit changes to local repository"""
        try:
            if local_path not in self.local_repos:
                return False

            repo = self.local_repos[local_path]

            # Add files
            if files:
                repo.index.add(files)
            else:
                repo.index.add("*")

            # Commit
            repo.index.commit(message)
            self.logger.info(f"Changes committed to {local_path}")
            return True

        except Exception as e:
            self.logger.error(f"Commit failed: {e}")
            return False

    def push_changes(self, local_path: str, remote: str = "origin",
                    branch: str = "main") -> bool:
        """Push changes to remote repository"""
        try:
            if local_path not in self.local_repos:
                return False

            repo = self.local_repos[local_path]
            repo.remote(remote).push(branch)
            self.logger.info(f"Changes pushed to {remote}/{branch}")
            return True

        except Exception as e:
            self.logger.error(f"Push failed: {e}")
            return False

    def pull_changes(self, local_path: str, remote: str = "origin",
                    branch: str = "main") -> bool:
        """Pull changes from remote repository"""
        try:
            if local_path not in self.local_repos:
                return False

            repo = self.local_repos[local_path]
            repo.remote(remote).pull(branch)
            self.logger.info(f"Changes pulled from {remote}/{branch}")
            return True

        except Exception as e:
            self.logger.error(f"Pull failed: {e}")
            return False

    # Git Operations via CLI (fallback)

    def run_git_command(self, local_path: str, command: List[str]) -> Tuple[bool, str]:
        """Run git command via CLI"""
        try:
            if local_path not in self.local_repos:
                return False, "Repository not opened"

            # Change to repository directory
            old_cwd = os.getcwd()
            os.chdir(local_path)

            try:
                result = subprocess.run(
                    ["git"] + command,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, result.stdout
            finally:
                os.chdir(old_cwd)

        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except Exception as e:
            return False, str(e)
