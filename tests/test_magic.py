# # tests/test_magic.py

# """
# Non-server magic extension tests for PyStackQL.

# This module tests the Jupyter magic extensions for StackQL in non-server mode.
# """

# import os
# import sys
# import re
# import pytest
# import pandas as pd
# from unittest.mock import MagicMock

# # Add the parent directory to the path so we can import from pystackql
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Add the current directory to the path so we can import test_constants
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# # Import directly from the original modules - this is what notebooks would do
# from pystackql import magic
# from pystackql import StackqlMagic

# from tests.test_constants import (
#     LITERAL_INT_QUERY,
#     REGISTRY_PULL_HOMEBREW_QUERY,
#     registry_pull_resp_pattern,
#     print_test_result
# )

# class TestStackQLMagic:
#     """Tests for the non-server mode magic extension."""
    
#     @pytest.fixture(autouse=True)
#     def setup_method(self, mock_interactive_shell):
#         """Set up the test environment."""
#         self.shell = mock_interactive_shell
        
#         # Load the magic extension
#         magic.load_ipython_extension(self.shell)
        
#         # Create the magic instance
#         self.stackql_magic = StackqlMagic(shell=self.shell)
        
#         # Set up test data
#         self.query = LITERAL_INT_QUERY
#         self.expected_result = pd.DataFrame({"literal_int_value": [1]})
#         self.statement = REGISTRY_PULL_HOMEBREW_QUERY
    
#     def test_line_magic_query(self):
#         """Test line magic with a query."""
#         # Mock the run_query method to return a known DataFrame
#         self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
#         # Execute the magic with our query
#         result = self.stackql_magic.stackql(line=self.query, cell=None)
        
#         # Validate the outcome
#         assert result.equals(self.expected_result), "Result should match expected DataFrame"
#         assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
#         assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
#         print_test_result("Line magic query test", 
#                           result.equals(self.expected_result) and 
#                           'stackql_df' in self.shell.user_ns and 
#                           self.shell.user_ns['stackql_df'].equals(self.expected_result),
#                           False, True)
    
#     def test_cell_magic_query(self):
#         """Test cell magic with a query."""
#         # Mock the run_query method to return a known DataFrame
#         self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
#         # Execute the magic with our query
#         result = self.stackql_magic.stackql(line="", cell=self.query)
        
#         # Validate the outcome
#         assert result.equals(self.expected_result), "Result should match expected DataFrame"
#         assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
#         assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
#         print_test_result("Cell magic query test", 
#                           result.equals(self.expected_result) and 
#                           'stackql_df' in self.shell.user_ns and 
#                           self.shell.user_ns['stackql_df'].equals(self.expected_result),
#                           False, True)
    
#     def test_cell_magic_query_no_display(self):
#         """Test cell magic with a query and --no-display option."""
#         # Mock the run_query method to return a known DataFrame
#         self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
#         # Execute the magic with our query and --no-display option
#         result = self.stackql_magic.stackql(line="--no-display", cell=self.query)
        
#         # Validate the outcome
#         assert result is None, "Result should be None with --no-display option"
#         assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
#         assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
#         print_test_result("Cell magic query test (with --no-display)", 
#                           result is None and 
#                           'stackql_df' in self.shell.user_ns and 
#                           self.shell.user_ns['stackql_df'].equals(self.expected_result),
#                           False, True)

#     def test_cell_magic_query_csv_download(self):
#         """Test cell magic with CSV download functionality."""
#         # Mock the run_query method to return a known DataFrame
#         self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
#         # Mock the _display_with_csv_download method to verify it's called
#         self.stackql_magic._display_with_csv_download = MagicMock()
        
#         # Execute the magic with --csv-download option
#         result = self.stackql_magic.stackql(line="--csv-download", cell=self.query)
        
#         # Validate the outcome
#         assert result.equals(self.expected_result), "Result should match expected DataFrame"
#         assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
#         assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
#         # Verify that _display_with_csv_download was called
#         self.stackql_magic._display_with_csv_download.assert_called_once_with(self.expected_result)
        
