# tests/test_constants.py

"""
Test constants and helper functions for PyStackQL tests.
"""

import os
import re
import sys
import time
import platform
import subprocess
from termcolor import colored
import pandas as pd

# Server connection settings
SERVER_PORT = 5466
SERVER_ADDRESS = "127.0.0.1"

# Expected properties and patterns for validation
EXPECTED_PROPERTIES = [
    "bin_path", "params", 
    "output", "platform", "server_mode", "sha", "version",
    "package_version"  # Modified: removed "download_dir" as it's no longer exposed
]

EXPECTED_VERSION_PATTERN = r'^v?(\d+\.\d+\.\d+)$'
EXPECTED_PACKAGE_VERSION_PATTERN = r'^(\d+\.\d+\.\d+)$'
EXPECTED_PLATFORM_PATTERN = r'^(Windows|Linux|Darwin) (\w+) \(([^)]+)\), Python (\d+\.\d+\.\d+)$'

# Get custom download directory based on platform
def get_custom_download_dir():
    """Return a platform-specific custom download directory."""
    custom_download_dirs = {
        'windows': 'C:\\temp',
        'darwin': '/tmp',
        'linux': '/tmp'
    }
    return custom_download_dirs.get(platform.system().lower(), '/tmp')

# Basic test queries that don't require authentication
LITERAL_INT_QUERY = "SELECT 1 as literal_int_value"
LITERAL_FLOAT_QUERY = "SELECT 1.001 as literal_float_value"
LITERAL_STRING_QUERY = "SELECT 'test' as literal_string_value"
EXPRESSION_TRUE_QUERY = "SELECT 1=1 as expression"
EXPRESSION_FALSE_QUERY = "SELECT 1=0 as expression"
EMPTY_RESULT_QUERY = "SELECT 1 WHERE 1=0"
JSON_EXTRACT_QUERY = """
SELECT
    json_extract('{"Key":"StackName","Value":"aws-stack"}', '$.Key') as key,
    json_extract('{"Key":"StackName","Value":"aws-stack"}', '$.Value') as value
"""

# Homebrew provider queries (no authentication required)
HOMEBREW_FORMULA_QUERY = "SELECT name, full_name, tap FROM homebrew.formula.formula WHERE formula_name = 'stackql'"
HOMEBREW_METRICS_QUERY = "SELECT * FROM homebrew.formula.vw_usage_metrics WHERE formula_name = 'stackql'"

# Registry pull queries
REGISTRY_PULL_HOMEBREW_QUERY = "REGISTRY PULL homebrew"

# Async test queries
ASYNC_QUERIES = [
    "SELECT * FROM homebrew.formula.vw_usage_metrics WHERE formula_name = 'stackql'",
    "SELECT * FROM homebrew.formula.vw_usage_metrics WHERE formula_name = 'terraform'"
]

# Pattern to match registry pull response
def registry_pull_resp_pattern(provider):
    """Returns a regex pattern to match a successful registry pull message."""
    return r"%s provider, version 'v\d+\.\d+\.\d+' successfully installed\s*" % provider

# Test result printer
def print_test_result(test_name, condition=True, server_mode=False, is_ipython=False, is_async=False):
    """Prints a formatted test result.
    
    Args:
        test_name: Name or description of the test
        condition: Whether the test passed (True) or failed (False)
        server_mode: Whether the test was run in server mode
        is_ipython: Whether the test involved IPython magic
        is_async: Whether the test involved async functionality
    """
    status_header = colored("[PASSED] ", 'green') if condition else colored("[FAILED] ", 'red')
    headers = [status_header]
    
    if server_mode:
        headers.append(colored("[SERVER MODE]", 'yellow'))
    if is_ipython:
        headers.append(colored("[MAGIC EXT]", 'blue'))
    if is_async:
        headers.append(colored("[ASYNC]", 'magenta'))
    
    headers.append(test_name)
    message = " ".join(headers)
    
    print("\n" + message)

# Decorators for test setup
def pystackql_test_setup(**kwargs):
    """Decorator to set up a StackQL instance with specified parameters."""
    def decorator(func):
        def wrapper(self, *args):
            try:
                del self.stackql
            except AttributeError:
                pass
            self.stackql = self.StackQL(**kwargs)
            func(self, *args)
        return wrapper
    return decorator

def async_test_decorator(func):
    """Decorator to run async tests with asyncio."""
    def wrapper(*args, **kwargs):
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return asyncio.run(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    return wrapper