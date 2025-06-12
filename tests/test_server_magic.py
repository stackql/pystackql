# tests/test_server_magic.py

"""
Server-mode magic extension tests for PyStackQL.

This module tests the Jupyter magic extensions for StackQL in server mode.
"""

import os
import sys
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the base test class
from tests.test_magic_base import BaseStackQLMagicTest

# Import directly from the original modules - this is what notebooks would do
from pystackql import magics
from pystackql import StackqlServerMagic

from tests.test_constants import print_test_result

class TestStackQLServerMagic(BaseStackQLMagicTest):
    """Tests for the server mode magic extension."""
    
    # Set the class attributes for the base test class
    magic_module = magics
    magic_class = StackqlServerMagic
    is_server_mode = True

def test_server_magic_extension_loading(mock_interactive_shell):
    """Test that server magic extension can be loaded."""
    # Test loading server magic
    magics.load_ipython_extension(mock_interactive_shell)
    assert hasattr(mock_interactive_shell, 'magics'), "Magic should be registered"
    assert isinstance(mock_interactive_shell.magics, StackqlServerMagic), "Registered magic should be StackqlServerMagic"
    
    print_test_result("Server magic extension loading test", 
                      hasattr(mock_interactive_shell, 'magics') and 
                      isinstance(mock_interactive_shell.magics, StackqlServerMagic),
                      True, True)

if __name__ == "__main__":
    pytest.main(["-v", __file__])