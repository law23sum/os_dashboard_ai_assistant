"""Identity and tenancy primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Role:
    """Represents a role (permissions bundle) within a tenant."""

    name: str
    description: str = ""


@dataclass
class Tenant:
    """Logical tenant (organisation, workspace, household)."""

    id: str
    name: str
    roles: List[Role]


@dataclass
class User:
    """End user of the OS Dashboard AI Assistant."""

    id: str
    email: str
    display_name: str
    tenant_id: str
    roles: List[Role]

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
