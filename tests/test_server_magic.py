"""
Server-mode magic extension tests for PyStackQL.

This module tests the Jupyter magic extensions for StackQL in server mode.
"""

import os
import sys
import re
import pytest
import pandas as pd
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import directly from the original modules - this is what notebooks would do
from pystackql import magics
from pystackql import StackqlServerMagic

from tests.test_constants import (
    LITERAL_INT_QUERY,
    REGISTRY_PULL_HOMEBREW_QUERY,
    registry_pull_resp_pattern,
    print_test_result
)

class TestStackQLServerMagic:
    """Tests for the server mode magic extension."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_interactive_shell):
        """Set up the test environment."""
        self.shell = mock_interactive_shell
        
        # Load the magic extension
        magics.load_ipython_extension(self.shell)
        
        # Create the magic instance
        self.stackql_magic = StackqlServerMagic(shell=self.shell)
        
        # Set up test data
        self.query = LITERAL_INT_QUERY
        self.expected_result = pd.DataFrame({"literal_int_value": [1]})
        self.statement = REGISTRY_PULL_HOMEBREW_QUERY
    
    def test_line_magic_query(self):
        """Test line magic with a query in server mode."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query
        result = self.stackql_magic.stackql(line=self.query, cell=None)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result("Line magic query test (server mode)", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          True, True)
    
    def test_cell_magic_query(self):
        """Test cell magic with a query in server mode."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query
        result = self.stackql_magic.stackql(line="", cell=self.query)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result("Cell magic query test (server mode)", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          True, True)
    
    def test_cell_magic_query_no_display(self):
        """Test cell magic with a query and --no-display option in server mode."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Execute the magic with our query and --no-display option
        result = self.stackql_magic.stackql(line="--no-display", cell=self.query)
        
        # Validate the outcome
        assert result is None, "Result should be None with --no-display option"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        print_test_result("Cell magic query test with --no-display (server mode)", 
                          result is None and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result),
                          True, True)

    def test_cell_magic_query_csv_download(self):
        """Test cell magic with a query and --csv-download option in server mode."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Mock the _display_with_csv_download method to track if it was called
        self.stackql_magic._display_with_csv_download = MagicMock()
        
        # Execute the magic with our query and --csv-download option
        result = self.stackql_magic.stackql(line="--csv-download", cell=self.query)
        
        # Validate the outcome
        assert result.equals(self.expected_result), "Result should match expected DataFrame"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        # Verify that _display_with_csv_download was called
        self.stackql_magic._display_with_csv_download.assert_called_once_with(self.expected_result)
        
        print_test_result("Cell magic query test (with --csv-download, server mode)", 
                          result.equals(self.expected_result) and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result) and
                          self.stackql_magic._display_with_csv_download.called,
                          True, True)

    def test_cell_magic_query_csv_download_with_no_display(self):
        """Test cell magic with both --csv-download and --no-display options in server mode."""
        # Mock the run_query method to return a known DataFrame
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        
        # Mock the _display_with_csv_download method to track if it was called
        self.stackql_magic._display_with_csv_download = MagicMock()
        
        # Execute the magic with both options
        result = self.stackql_magic.stackql(line="--csv-download --no-display", cell=self.query)
        
        # Validate the outcome - --no-display should take precedence
        assert result is None, "Result should be None when --no-display is set"
        assert 'stackql_df' in self.shell.user_ns, "stackql_df should still be in user namespace"
        assert self.shell.user_ns['stackql_df'].equals(self.expected_result), "stackql_df should match expected DataFrame"
        
        # Verify that _display_with_csv_download was NOT called
        self.stackql_magic._display_with_csv_download.assert_not_called()
        
        print_test_result("Cell magic query test (with --csv-download and --no-display, server mode)", 
                          result is None and 
                          'stackql_df' in self.shell.user_ns and 
                          self.shell.user_ns['stackql_df'].equals(self.expected_result) and
                          not self.stackql_magic._display_with_csv_download.called,
                          True, True)

    def test_display_with_csv_download_method(self):
        """Test the _display_with_csv_download method directly in server mode."""
        import base64
        from unittest.mock import patch
        
        # Create a test DataFrame
        test_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        
        # Mock IPython display functionality
        with patch('pystackql.magic_ext.server.display') as mock_display, \
             patch('pystackql.magic_ext.server.HTML') as mock_html:
            
            # Call the method
            self.stackql_magic._display_with_csv_download(test_df)
            
            # Verify display was called
            mock_display.assert_called_once()
            mock_html.assert_called_once()
            
            # Get the HTML content that was passed
            html_content = mock_html.call_args[0][0]
            
            # Verify the HTML contains expected elements
            assert "data:text/csv;base64," in html_content, "HTML should contain base64 data URI"
            assert "download=\"stackql_results.csv\"" in html_content, "HTML should contain download filename"
            assert "📥 Download CSV" in html_content, "HTML should contain download button text"
            
            # Verify the CSV content is properly base64 encoded
            expected_csv = test_df.to_csv(index=False)
            expected_base64 = base64.b64encode(expected_csv.encode('utf-8')).decode('utf-8')
            assert expected_base64 in html_content, "HTML should contain correctly encoded CSV data"
        
        print_test_result("CSV download method test (server mode)", 
                          True,  # All assertions passed if we reach here
                          True, True)

    def test_display_with_csv_download_error_handling(self):
        """Test error handling in _display_with_csv_download method in server mode."""
        from unittest.mock import patch
        
        # Create a mock DataFrame that will raise an exception during to_csv()
        mock_df = MagicMock()
        mock_df.to_csv.side_effect = Exception("Test CSV error")
        
        # Mock IPython display functionality
        with patch('pystackql.magic_ext.server.display') as mock_display, \
             patch('pystackql.magic_ext.server.HTML') as mock_html:
            
            # Call the method with the problematic DataFrame
            self.stackql_magic._display_with_csv_download(mock_df)
            
            # Verify display was called (for error message)
            mock_display.assert_called_once()
            mock_html.assert_called_once()
            
            # Get the HTML content that was passed
            html_content = mock_html.call_args[0][0]
            
            # Verify the HTML contains error message
            assert "CSV Download Error:" in html_content, "HTML should contain error message"
            assert "Test CSV error" in html_content, "HTML should contain specific error text"
        
        print_test_result("CSV download error handling test (server mode)", 
                          True,  # All assertions passed if we reach here
                          True, True)

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