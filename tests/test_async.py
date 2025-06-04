# tests/test_async.py

"""
Async functionality tests for PyStackQL in non-server mode.

This module tests the async query execution functionality of the StackQL class.
"""

import os
import sys
import platform
import pytest
import pandas as pd

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import (
    ASYNC_QUERIES,
    print_test_result,
    async_test_decorator
)

# Skip all tests on Windows due to asyncio issues
pytestmark = pytest.mark.skipif(
    platform.system() == "Windows", 
    reason="Skipping async tests on Windows"
)

class TestAsyncFunctionality:
    """Tests for PyStackQL async functionality in non-server mode."""
    
    # Helper method to extract value from response objects
    def _get_value(self, obj):
        """Extract actual value from response objects that might be wrapped in a dict."""
        if isinstance(obj, dict) and 'String' in obj and 'Valid' in obj:
            return obj['String']
        return obj
    
    @async_test_decorator
    async def test_execute_queries_async_dict_output(self):
        """Test executeQueriesAsync with dict output format."""
        stackql = StackQL()
        results = await stackql.executeQueriesAsync(ASYNC_QUERIES)
        
        # Check result structure
        assert isinstance(results, list), "Results should be a list"
        assert all(isinstance(item, dict) for item in results), "Each item in results should be a dict"
        
        # Check result content
        assert len(results) > 0, "Results should not be empty"
        assert all("formula_name" in item for item in results), "Each item should have 'formula_name' column"
        
        # Extract formula names, handling possible dictionary format
        formula_names = []
        for item in results:
            if "formula_name" in item:
                formula_name = self._get_value(item["formula_name"])
                formula_names.append(formula_name)
        
        # Check that we have the expected formula names
        assert any("stackql" in str(name) for name in formula_names), "Results should include 'stackql'"
        assert any("terraform" in str(name) for name in formula_names), "Results should include 'terraform'"
        
        print_test_result(f"Async executeQueriesAsync with dict output test\nRESULT COUNT: {len(results)}", 
                          isinstance(results, list) and all(isinstance(item, dict) for item in results),
                          is_async=True)
    
    @async_test_decorator
    async def test_execute_queries_async_pandas_output(self):
        """Test executeQueriesAsync with pandas output format."""
        stackql = StackQL(output='pandas')
        result = await stackql.executeQueriesAsync(ASYNC_QUERIES)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        assert "formula_name" in result.columns, "DataFrame should have 'formula_name' column"
        
        # Extract formula names, handling possible dictionary format
        formula_values = []
        for i in range(len(result)):
            formula_name = result["formula_name"].iloc[i]
            if isinstance(formula_name, dict) and 'String' in formula_name:
                formula_name = formula_name['String']
            formula_values.append(formula_name)
            
        # Check that we have the expected formula names
        assert any("stackql" in str(name) for name in formula_values), "Results should include 'stackql'"
        assert any("terraform" in str(name) for name in formula_values), "Results should include 'terraform'"
        
        # Check that numeric columns exist
        numeric_columns = [
            "installs_30d", "installs_90d", "installs_365d", 
            "install_on_requests_30d", "install_on_requests_90d", "install_on_requests_365d"
        ]
        for col in numeric_columns:
            assert col in result.columns, f"DataFrame should have '{col}' column"
            
            # Check that the column can be converted to numeric
            try:
                if isinstance(result[col].iloc[0], dict) and 'String' in result[col].iloc[0]:
                    # If it's a dictionary with a String key, try to convert that string to numeric
                    pd.to_numeric(result[col].iloc[0]['String'])
                else:
                    # Otherwise try to convert the column directly
                    pd.to_numeric(result[col])
                numeric_conversion_success = True
            except (ValueError, TypeError):
                numeric_conversion_success = False
                
            assert numeric_conversion_success, f"Column '{col}' should be convertible to numeric"
        
        print_test_result(f"Async executeQueriesAsync with pandas output test\nRESULT COUNT: {len(result)}", 
                          isinstance(result, pd.DataFrame) and not result.empty,
                          is_async=True)
    
    @async_test_decorator
    async def test_execute_queries_async_csv_output(self):
        """Test that executeQueriesAsync with csv output raises ValueError."""
        stackql = StackQL(output='csv')
        
        with pytest.raises(ValueError) as exc_info:
            await stackql.executeQueriesAsync(ASYNC_QUERIES)
        
        # Check exception message
        error_msg = str(exc_info.value)
        assert "executeQueriesAsync supports only" in error_msg, "Error message should mention supported formats"
        assert "dict" in error_msg, "Error message should mention 'dict'"
        assert "pandas" in error_msg, "Error message should mention 'pandas'"
        
        print_test_result(f"Async executeQueriesAsync with csv output test", 
                          "executeQueriesAsync supports only" in error_msg,
                          is_async=True)

if __name__ == "__main__":
    pytest.main(["-v", __file__])