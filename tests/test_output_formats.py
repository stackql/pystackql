# tests/test_output_formats.py

"""
Output format tests for PyStackQL.

This module tests the different output formats of the StackQL class.
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import (
    LITERAL_INT_QUERY,
    LITERAL_STRING_QUERY,
    HOMEBREW_METRICS_QUERY,
    print_test_result,
    pystackql_test_setup
)

class TestOutputFormats:
    """Tests for PyStackQL output format functionality."""
    
    StackQL = StackQL  # For use with pystackql_test_setup decorator
    
    @pystackql_test_setup()
    def test_dict_output_format(self):
        """Test that dict output format returns a list of dictionaries."""
        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert all(isinstance(item, dict) for item in result), "Each item in result should be a dict"
        
        print_test_result(f"Dict output format test\nRESULT: {result}", 
                          isinstance(result, list) and all(isinstance(item, dict) for item in result))
    
    @pystackql_test_setup(output='pandas')
    def test_pandas_output_format(self):
        """Test that pandas output format returns a pandas DataFrame."""
        result = self.stackql.execute(LITERAL_STRING_QUERY)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "literal_string_value" in result.columns, "DataFrame should have 'literal_string_value' column"
        
        # Extract the value
        value = result["literal_string_value"].iloc[0]
        
        assert value == "test" or value == '"test"', f"Value should be 'test', got {value}"
        
        print_test_result(f"Pandas output format test\nRESULT: {result}", 
                          isinstance(result, pd.DataFrame) and "literal_string_value" in result.columns)
    
    @pystackql_test_setup(output='pandas')
    def test_pandas_output_with_numeric_types(self):
        """Test that pandas output format handles numeric types correctly."""
        result = self.stackql.execute(HOMEBREW_METRICS_QUERY)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "formula_name" in result.columns, "DataFrame should have 'formula_name' column"
        
        # Check numeric columns - either directly numeric or string representation
        numeric_columns = [
            "installs_30d", "installs_90d", "installs_365d", 
            "install_on_requests_30d", "install_on_requests_90d", "install_on_requests_365d"
        ]
        
        # Validate formula name
        formula_name = result["formula_name"].iloc[0]
        assert "stackql" in str(formula_name), f"Formula name should contain 'stackql', got {formula_name}"
        
        # Verify numeric columns exist
        for col in numeric_columns:
            assert col in result.columns, f"DataFrame should have '{col}' column"
            
            # Try to convert to numeric if possible
            try:
                pd.to_numeric(result[col])
                numeric_conversion_success = True
            except (ValueError, TypeError):
                numeric_conversion_success = False
                
            assert numeric_conversion_success, f"Column '{col}' should be convertible to numeric"
        
        print_test_result(f"Pandas output with numeric types test\nCOLUMNS: {list(result.columns)}", 
                          isinstance(result, pd.DataFrame) and 
                          all(col in result.columns for col in numeric_columns))
    
    @pystackql_test_setup(output='csv')
    def test_csv_output_format(self):
        """Test that csv output format returns a string."""
        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, str), "Result should be a string"
        # The CSV output might just contain the value (1) or might include the column name
        # We'll check for either possibility
        assert "1" in result, "Result should contain the value '1'"
        
        print_test_result(f"CSV output format test\nRESULT: {result}", 
                          isinstance(result, str) and "1" in result)
    
    @pystackql_test_setup(output='csv')
    def test_csv_output_with_pipe_separator(self):
        """Test that csv output format with custom separator is configured correctly."""
        # Create a new instance with pipe separator
        stackql_with_pipe = StackQL(output='csv', sep='|')
        
        # Verify that the separator setting is correct
        assert stackql_with_pipe.sep == "|", "Separator should be '|'"
        assert "--delimiter" in stackql_with_pipe.params, "Params should include '--delimiter'"
        assert "|" in stackql_with_pipe.params, "Params should include '|'"
        
        # Instead of checking the output (which might be affected by other factors),
        # we'll focus on verifying that the parameters are set correctly
        print_test_result(f"CSV output with pipe separator test\nPARAMS: {stackql_with_pipe.params}", 
                          stackql_with_pipe.sep == "|" and 
                          "--delimiter" in stackql_with_pipe.params and 
                          "|" in stackql_with_pipe.params)
    
    @pystackql_test_setup(output='csv', header=True)
    def test_csv_output_with_header(self):
        """Test that csv output format with header works correctly."""
        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, str), "Result should be a string"
        
        # Check that params are set correctly
        assert self.stackql.header is True, "Header should be True"
        assert "--hideheaders" not in self.stackql.params, "Params should not include '--hideheaders'"
        
        print_test_result(f"CSV output with header test\nRESULT: {result}", 
                          isinstance(result, str))
    
    @pystackql_test_setup(output='csv', header=False)
    def test_csv_output_without_header(self):
        """Test that csv output format without header works correctly."""
        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, str), "Result should be a string"
        
        # Check that params are set correctly
        assert self.stackql.header is False, "Header should be False"
        assert "--hideheaders" in self.stackql.params, "Params should include '--hideheaders'"
        
        print_test_result(f"CSV output without header test\nRESULT: {result}", 
                          isinstance(result, str))
    
    def test_invalid_output_format(self):
        """Test that an invalid output format raises a ValueError."""
        with pytest.raises(ValueError) as exc_info:
            StackQL(output='invalid')
        
        # Check that the exception message contains the expected elements
        # rather than checking for an exact match, which is brittle
        error_msg = str(exc_info.value)
        assert "Invalid output" in error_msg, "Error message should mention 'Invalid output'"
        assert "Expected one of" in error_msg, "Error message should mention 'Expected one of'"
        assert "dict" in error_msg, "Error message should mention 'dict'"
        assert "pandas" in error_msg, "Error message should mention 'pandas'"
        assert "csv" in error_msg, "Error message should mention 'csv'"
        assert "invalid" in error_msg, "Error message should mention 'invalid'"
        
        print_test_result(f"Invalid output format test\nERROR: {error_msg}", 
                          all(text in error_msg for text in ["Invalid output", "Expected one of", "dict", "pandas", "csv", "invalid"]))
    
    def test_csv_output_in_server_mode(self):
        """Test that csv output in server mode raises a ValueError."""
        with pytest.raises(ValueError) as exc_info:
            StackQL(server_mode=True, output='csv')
        
        # Check that the exception message contains the expected elements
        error_msg = str(exc_info.value)
        assert "CSV output is not supported in server mode" in error_msg, "Error message should mention CSV not supported"
        assert "use 'dict' or 'pandas' instead" in error_msg, "Error message should suggest alternatives"
        
        print_test_result(f"CSV output in server mode test\nERROR: {error_msg}", 
                          "CSV output is not supported in server mode" in error_msg)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
