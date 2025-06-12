# tests/test_magic.py

"""
Non-server magic extension tests for PyStackQL.

This module tests the Jupyter magic extensions for StackQL in non-server mode.
"""

import os
import sys
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the base test class
from tests.test_magic_base import BaseStackQLMagicTest

# Import directly from the original modules - this is what notebooks would do
from pystackql import magic
from pystackql import StackqlMagic

from tests.test_constants import print_test_result

class TestStackQLMagic(BaseStackQLMagicTest):
    """Tests for the non-server mode magic extension."""
    
    # Set the class attributes for the base test class
    magic_module = magic
    magic_class = StackqlMagic
    is_server_mode = False

def test_magic_extension_loading(mock_interactive_shell):
    """Test that non-server magic extension can be loaded."""
    # Test loading non-server magic
    magic.load_ipython_extension(mock_interactive_shell)
    assert hasattr(mock_interactive_shell, 'magics'), "Magic should be registered"
    assert isinstance(mock_interactive_shell.magics, StackqlMagic), "Registered magic should be StackqlMagic"
    
    print_test_result("Magic extension loading test", 
                      hasattr(mock_interactive_shell, 'magics') and 
                      isinstance(mock_interactive_shell.magics, StackqlMagic),
                      False, True)

if __name__ == "__main__":
    pytest.main(["-v", __file__])