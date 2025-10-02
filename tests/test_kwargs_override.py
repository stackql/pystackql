# tests/test_kwargs_override.py

"""
Tests for kwargs override functionality in execute and executeStmt methods.

This module tests the ability to override constructor parameters via kwargs
passed to execute() and executeStmt() methods.
"""

import os
import sys
import pytest
import pandas as pd

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import (
    LITERAL_INT_QUERY,
    LITERAL_STRING_QUERY,
    print_test_result,
    pystackql_test_setup
)

class TestKwargsOverride:
    """Tests for kwargs override in execute and executeStmt methods."""
    
    StackQL = StackQL  # For use with pystackql_test_setup decorator
    
    @pystackql_test_setup(output='csv')
    def test_execute_output_override_csv_to_dict(self):
        """Test that output format can be overridden from csv to dict in execute()."""
        # Instance is configured with CSV output
        assert self.stackql.output == 'csv', "Instance should be configured with CSV output"
        
        # Execute with dict output override
        result = self.stackql.execute(LITERAL_INT_QUERY, output='dict')
        
        # Check result structure - should be dict format, not csv
        assert isinstance(result, list), "Result should be a list (dict format)"
        assert len(result) > 0, "Result should not be empty"
        assert isinstance(result[0], dict), "Result items should be dicts"
        
        print_test_result(f"Execute output override csv to dict test\nRESULT TYPE: {type(result)}", 
                          isinstance(result, list) and isinstance(result[0], dict))
    
    @pystackql_test_setup(output='dict')
    def test_execute_output_override_dict_to_pandas(self):
        """Test that output format can be overridden from dict to pandas in execute()."""
        # Instance is configured with dict output
        assert self.stackql.output == 'dict', "Instance should be configured with dict output"
        
        # Execute with pandas output override
        result = self.stackql.execute(LITERAL_STRING_QUERY, output='pandas')
        
        # Check result structure - should be pandas DataFrame, not dict
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        assert not result.empty, "DataFrame should not be empty"
        
        print_test_result(f"Execute output override dict to pandas test\nRESULT TYPE: {type(result)}", 
                          isinstance(result, pd.DataFrame))
    
    @pystackql_test_setup(output='pandas')
    def test_execute_output_override_pandas_to_csv(self):
        """Test that output format can be overridden from pandas to csv in execute()."""
        # Instance is configured with pandas output
        assert self.stackql.output == 'pandas', "Instance should be configured with pandas output"
        
        # Execute with csv output override
        result = self.stackql.execute(LITERAL_INT_QUERY, output='csv')
        
        # Check result structure - should be csv string, not pandas
        assert isinstance(result, str), "Result should be a string (csv format)"
        assert "1" in result, "Result should contain the value '1'"
        
        print_test_result(f"Execute output override pandas to csv test\nRESULT: {result}", 
                          isinstance(result, str))
    
    @pystackql_test_setup(output='dict')
    def test_execute_multiple_overrides_in_sequence(self):
        """Test that multiple execute calls with different overrides work correctly."""
        # Instance is configured with dict output
        assert self.stackql.output == 'dict', "Instance should be configured with dict output"
        
        # First execution with dict (default)
        result1 = self.stackql.execute(LITERAL_INT_QUERY)
        assert isinstance(result1, list), "First result should be dict format"
        
        # Second execution with pandas override
        result2 = self.stackql.execute(LITERAL_STRING_QUERY, output='pandas')
        assert isinstance(result2, pd.DataFrame), "Second result should be pandas format"
        
        # Third execution with csv override
        result3 = self.stackql.execute(LITERAL_INT_QUERY, output='csv')
        assert isinstance(result3, str), "Third result should be csv format"
        
        # Fourth execution should still use dict (instance default)
        result4 = self.stackql.execute(LITERAL_INT_QUERY)
        assert isinstance(result4, list), "Fourth result should be dict format again"
        
        print_test_result(f"Multiple overrides in sequence test\nTypes: {[type(r).__name__ for r in [result1, result2, result3, result4]]}", 
                          isinstance(result1, list) and 
                          isinstance(result2, pd.DataFrame) and 
                          isinstance(result3, str) and 
                          isinstance(result4, list))
    
    @pystackql_test_setup(output='csv', header=False)
    def test_execute_csv_header_override(self):
        """Test that CSV header setting can be overridden in execute()."""
        # Instance is configured with CSV output and no header
        assert self.stackql.output == 'csv', "Instance should be configured with CSV output"
        assert self.stackql.header is False, "Instance should be configured with header=False"
        
        # Execute with header override
        result = self.stackql.execute(LITERAL_INT_QUERY, header=True)
        
        # Check result structure - should be csv string
        assert isinstance(result, str), "Result should be a string (csv format)"
        
        print_test_result(f"CSV header override test\nRESULT: {result}", 
                          isinstance(result, str))
    
    @pystackql_test_setup(output='csv', sep=',')
    def test_execute_csv_separator_override(self):
        """Test that CSV separator can be overridden in execute()."""
        # Instance is configured with CSV output and comma separator
        assert self.stackql.output == 'csv', "Instance should be configured with CSV output"
        assert self.stackql.sep == ',', "Instance should be configured with comma separator"
        
        # Execute with pipe separator override
        result = self.stackql.execute(LITERAL_INT_QUERY, sep='|')
        
        # Check result structure - should be csv string
        assert isinstance(result, str), "Result should be a string (csv format)"
        
        print_test_result(f"CSV separator override test\nRESULT: {result}", 
                          isinstance(result, str))
    
    @pystackql_test_setup(output='dict')
    def test_executeStmt_output_override(self):
        """Test that output format can be overridden in executeStmt()."""
        # Instance is configured with dict output
        assert self.stackql.output == 'dict', "Instance should be configured with dict output"
        
        # Execute a statement with pandas override
        # Using a simple SELECT that works as a statement
        result = self.stackql.executeStmt(LITERAL_INT_QUERY, output='pandas')
        
        # Check result structure - should be pandas DataFrame
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
        
        print_test_result(f"ExecuteStmt output override test\nRESULT TYPE: {type(result)}", 
                          isinstance(result, pd.DataFrame))

if __name__ == "__main__":
    pytest.main(["-v", __file__])
