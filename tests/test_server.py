# tests/test_server.py

"""
Server mode tests for PyStackQL.

This module tests the server mode functionality of the StackQL class.
"""

import re
import os
import pytest
import pandas as pd
from unittest.mock import patch
from pystackql import StackQL
from test_constants import (
    LITERAL_INT_QUERY,
    LITERAL_STRING_QUERY,
    HOMEBREW_FORMULA_QUERY,
    REGISTRY_PULL_HOMEBREW_QUERY,
    print_test_result,
    pystackql_test_setup
)

# @pytest.mark.usefixtures("stackql_server")
class TestServerMode:
    """Tests for PyStackQL server mode functionality."""
    
    StackQL = StackQL  # For use with pystackql_test_setup decorator
    server_available = False  # Class-level flag to track server availability    

    # @pystackql_test_setup(server_mode=True)
    # def test_server_mode_connectivity(self):
    #     """Test that server mode connects successfully."""
    #     # Check server_mode flag is set correctly
    #     assert self.stackql.server_mode, "StackQL should be in server mode"
        
    #     # Check server connection object exists
    #     assert hasattr(self.stackql, 'server_connection'), "StackQL should have a server_connection attribute"
    #     assert self.stackql.server_connection is not None, "Server connection object should not be None"
        
    #     # IMPORTANT: Actually test the connection works
    #     connection_working = self.stackql.test_connection()
        
    #     # Print detailed results for debugging
    #     if not connection_working:
    #         print("⚠️ Server connection test failed: unable to execute a simple query")
    #         print(f"Server address: {self.stackql.server_address}")
    #         print(f"Server port: {self.stackql.server_port}")
    #         print("\n❌ SERVER CONNECTION FAILED - SKIPPING REMAINING SERVER TESTS")
    #     else:
    #         # Set flag indicating server is available
    #         TestServerMode.server_available = True
        
    #     print_test_result("Server mode connectivity test", 
    #                     self.stackql.server_mode and 
    #                     hasattr(self.stackql, 'server_connection') and 
    #                     self.stackql.server_connection is not None and
    #                     connection_working,  # Include connection check in the pass criteria
    #                     True)
        
    #     # Add additional output about the actual connection status
    #     print(f"  - Connection status: {'✅ WORKING' if connection_working else '❌ NOT WORKING'}")
    #     print(f"  - Expected status: ✅ WORKING")  # Always expected to be working
        
    #     # Always assert that the connection is working
    #     assert connection_working, "Server connection should be working"

    @pystackql_test_setup(server_mode=True)
    def test_server_mode_connectivity(self):
        """Test that server mode connects successfully."""
        # Initialize class variable 
        TestServerMode.server_available = False
        
        # Perform basic server connection test
        connection_working = self.stackql.test_connection()
        
        if not connection_working:
            # Log minimal diagnostic info
            print("\n⚠️ Server connection failed")
            print(f"Address: {self.stackql.server_address}:{self.stackql.server_port}")
            print("❌ Skipping remaining server tests")
            
            # Fail with a concise message - this will be what shows in the error summary
            pytest.fail("Server connection failed - please start stackql server")
        
        # Connection succeeded
        TestServerMode.server_available = True
        print("✅ Server connection successful")

    @pystackql_test_setup(server_mode=True)
    def test_server_mode_execute_stmt(self):
        """Test executeStmt in server mode."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        result = self.stackql.executeStmt(REGISTRY_PULL_HOMEBREW_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one item"
        assert "message" in result[0], "Result should have a 'message' key"
        assert result[0]["message"] == "OK", "Message should be 'OK'"
        
        print_test_result(f"Server mode executeStmt test\nRESULT: {result}", 
                          isinstance(result, list) and 
                          len(result) == 1 and 
                          result[0]["message"] == "OK", 
                          True)
    
    @pystackql_test_setup(server_mode=True, output='pandas')
    def test_server_mode_execute_stmt_pandas(self):
        """Test executeStmt in server mode with pandas output."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        result = self.stackql.executeStmt(REGISTRY_PULL_HOMEBREW_QUERY)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "message" in result.columns, "DataFrame should have a 'message' column"
        assert result["message"].iloc[0] == "OK", "Message should be 'OK'"
        
        print_test_result(f"Server mode executeStmt with pandas output test\nRESULT: {result}", 
                          isinstance(result, pd.DataFrame) and 
                          not result.empty and 
                          result["message"].iloc[0] == "OK", 
                          True)
    
    @pystackql_test_setup(server_mode=True)
    def test_server_mode_execute(self):
        """Test execute in server mode."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one item"
        assert "literal_int_value" in result[0], "Result should have a 'literal_int_value' key"
        # Update assertion to handle string value from server
        literal_value = result[0]["literal_int_value"]
        if isinstance(literal_value, str):
            literal_value = int(literal_value)
        assert literal_value == 1, "Value should be 1"
        
        print_test_result(f"Server mode execute test\nRESULT: {result}", 
                          isinstance(result, list) and 
                          len(result) == 1 and 
                          int(result[0]["literal_int_value"]) == 1, 
                          True)
    
    @pystackql_test_setup(server_mode=True, output='pandas')
    def test_server_mode_execute_pandas(self):
        """Test execute in server mode with pandas output."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        result = self.stackql.execute(LITERAL_STRING_QUERY)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "literal_string_value" in result.columns, "DataFrame should have a 'literal_string_value' column"
        assert result["literal_string_value"].iloc[0] == "test", "Value should be 'test'"
        
        print_test_result(f"Server mode execute with pandas output test\nRESULT: {result}", 
                          isinstance(result, pd.DataFrame) and 
                          not result.empty and 
                          result["literal_string_value"].iloc[0] == "test", 
                          True)
    
    @pystackql_test_setup(server_mode=True)
    def test_server_mode_provider_query(self):
        """Test querying a provider in server mode."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        result = self.stackql.execute(HOMEBREW_FORMULA_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one item"
        assert "name" in result[0], "Result should have a 'name' key"
        assert "full_name" in result[0], "Result should have a 'full_name' key"
        assert "tap" in result[0], "Result should have a 'tap' key"
        assert result[0]["name"] == "stackql", "Name should be 'stackql'"
        
        print_test_result(f"Server mode provider query test\nRESULT: {result}", 
                          isinstance(result, list) and 
                          len(result) == 1 and 
                          result[0]["name"] == "stackql", 
                          True)
    
    # Update mocked tests to use execute_query instead of _run_server_query
    @patch('pystackql.core.server.ServerConnection.execute_query')
    def test_server_mode_execute_mocked(self, mock_execute_query):
        """Test execute in server mode with mocked server response."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        # Create a StackQL instance in server mode
        stackql = StackQL(server_mode=True)
        
        # Mock the server response
        mock_result = [{"literal_int_value": 1}]
        mock_execute_query.return_value = mock_result
        
        # Execute the query
        result = stackql.execute(LITERAL_INT_QUERY)
        
        # Check that the mock was called with the correct query
        mock_execute_query.assert_called_once_with(LITERAL_INT_QUERY)
        
        # Check result structure
        assert result == mock_result, "Result should match the mocked result"
        
        print_test_result(f"Server mode execute test (mocked)\nRESULT: {result}", 
                          result == mock_result, 
                          True)
    
    @patch('pystackql.core.server.ServerConnection.execute_query')
    def test_server_mode_execute_pandas_mocked(self, mock_execute_query):
        """Test execute in server mode with pandas output and mocked server response."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        # Create a StackQL instance in server mode with pandas output
        stackql = StackQL(server_mode=True, output='pandas')
        
        # Mock the server response
        mock_result = [{"literal_string_value": "test"}]
        mock_execute_query.return_value = mock_result
        
        # Execute the query
        result = stackql.execute(LITERAL_STRING_QUERY)
        
        # Check that the mock was called with the correct query
        mock_execute_query.assert_called_once_with(LITERAL_STRING_QUERY)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "literal_string_value" in result.columns, "DataFrame should have a 'literal_string_value' column"
        assert result["literal_string_value"].iloc[0] == "test", "Value should be 'test'"
        
        print_test_result(f"Server mode execute with pandas output test (mocked)\nRESULT: {result}", 
                          isinstance(result, pd.DataFrame) and 
                          not result.empty and 
                          result["literal_string_value"].iloc[0] == "test", 
                          True)
    
    @patch('pystackql.core.server.ServerConnection.execute_query')
    def test_server_mode_execute_stmt_mocked(self, mock_execute_query):
        """Test executeStmt in server mode with mocked server response."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        # Create a StackQL instance in server mode
        stackql = StackQL(server_mode=True)
        
        # Mock the server response
        mock_result = [{"message": "OK"}]
        mock_execute_query.return_value = mock_result
        
        # Execute the statement
        result = stackql.executeStmt(REGISTRY_PULL_HOMEBREW_QUERY)
        
        # Check that the mock was called with the correct query and is_statement=True
        mock_execute_query.assert_called_once_with(REGISTRY_PULL_HOMEBREW_QUERY, is_statement=True)
        
        # Check result structure
        assert result == mock_result, "Result should match the mocked result"
        
        print_test_result(f"Server mode executeStmt test (mocked)\nRESULT: {result}", 
                          result == mock_result, 
                          True)
    
    def test_server_mode_csv_output_error(self):
        """Test that server mode with csv output raises an error."""

        # Skip if server is not available
        if not TestServerMode.server_available:
            pytest.skip("Server is not available, skipping test")

        with pytest.raises(ValueError) as exc_info:
            StackQL(server_mode=True, output='csv')
        
        # Check exception message
        expected_message = "CSV output is not supported in server mode, use 'dict' or 'pandas' instead."
        assert str(exc_info.value) == expected_message, f"Exception message '{str(exc_info.value)}' does not match expected"
        
        print_test_result(f"Server mode with csv output error test", 
                          str(exc_info.value) == expected_message, 
                          True)


if __name__ == "__main__":
    pytest.main(["-v", __file__])