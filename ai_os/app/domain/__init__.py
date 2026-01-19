"""Core domain model for AI OS.

This package provides light-weight dataclasses and type definitions for
users, tenants, projects, tasks, and related entities described in the
canonical specification.
"""

from .identity import User, Tenant, Role
from .project import Project, Workspace, Task
from .knowledge import CIRDocument, CapsuleRef

__all__ = [
    "User",
    "Tenant",
    "Role",
    "Project",
    "Workspace",
    "Task",
    "CIRDocument",
    "CapsuleRef",
]
