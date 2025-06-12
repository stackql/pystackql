# tests/test_magic_base.py

"""
Base test class for Jupyter magic extensions for PyStackQL.

This module provides a base test class for testing both local and server mode
magic extensions.
"""

import os
import sys
import re
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_constants import (
    LITERAL_INT_QUERY,
    REGISTRY_PULL_HOMEBREW_QUERY,
    registry_pull_resp_pattern,
    print_test_result
)

class BaseStackQLMagicTest:
    """Base class for testing StackQL magic extensions."""

    # Each derived class should define:
    # - magic_module: the module to import
    # - magic_class: the class to use
    # - is_server_mode: True for server mode tests, False for local mode tests
    magic_module = None
    magic_class = None
    is_server_mode = None
    
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_interactive_shell):
        """Set up the test environment."""
        self.shell = mock_interactive_shell
        
        # Load the magic extension
        self.magic_module.load_ipython_extension(self.shell)
        
        # Create the magic instance
        self.stackql_magic = self.magic_class(shell=self.shell)
        
        # Set up test data
        self.query = LITERAL_INT_QUERY
        self.expected_result = pd.DataFrame({"literal_int_value": [1]})
        self.statement = REGISTRY_PULL_HOMEBREW_QUERY
    
    def test_line_magic_query(self):
        """Test line magic with a query."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query
        result = self.stackql_magic.stackql(line=self.query, cell=None)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result(f"Line magic query test{' (server mode)' if self.is_server_mode else ''}", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          self.is_server_mode, True)
    
    def test_cell_magic_query(self):
        """Test cell magic with a query."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query
        result = self.stackql_magic.stackql(line="", cell=self.query)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result(f"Cell magic query test{' (server mode)' if self.is_server_mode else ''}", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          self.is_server_mode, True)
    
    def test_cell_magic_query_no_display(self):
        """Test cell magic with a query and --no-display option."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query and --no-display option
        result = self.stackql_magic.stackql(line="--no-display", cell=self.query)
        
        # Validate the outcome
        assert result is None, "Result should be None with --no-display option"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result(f"Cell magic query test with --no-display{' (server mode)' if self.is_server_mode else ''}", 
                          result is None and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          self.is_server_mode, True)

    def test_cell_magic_query_csv_download(self):
        """Test cell magic with CSV download functionality."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Mock the _display_with_csv_download method to verify it's called
        self.stackql_magic._display_with_csv_download = MagicMock()
        
        # Execute the magic with --csv-download option
        result = self.stackql_magic.stackql(line="--csv-download", cell=self.query)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        # Verify that _display_with_csv_download was called
        self.stackql_magic._display_with_csv_download.assert_called_once_with(self.expected_result)
        
        print_test_result(f"Cell magic query test with CSV download{' (server mode)' if self.is_server_mode else ''}", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.stackql_magic._display_with_csv_download.called,
                          self.is_server_mode, True)

    def test_cell_magic_query_csv_download_with_no_display(self):
        """Test that --no-display takes precedence over --csv-download."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Mock the _display_with_csv_download method to verify it's not called
        self.stackql_magic._display_with_csv_download = MagicMock()
        
        # Execute the magic with both --csv-download and --no-display options
        result = self.stackql_magic.stackql(line="--csv-download --no-display", cell=self.query)
        
        # Validate the outcome
        assert result is None, "Result should be None with --no-display option"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        # Verify that _display_with_csv_download was NOT called
        self.stackql_magic._display_with_csv_download.assert_not_called()
        
        print_test_result(f"Cell magic query test with CSV download and no-display{' (server mode)' if self.is_server_mode else ''}", 
                          result is None and 
                          'stackql_df' in self.shell.user_ns and 
                          not self.stackql_magic._display_with_csv_download.called,
                          self.is_server_mode, True)

    def test_display_with_csv_download_method(self):
        """Test the _display_with_csv_download method directly."""
        import base64
        
        # Create a test DataFrame
        test_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        
        # Mock IPython display functionality
        with patch('IPython.display.display') as mock_display, \
             patch('IPython.display.HTML') as mock_html:
            
            # Call the method
            self.stackql_magic._display_with_csv_download(test_df)
            
            # Verify display was called once (only for HTML, not for DataFrame)
            assert mock_display.call_count == 1, "Display should be called once"
            
            # Verify HTML was called once
            mock_html.assert_called_once()
            
            # Check that the HTML call contains download link
            html_call_args = mock_html.call_args[0][0]
            assert 'download="stackql_results.csv"' in html_call_args
            assert 'data:text/csv;base64,' in html_call_args
            
        print_test_result(f"_display_with_csv_download method test{' (server mode)' if self.is_server_mode else ''}", 
                          mock_display.call_count == 1 and mock_html.called,
                          self.is_server_mode, True)

    # def test_display_with_csv_download_error_handling(self):
    #     """Test error handling in _display_with_csv_download method."""
        
    #     # Create a mock DataFrame that will raise an exception during to_csv()
    #     mock_df = MagicMock()
    #     mock_df.to_csv.side_effect = Exception("Test CSV error")
        
    #     # Mock IPython display functionality
    #     with patch('IPython.display.display') as mock_display, \
    #          patch('IPython.display.HTML') as mock_html, \
    #          patch('builtins.print') as mock_print:
            
    #         # Call the method with the problematic DataFrame
    #         self.stackql_magic._display_with_csv_download(mock_df)
            
    #         # Verify display was not called (we now only print an error message)
    #         mock_display.assert_not_called()
            
    #         # Verify HTML was not called due to error
    #         mock_html.assert_not_called()
            
    #         # Verify error message was printed
    #         mock_print.assert_called_once()
    #         error_message = mock_print.call_args[0][0]
    #         assert "Error generating CSV download:" in error_message
            
    #     print_test_result(f"_display_with_csv_download error handling test{' (server mode)' if self.is_server_mode else ''}", 
    #                       not mock_display.called and not mock_html.called and mock_print.called,
    #                       self.is_server_mode, True)

    def test_display_with_csv_download_error_handling(self):
        """Test error handling in _display_with_csv_download method."""
        
        # Create a mock DataFrame that will raise an exception during to_csv()
        mock_df = MagicMock()
        mock_df.to_csv.side_effect = Exception("Test CSV error")
        
        # Mock IPython display functionality
        with patch('IPython.display.display') as mock_display, \
            patch('IPython.display.HTML') as mock_html, \
            patch('builtins.print') as mock_print:
            
            # Call the method with the problematic DataFrame
            self.stackql_magic._display_with_csv_download(mock_df)
            
            # Verify display was not called in the error case
            mock_display.assert_not_called()
            
            # Verify HTML was not called in the error case
            mock_html.assert_not_called()
            
            # Verify error message was printed
            mock_print.assert_called_once()
            error_message = mock_print.call_args[0][0]
            assert "Error generating CSV download:" in error_message
            
        print_test_result(f"_display_with_csv_download error handling test{' (server mode)' if self.is_server_mode else ''}", 
                        not mock_display.called and not mock_html.called and mock_print.called,
                        self.is_server_mode, True)    