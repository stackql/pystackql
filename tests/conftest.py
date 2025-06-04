# tests/conftest.py

"""
Common test setup and fixtures for PyStackQL tests.
"""

import os
import sys
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

@pytest.fixture(scope="session")
def stackql_server(setup_stackql):
    """
    Session-level fixture to start and stop a StackQL server.
    This runs once for all tests that request it.
    
    This improved version:
    1. Checks if a server is already running before starting one
    2. Uses process groups for better cleanup
    3. Handles errors more gracefully
    """
    global server_process
    
    # Check if server is already running
    print("\nChecking if server is running...")
    ps_output = subprocess.run(
        ["ps", "aux"], 
        capture_output=True, 
        text=True
    ).stdout
    
    if "stackql" in ps_output and f"--pgsrv.port={SERVER_PORT}" in ps_output:
        print("Server is already running")
        # No need to start a server or set server_process
    else:
        # Start the server
        print(f"Starting stackql server on {SERVER_ADDRESS}:{SERVER_PORT}...")
        
        # Get the registry setting from environment variable if available
        registry = os.environ.get('REG', '')
        registry_arg = f"--registry {registry}" if registry else ""
        
        # Build the command
        cmd = f"{setup_stackql.bin_path} srv --pgsrv.address {SERVER_ADDRESS} --pgsrv.port {SERVER_PORT} {registry_arg}"
        
        # Start the server process with process group for better cleanup
        server_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Use process group for cleaner termination
        )
        
        # Wait for server to start
        print("Waiting for server to initialize...")
        time.sleep(5)
        
        # Check if server started successfully
        if server_process.poll() is not None:
            # Process has terminated
            stdout, stderr = server_process.communicate()
            pytest.fail(f"Server failed to start: {stderr.decode()}")
    
    # Yield to run tests
    yield
    
    # Clean up server at the end if we started it
    if server_process and server_process.poll() is None:
        print("\nShutting down stackql server...")
        try:
            # Kill the entire process group
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            server_process.wait(timeout=5)
            print("Server shutdown complete")
        except subprocess.TimeoutExpired:
            print("Server did not terminate gracefully, forcing shutdown...")
            os.killpg(os.getpgid(server_process.pid), signal.SIGKILL)

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