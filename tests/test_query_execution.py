# tests/test_query_execution.py

"""
Query execution tests for PyStackQL.

This module tests the query execution functionality of the StackQL class.
"""

import os
import re
import sys
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import (
    LITERAL_INT_QUERY,
    LITERAL_FLOAT_QUERY,
    LITERAL_STRING_QUERY,
    EXPRESSION_TRUE_QUERY,
    EXPRESSION_FALSE_QUERY,
    EMPTY_RESULT_QUERY,
    JSON_EXTRACT_QUERY,
    HOMEBREW_FORMULA_QUERY,
    HOMEBREW_METRICS_QUERY,
    REGISTRY_PULL_HOMEBREW_QUERY,
    registry_pull_resp_pattern,
    print_test_result,
    pystackql_test_setup
)

class TestQueryExecution:
    """Tests for PyStackQL query execution functionality."""
    
    StackQL = StackQL  # For use with pystackql_test_setup decorator
    
    # Helper method to check if a value is numeric
    def _is_numeric(self, value):
        """Check if a value is numeric."""
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        return False
    
    @pystackql_test_setup()
    def test_execute_literal_int(self):
        """Test executing a query with a literal integer value."""
        result = self.stackql.execute(LITERAL_INT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "literal_int_value" in result[0], "Result should have 'literal_int_value' column"
        
        # Check the value - could be int or string representation
        value = result[0]["literal_int_value"]
        assert value == "1" or value == 1, f"Result value should be 1, got {value}"
        
        print_test_result(f"Execute literal int query test\nRESULT: {result}", 
                          value == "1" or value == 1)
    
    @pystackql_test_setup()
    def test_execute_literal_float(self):
        """Test executing a query with a literal float value."""
        result = self.stackql.execute(LITERAL_FLOAT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "literal_float_value" in result[0], "Result should have 'literal_float_value' column"
        
        # Check the value - could be float or string representation
        value = result[0]["literal_float_value"]
        assert value == "1.001" or value == 1.001, f"Result value should be 1.001, got {value}"
        
        print_test_result(f"Execute literal float query test\nRESULT: {result}", 
                          value == "1.001" or value == 1.001)
    
    @pystackql_test_setup()
    def test_execute_literal_string(self):
        """Test executing a query with a literal string value."""
        result = self.stackql.execute(LITERAL_STRING_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "literal_string_value" in result[0], "Result should have 'literal_string_value' column"
        
        # Check the value
        value = result[0]["literal_string_value"]
        assert value == "test", f"Result value should be 'test', got {value}"
        
        print_test_result(f"Execute literal string query test\nRESULT: {result}", 
                          value == "test")
    
    @pystackql_test_setup()
    def test_execute_expression_true(self):
        """Test executing a query with a true expression."""
        result = self.stackql.execute(EXPRESSION_TRUE_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "expression" in result[0], "Result should have 'expression' column"
        
        # Check the value - could be int or string
        value = result[0]["expression"]
        assert value == "1" or value == 1, f"Result value should be 1 (true), got {value}"
        
        print_test_result(f"Execute true expression query test\nRESULT: {result}", 
                          value == "1" or value == 1)
    
    @pystackql_test_setup()
    def test_execute_expression_false(self):
        """Test executing a query with a false expression."""
        result = self.stackql.execute(EXPRESSION_FALSE_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "expression" in result[0], "Result should have 'expression' column"
        
        # Check the value - could be int or string
        value = result[0]["expression"]
        assert value == "0" or value == 0, f"Result value should be 0 (false), got {value}"
        
        print_test_result(f"Execute false expression query test\nRESULT: {result}", 
                          value == "0" or value == 0)
    
    @pystackql_test_setup()
    def test_execute_empty_result(self):
        """Test executing a query that returns an empty result."""
        result = self.stackql.execute(EMPTY_RESULT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 0, "Result should be empty"
        
        print_test_result(f"Execute empty result query test\nRESULT: {result}", len(result) == 0)
    
    @pystackql_test_setup()
    def test_execute_json_extract(self):
        """Test executing a query that uses the json_extract function."""
        result = self.stackql.execute(JSON_EXTRACT_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "key" in result[0], "Result should have 'key' column"
        assert "value" in result[0], "Result should have 'value' column"
        
        # Get the extracted values
        key_value = result[0]["key"]
        value_value = result[0]["value"]
        
        # Check values - with new implementation they should be direct strings
        assert "StackName" in str(key_value), "Key should contain 'StackName'"
        assert "aws-stack" in str(value_value), "Value should contain 'aws-stack'"
        
        print_test_result(f"Execute JSON extract query test\nRESULT: {result}", 
                          "StackName" in str(key_value) and "aws-stack" in str(value_value))
    
    @pystackql_test_setup()
    def test_execute_homebrew_formula(self):
        """Test executing a query against the homebrew.formula.formula table."""
        result = self.stackql.execute(HOMEBREW_FORMULA_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        assert "name" in result[0], "Result should have 'name' column"
        assert "full_name" in result[0], "Result should have 'full_name' column"
        assert "tap" in result[0], "Result should have 'tap' column"
        
        # Check formula values - should be direct strings now
        name_value = result[0]["name"]
        full_name_value = result[0]["full_name"]
        tap_value = result[0]["tap"]
        
        assert "stackql" in str(name_value), f"Name should contain 'stackql', got {name_value}"
        assert "stackql" in str(full_name_value), f"Full name should contain 'stackql', got {full_name_value}"
        assert "homebrew/core" in str(tap_value), f"Tap should contain 'homebrew/core', got {tap_value}"
        
        print_test_result(f"Execute homebrew formula query test\nRESULT: {result}", 
                          "stackql" in str(name_value) and 
                          "stackql" in str(full_name_value) and 
                          "homebrew/core" in str(tap_value))
    
    @pystackql_test_setup()
    def test_execute_homebrew_metrics(self):
        """Test executing a query against the homebrew.formula.vw_usage_metrics view."""
        result = self.stackql.execute(HOMEBREW_METRICS_QUERY)
        
        # Check result structure
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == 1, "Result should have exactly one row"
        
        # Check column names (not values as they change over time)
        expected_columns = [
            "formula_name", "installs_30d", "installs_90d", "installs_365d", 
            "install_on_requests_30d", "install_on_requests_90d", "install_on_requests_365d"
        ]
        for col in expected_columns:
            assert col in result[0], f"Result should have '{col}' column"
        
        # Check formula name - should be direct string now
        formula_name = result[0]["formula_name"]
        assert "stackql" in str(formula_name), f"Formula name should contain 'stackql', got {formula_name}"
        
        # Check data types - should be numeric or string representations of numbers
        for col in expected_columns[1:]:  # Skip formula_name
            assert self._is_numeric(result[0][col]), f"Column '{col}' should be numeric or string representation of a number"
        
        print_test_result(f"Execute homebrew metrics query test\nCOLUMNS: {list(result[0].keys())}", 
                          all(col in result[0] for col in expected_columns) and 
                          "stackql" in str(formula_name))
    
    @pystackql_test_setup()
    def test_execute_stmt_registry_pull(self):
        """Test executing a registry pull statement."""
        result = self.stackql.executeStmt(REGISTRY_PULL_HOMEBREW_QUERY)
        
        # Check result structure (depends on output format)
        if self.stackql.output == 'dict':
            assert 'message' in result, "Result should have 'message' key"
            message = result['message']
        elif self.stackql.output == 'pandas':
            assert 'message' in result.columns, "Result should have 'message' column"
            message = result['message'].iloc[0]
        elif self.stackql.output == 'csv':
            message = result
        else:
            message = str(result)
        
        # Check that the message matches the expected pattern
        expected_pattern = registry_pull_resp_pattern("homebrew")
        assert re.search(expected_pattern, message), f"Message '{message}' does not match expected pattern"
        
        print_test_result(f"Execute registry pull statement test\nRESULT: {result}", 
                          re.search(expected_pattern, message) is not None)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
