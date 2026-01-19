"""Planes architecture (data, control, governance) for AI OS.

This package provides lightweight primitives that correspond to the
canonical planes described in the technical specification. They are
intentionally minimal and are designed to be extended by concrete
deployments and services.
"""

from .data_plane import DataPlane
from .control_plane import ControlPlane
from .governance_plane import GovernancePlane

__all__ = ["DataPlane", "ControlPlane", "GovernancePlane"]
