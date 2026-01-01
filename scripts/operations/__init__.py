"""
Operations module for OS Dashboard AI Assistant
Provides unified execution pipeline for install, build, test, execute, and verify operations
"""

from .base import OperationResult, OperationError, OperationStatus, BaseOperation
from .install import InstallOperation
from .build import BuildOperation
from .test import TestOperation
from .launch import LaunchOperation
from .verify import VerifyOperation

__all__ = [
    'OperationResult',
    'OperationError',
    'OperationStatus',
    'BaseOperation',
    'InstallOperation',
    'BuildOperation',
    'TestOperation',
    'LaunchOperation',
    'VerifyOperation',
]

