# pystackql/magic_ext/__init__.py

"""
Jupyter magic extensions for PyStackQL.

This module provides Jupyter magic commands for running StackQL queries
directly in Jupyter notebooks.
"""

from .base import BaseStackqlMagic
from .local import StackqlMagic
from .server import StackqlServerMagic

__all__ = ['BaseStackqlMagic', 'StackqlMagic', 'StackqlServerMagic']