# tests/conftest.py

"""
Common test setup and fixtures for PyStackQL tests.
"""

import os
import sys
import platform
import time
import pytest
import subprocess
import signal
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import SERVER_ADDRESS, SERVER_PORT, REGISTRY_PULL_HOMEBREW_QUERY

# Global variables to store server process
server_process = None

@pytest.fixture(scope="session", autouse=True)
def setup_stackql():
    """
    Session-wide fixture to download stackql binary and setup server.
    This runs once before all tests.
    """
    print("\nDownloading and setting up stackql binary...")
    stackql = StackQL()
    
    # Check if we're running in GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    if not is_github_actions:
        print("Running tests outside of GitHub Actions, upgrading stackql binary...")
        stackql.upgrade()
    
    # Pull the homebrew provider for provider-specific tests
    print("Pulling homebrew provider for tests...")
    result = stackql.executeStmt(REGISTRY_PULL_HOMEBREW_QUERY)
    print(result)
    
    # Return the StackQL instance for use in tests
    return stackql

@pytest.fixture
def mock_interactive_shell():
    """Create a mock IPython shell for testing."""
    class MockInteractiveShell:
        def __init__(self):
            self.user_ns = {}
            self.register_magics_called = False
            
        def register_magics(self, magic_instance):
            """Mock for registering magics."""
            self.magics = magic_instance
            self.register_magics_called = True

    return MockInteractiveShell()