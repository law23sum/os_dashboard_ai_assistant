"""
Git Connector - Version control and repository management
Handles Git operations, commit history, branch management, and code analysis
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import json
from pathlib import Path

from .base import BaseConnector, ConnectorConfig, OperationResult, ResourceRef, ConnectorCapability
from ..cir import (
    CIRDocument, CIRNode, ContentType, SourceSystem, Provenance, 
    DocumentMetadata, GitExtension, CodeBlock
)


class GitConnector(BaseConnector):
    """
    Connector for Git repositories with comprehensive version control operations
    """
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.repo_path = config.settings.get('repo_path', '.')
        self.git_executable = config.settings.get('git_executable', 'git')
        self.repo = None
        self._initialize_git()
    
    def _initialize_git(self):
        """Initialize Git repository connection"""
        try:
            # Check if git is available
            result = subprocess.run([self.git_executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Git executable not found")
            
            # Check if repo_path is a git repository
            repo_path = Path(self.repo_path)
            if not (repo_path / '.git').exists():
                raise Exception(f"Not a git repository: {self.repo_path}")
                
        except Exception as e:
            self.repo = None
    
    async def connect(self) -> OperationResult:
        """Connect to Git repository"""
        try:
            # Verify git repository
            result = await self._run_git_command(['status', '--porcelain'])
            if not result.success:
                return OperationResult(
                    success=False,
                    error="Failed to connect to Git repository",
                    error_code="GIT_CONNECTION_FAILED"
                )
            
            # Get repository info
            repo_info = await self._get_repository_info()
            
            self.is_connected = True
            return OperationResult(
                success=True,
                data={
                    "status": "connected",
                    "repository_info": repo_info,
                    "capabilities": [
                        "commit_history", "branch_management", "file_tracking",
                        "diff_analysis", "blame_tracking", "tag_management"
                    ]
                }
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def disconnect(self) -> OperationResult:
        """Disconnect from Git repository"""
        self.is_connected = False
        return OperationResult(success=True, data={"status": "disconnected"})
    
    async def health_check(self) -> OperationResult:
        """Check Git repository health"""
        try:
            if not self.is_connected:
                return OperationResult(
                    success=False,
                    error="Not connected to Git repository",
                    error_code="NOT_CONNECTED"
                )
            
            # Check repository status
            status_result = await self._run_git_command(['status', '--porcelain'])
            if not status_result.success:
                return OperationResult(
                    success=False,
                    error="Git repository health check failed",
                    error_code="HEALTH_CHECK_FAILED"
                )
            
            self.last_health_check = datetime.utcnow()
            return OperationResult(
                success=True,
                data={
                    "status": "healthy",
                    "last_check": self.last_health_check,
                    "working_directory_clean": len(status_result.data.strip()) == 0
                }
            )
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def list_resources(self, resource_type: str = None, 
                           filters: Dict[str, Any] = None) -> OperationResult:
        """List Git resources (commits, branches, files, tags)"""
        try:
            resources = []
            
            if not resource_type or resource_type == "commits":
                commits = await self._list_commits(filters)
                resources.extend(commits)
            
            if not resource_type or resource_type == "branches":
                branches = await self._list_branches(filters)
                resources.extend(branches)
            
            if not resource_type or resource_type == "files":
                files = await self._list_tracked_files(filters)
                resources.extend(files)
            
            if not resource_type or resource_type == "tags":
                tags = await self._list_tags(filters)
                resources.extend(tags)
            
            return OperationResult(success=True, data=resources)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def get_resource_metadata(self, resource_id: str) -> OperationResult:
        """Get detailed metadata for Git resource"""
        try:
            # Determine resource type from ID format
            if resource_id.startswith('commit:'):
                commit_hash = resource_id[7:]
                metadata = await self._get_commit_metadata(commit_hash)
            elif resource_id.startswith('branch:'):
                branch_name = resource_id[7:]
                metadata = await self._get_branch_metadata(branch_name)
            elif resource_id.startswith('file:'):
                file_path = resource_id[5:]
                metadata = await self._get_file_metadata(file_path)
            elif resource_id.startswith('tag:'):
                tag_name = resource_id[4:]
                metadata = await self._get_tag_metadata(tag_name)
            else:
                return OperationResult(
                    success=False,
                    error="Invalid resource ID format",
                    error_code="INVALID_RESOURCE_ID"
                )
            
            return OperationResult(success=True, data=metadata)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def read_resource(self, resource_id: str, 
                          options: Dict[str, Any] = None) -> OperationResult:
        """Read Git resource and convert to CIR"""
        try:
            if resource_id.startswith('commit:'):
                commit_hash = resource_id[7:]
                cir_document = await self._read_commit_as_cir(commit_hash, options)
            elif resource_id.startswith('file:'):
                file_path = resource_id[5:]
                cir_document = await self._read_file_history_as_cir(file_path, options)
            elif resource_id.startswith('branch:'):
                branch_name = resource_id[7:]
                cir_document = await self._read_branch_as_cir(branch_name, options)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not readable",
                    error_code="RESOURCE_NOT_READABLE"
                )
            
            return OperationResult(success=True, data=cir_document)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def write_resource(self, resource_id: str, cir_content: CIRDocument,
                           options: Dict[str, Any] = None) -> OperationResult:
        """Write changes to Git (commit, create branch, etc.)"""
        try:
            if resource_id.startswith('commit:'):
                # Create new commit
                result = await self._create_commit_from_cir(cir_content, options)
            elif resource_id.startswith('branch:'):
                # Create or update branch
                branch_name = resource_id[7:]
                result = await self._create_or_update_branch(branch_name, cir_content, options)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not writable",
                    error_code="RESOURCE_NOT_WRITABLE"
                )
            
            return OperationResult(success=True, data=result)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def create_resource(self, resource_type: str, cir_content: CIRDocument,
                            options: Dict[str, Any] = None) -> OperationResult:
        """Create new Git resource"""
        try:
            if resource_type == "commit":
                result = await self._create_commit_from_cir(cir_content, options)
            elif resource_type == "branch":
                branch_name = options.get('branch_name') or cir_content.title
                result = await self._create_branch(branch_name, options)
            elif resource_type == "tag":
                tag_name = options.get('tag_name') or cir_content.title
                result = await self._create_tag(tag_name, options)
            else:
                return OperationResult(
                    success=False,
                    error=f"Unsupported resource type: {resource_type}",
                    error_code="UNSUPPORTED_TYPE"
                )
            
            return OperationResult(success=True, data=result)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def delete_resource(self, resource_id: str) -> OperationResult:
        """Delete Git resource"""
        try:
            if resource_id.startswith('branch:'):
                branch_name = resource_id[7:]
                result = await self._delete_branch(branch_name)
            elif resource_id.startswith('tag:'):
                tag_name = resource_id[4:]
                result = await self._delete_tag(tag_name)
            else:
                return OperationResult(
                    success=False,
                    error="Resource type not deletable",
                    error_code="RESOURCE_NOT_DELETABLE"
                )
            
            return OperationResult(success=True, data=result)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def search(self, query: str, filters: Dict[str, Any] = None,
                    options: Dict[str, Any] = None) -> OperationResult:
        """Search Git history and content"""
        try:
            search_results = []
            
            # Search commit messages
            commit_results = await self._search_commits(query, filters)
            search_results.extend(commit_results)
            
            # Search file content
            if options and options.get('search_content', True):
                content_results = await self._search_file_content(query, filters)
                search_results.extend(content_results)
            
            # Sort by relevance/date
            search_results.sort(key=lambda x: x.metadata.get('commit_date', datetime.min), reverse=True)
            
            # Limit results
            limit = options.get('limit', 50) if options else 50
            search_results = search_results[:limit]
            
            return OperationResult(success=True, data=search_results)
            
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    # Private helper methods
    async def _run_git_command(self, args: List[str]) -> OperationResult:
        """Run git command and return result"""
        try:
            cmd = [self.git_executable] + args
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return OperationResult(success=True, data=result.stdout)
            else:
                return OperationResult(
                    success=False,
                    error=result.stderr,
                    error_code="GIT_COMMAND_FAILED"
                )
                
        except subprocess.TimeoutExpired:
            return OperationResult(
                success=False,
                error="Git command timed out",
                error_code="COMMAND_TIMEOUT"
            )
        except Exception as e:
            return OperationResult(success=False, error=str(e))
    
    async def _get_repository_info(self) -> Dict[str, Any]:
        """Get basic repository information"""
        info = {}
        
        # Get current branch
        branch_result = await self._run_git_command(['branch', '--show-current'])
        if branch_result.success:
            info['current_branch'] = branch_result.data.strip()
        
        # Get remote URL
        remote_result = await self._run_git_command(['remote', 'get-url', 'origin'])
        if remote_result.success:
            info['remote_url'] = remote_result.data.strip()
        
        # Get commit count
        count_result = await self._run_git_command(['rev-list', '--count', 'HEAD'])
        if count_result.success:
            info['commit_count'] = int(count_result.data.strip())
        
        # Get repository status
        status_result = await self._run_git_command(['status', '--porcelain'])
        if status_result.success:
            info['has_uncommitted_changes'] = len(status_result.data.strip()) > 0
        
        return info
    
    async def _list_commits(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """List repository commits"""
        commits = []
        
        # Build git log command
        args = ['log', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso']
        
        if filters:
            if 'since' in filters:
                args.extend(['--since', filters['since']])
            if 'until' in filters:
                args.extend(['--until', filters['until']])
            if 'author' in filters:
                args.extend(['--author', filters['author']])
            if 'max_count' in filters:
                args.extend(['-n', str(filters['max_count'])])
        
        result = await self._run_git_command(args)
        if not result.success:
            return commits
        
        for line in result.data.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|', 4)
            if len(parts) == 5:
                commit_hash, author_name, author_email, date_str, message = parts
                
                commits.append(ResourceRef(
                    id=f"commit:{commit_hash}",
                    name=message[:50] + "..." if len(message) > 50 else message,
                    path=commit_hash,
                    resource_type="commit",
                    created_at=datetime.fromisoformat(date_str.replace(' ', 'T')),
                    metadata={
                        "commit_hash": commit_hash,
                        "author_name": author_name,
                        "author_email": author_email,
                        "message": message,
                        "short_hash": commit_hash[:8]
                    }
                ))
        
        return commits
    
    async def _list_branches(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """List repository branches"""
        branches = []
        
        # List all branches
        result = await self._run_git_command(['branch', '-a', '--format=%(refname:short)|%(committerdate:iso)|%(subject)'])
        if not result.success:
            return branches
        
        for line in result.data.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|', 2)
            if len(parts) >= 2:
                branch_name = parts[0].strip()
                date_str = parts[1].strip()
                subject = parts[2] if len(parts) > 2 else ""
                
                # Skip remote tracking branches if not requested
                if branch_name.startswith('origin/') and not (filters and filters.get('include_remote')):
                    continue
                
                branches.append(ResourceRef(
                    id=f"branch:{branch_name}",
                    name=branch_name,
                    path=branch_name,
                    resource_type="branch",
                    modified_at=datetime.fromisoformat(date_str.replace(' ', 'T')),
                    metadata={
                        "branch_name": branch_name,
                        "last_commit_subject": subject,
                        "is_remote": branch_name.startswith('origin/')
                    }
                ))
        
        return branches
    
    async def _list_tracked_files(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """List tracked files in repository"""
        files = []
        
        # List all tracked files
        result = await self._run_git_command(['ls-files'])
        if not result.success:
            return files
        
        for file_path in result.data.strip().split('\n'):
            if not file_path:
                continue
            
            # Get file info
            file_info = await self._get_file_info(file_path)
            
            files.append(ResourceRef(
                id=f"file:{file_path}",
                name=Path(file_path).name,
                path=file_path,
                resource_type="file",
                modified_at=file_info.get('last_modified'),
                metadata=file_info
            ))
        
        return files
    
    async def _list_tags(self, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """List repository tags"""
        tags = []
        
        result = await self._run_git_command(['tag', '-l', '--format=%(refname:short)|%(creatordate:iso)|%(subject)'])
        if not result.success:
            return tags
        
        for line in result.data.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('|', 2)
            if len(parts) >= 1:
                tag_name = parts[0].strip()
                date_str = parts[1].strip() if len(parts) > 1 else ""
                subject = parts[2] if len(parts) > 2 else ""
                
                created_at = None
                if date_str:
                    try:
                        created_at = datetime.fromisoformat(date_str.replace(' ', 'T'))
                    except:
                        pass
                
                tags.append(ResourceRef(
                    id=f"tag:{tag_name}",
                    name=tag_name,
                    path=tag_name,
                    resource_type="tag",
                    created_at=created_at,
                    metadata={
                        "tag_name": tag_name,
                        "subject": subject
                    }
                ))
        
        return tags
    
    async def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        info = {"file_path": file_path}
        
        # Get last commit for file
        result = await self._run_git_command([
            'log', '-1', '--pretty=format:%H|%an|%ad|%s', '--date=iso', '--', file_path
        ])
        
        if result.success and result.data.strip():
            parts = result.data.strip().split('|', 3)
            if len(parts) == 4:
                info.update({
                    "last_commit_hash": parts[0],
                    "last_author": parts[1],
                    "last_modified": datetime.fromisoformat(parts[2].replace(' ', 'T')),
                    "last_commit_message": parts[3]
                })
        
        return info
    
    async def _read_commit_as_cir(self, commit_hash: str, options: Dict[str, Any] = None) -> CIRDocument:
        """Read commit details as CIR document"""
        # Get commit details
        result = await self._run_git_command([
            'show', '--pretty=format:%H|%an|%ae|%ad|%s|%b', '--name-status', commit_hash
        ])
        
        if not result.success:
            raise Exception(f"Failed to read commit {commit_hash}")
        
        lines = result.data.strip().split('\n')
        commit_info = lines[0].split('|', 5)
        
        if len(commit_info) < 5:
            raise Exception("Invalid commit format")
        
        commit_hash, author_name, author_email, date_str, subject = commit_info[:5]
        body = commit_info[5] if len(commit_info) > 5 else ""
        
        # Create CIR document
        cir_document = CIRDocument(
            title=f"Commit: {subject}",
            document_type=SourceSystem.GIT,
            root=CIRNode(
                type=ContentType.DOCUMENT,
                title=subject,
                text=body,
                provenance=[Provenance(
                    source_system=SourceSystem.GIT,
                    source_id=commit_hash,
                    extraction_method="git_show"
                )]
            ),
            metadata=DocumentMetadata(
                source_format="git_commit",
                source_path=commit_hash,
                author=author_name,
                created_at=datetime.fromisoformat(date_str.replace(' ', 'T'))
            )
        )
        
        # Add Git extension
        git_extension = GitExtension(
            commit_hash=commit_hash,
            author_name=author_name,
            author_email=author_email,
            commit_message=subject,
            commit_body=body
        )
        
        # Process changed files
        file_changes = []
        for line in lines[1:]:
            if not line or line.startswith(' '):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                status = parts[0]
                file_path = parts[1]
                
                # Get file diff
                diff_result = await self._run_git_command(['show', commit_hash, '--', file_path])
                diff_content = diff_result.data if diff_result.success else ""
                
                file_node = CIRNode(
                    type=ContentType.CODE,
                    title=f"{status}: {file_path}",
                    code=CodeBlock(
                        content=diff_content,
                        language=self._detect_language(file_path),
                        file_path=file_path
                    ),
                    provenance=[Provenance(
                        source_system=SourceSystem.GIT,
                        source_id=f"{commit_hash}:{file_path}",
                        extraction_method="git_diff"
                    )],
                    metadata={
                        "change_type": status,
                        "file_path": file_path
                    }
                )
                
                cir_document.root.children.append(file_node)
                file_changes.append({"status": status, "path": file_path})
        
        git_extension.changed_files = file_changes
        cir_document.extensions = {"git": git_extension}
        
        return cir_document
    
    async def _search_commits(self, query: str, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """Search commit messages and content"""
        results = []
        
        # Search commit messages
        args = ['log', '--grep', query, '--pretty=format:%H|%an|%ad|%s', '--date=iso']
        
        if filters:
            if 'since' in filters:
                args.extend(['--since', filters['since']])
            if 'author' in filters:
                args.extend(['--author', filters['author']])
        
        result = await self._run_git_command(args)
        if result.success:
            for line in result.data.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commit_hash, author, date_str, message = parts
                    
                    results.append(ResourceRef(
                        id=f"commit:{commit_hash}",
                        name=message,
                        path=commit_hash,
                        resource_type="commit",
                        created_at=datetime.fromisoformat(date_str.replace(' ', 'T')),
                        metadata={
                            "commit_hash": commit_hash,
                            "author": author,
                            "message": message,
                            "search_type": "commit_message",
                            "search_query": query
                        }
                    ))
        
        return results
    
    async def _search_file_content(self, query: str, filters: Dict[str, Any] = None) -> List[ResourceRef]:
        """Search file content in Git history"""
        results = []
        
        # Search file content
        args = ['log', '-S', query, '--pretty=format:%H|%an|%ad|%s', '--date=iso']
        
        result = await self._run_git_command(args)
        if result.success:
            for line in result.data.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commit_hash, author, date_str, message = parts
                    
                    results.append(ResourceRef(
                        id=f"commit:{commit_hash}",
                        name=f"Content change: {message}",
                        path=commit_hash,
                        resource_type="commit",
                        created_at=datetime.fromisoformat(date_str.replace(' ', 'T')),
                        metadata={
                            "commit_hash": commit_hash,
                            "author": author,
                            "message": message,
                            "search_type": "file_content",
                            "search_query": query
                        }
                    ))
        
        return results
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        ext = Path(file_path).suffix.lower()
        return extension_map.get(ext, 'text')
