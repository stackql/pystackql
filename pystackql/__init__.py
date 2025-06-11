# pystackql/__init__.py

"""
PyStackQL - Python wrapper for StackQL

This package provides a Python interface to the StackQL query language
for cloud resource querying.
"""

# Import the core StackQL class
from .core import StackQL

# Import the magic classes for Jupyter integration
from .magic_ext import StackqlMagic, StackqlServerMagic

# Define the public API
__all__ = ['StackQL', 'StackqlMagic', 'StackqlServerMagic']