#         print_test_result("Cell magic query test with CSV download", 
#                           result.equals(self.expected_result) and 
#                           'stackql_df' in self.shell.user_ns and 
#                           self.stackql_magic._display_with_csv_download.called,
#                           False, True)

#     def test_cell_magic_query_csv_download_with_no_display(self):
#         """Test that --no-display takes precedence over --csv-download."""
#         # Mock the run_query method to return a known DataFrame
#         self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
#         # Mock the _display_with_csv_download method to verify it's not called
#         self.stackql_magic._display_with_csv_download = MagicMock()
        
#         # Execute the magic with both --csv-download and --no-display options
#         result = self.stackql_magic.stackql(line="--csv-download --no-display", cell=self.query)
        
#         # Validate the outcome
#         assert result is None, "Result should be None with --no-display option"
#         assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
#         assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
#         # Verify that _display_with_csv_download was NOT called
#         self.stackql_magic._display_with_csv_download.assert_not_called()
        
#         print_test_result("Cell magic query test with CSV download and no-display", 
#                           result is None and 
#                           'stackql_df' in self.shell.user_ns and 
#                           not self.stackql_magic._display_with_csv_download.called,
#                           False, True)

#     def test_display_with_csv_download_method(self):
#         """Test the _display_with_csv_download method directly."""
#         import base64
#         from unittest.mock import patch
        
#         # Create a test DataFrame
#         test_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        
#         # Mock IPython display functionality
#         with patch('IPython.display.display') as mock_display, \
#              patch('IPython.display.HTML') as mock_html:
            
#             # Call the method
#             self.stackql_magic._display_with_csv_download(test_df)
            
#             # Verify display was called twice (once for DataFrame, once for HTML)
#             assert mock_display.call_count == 2, "Display should be called twice"
            
#             # Verify HTML was called once
#             mock_html.assert_called_once()
            
#             # Check that the HTML call contains download link
#             html_call_args = mock_html.call_args[0][0]
#             assert 'download="stackql_results.csv"' in html_call_args
#             assert 'data:text/csv;base64,' in html_call_args
            
#         print_test_result("_display_with_csv_download method test", 
#                           mock_display.call_count == 2 and mock_html.called,
#                           False, True)

#     def test_display_with_csv_download_error_handling(self):
#         """Test error handling in _display_with_csv_download method."""
#         from unittest.mock import patch
        
#         # Create a mock DataFrame that will raise an exception during to_csv()
#         mock_df = MagicMock()
#         mock_df.to_csv.side_effect = Exception("Test CSV error")
        
#         # Mock IPython display functionality
#         with patch('IPython.display.display') as mock_display, \
#              patch('IPython.display.HTML') as mock_html, \
#              patch('builtins.print') as mock_print:
            
#             # Call the method with the problematic DataFrame
#             self.stackql_magic._display_with_csv_download(mock_df)
            
#             # Verify display was called once (for DataFrame only, not for HTML)
#             mock_display.assert_called_once_with(mock_df)
            
#             # Verify HTML was not called due to error
#             mock_html.assert_not_called()
            
#             # Verify error message was printed
#             mock_print.assert_called_once()
#             error_message = mock_print.call_args[0][0]
#             assert "Error generating CSV download:" in error_message
            
#         print_test_result("_display_with_csv_download error handling test", 
#                           mock_display.called and not mock_html.called and mock_print.called,
#                           False, True)

# def test_magic_extension_loading(mock_interactive_shell):
#     """Test that non-server magic extension can be loaded."""
#     # Test loading non-server magic
#     magic.load_ipython_extension(mock_interactive_shell)
#     assert hasattr(mock_interactive_shell, 'magics'), "Magic should be registered"
#     assert isinstance(mock_interactive_shell.magics, StackqlMagic), "Registered magic should be StackqlMagic"
    
#     print_test_result("Magic extension loading test", 
#                       hasattr(mock_interactive_shell, 'magics') and 
#                       isinstance(mock_interactive_shell.magics, StackqlMagic),
#                       False, True)

# if __name__ == "__main__":
#     pytest.main(["-v", __file__])

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