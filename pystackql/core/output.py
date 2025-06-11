# pystackql/core/output.py

"""
Output formatting module for PyStackQL.

This module handles the formatting of query results into different output formats.
"""

import json
from io import StringIO

class OutputFormatter:
    """Formats query results into different output formats.
    
    This class is responsible for converting raw query results into
    the desired output format (dict, pandas, or csv).
    """
    
    def __init__(self, output_format='dict'):
        """Initialize the OutputFormatter.
        
        Args:
            output_format (str, optional): The output format. Defaults to 'dict'.
                Allowed values: 'dict', 'pandas', 'csv'
                
        Raises:
            ValueError: If an invalid output format is specified
        """
        ALLOWED_OUTPUTS = {'dict', 'pandas', 'csv'}
        if output_format.lower() not in ALLOWED_OUTPUTS:
            raise ValueError(f"Invalid output format. Expected one of {ALLOWED_OUTPUTS}, got {output_format}.")
        self.output_format = output_format.lower()
    
    def format_query_result(self, result, suppress_errors=True):
        """Format a query result.
        
        Args:
            result (dict): The raw query result from the executor
            suppress_errors (bool, optional): Whether to suppress errors. Defaults to True.
            
        Returns:
            The formatted result in the specified output format
        """
        # Handle exceptions
        if "exception" in result:
            exception_msg = result["exception"]
            return self._format_exception(exception_msg)
        
        # Handle data
        if "data" in result:
            data = result["data"]
            return self._format_data(data)
        
        # Handle errors
        if "error" in result and not suppress_errors:
            err_msg = result["error"]
            return self._format_error(err_msg)
        
        # No data, no error, return empty result
        return self._format_empty()
    
    def _format_exception(self, exception_msg):
        """Format an exception message.
        
        Args:
            exception_msg (str): The exception message
            
        Returns:
            The formatted exception in the specified output format
        """
        if self.output_format == 'pandas':
            import pandas as pd
            return pd.DataFrame({'error': [exception_msg]}) if exception_msg else pd.DataFrame({'error': []})
        elif self.output_format == 'csv':
            return exception_msg
        else:  # dict
            return [{"error": exception_msg}]
    
    def _format_error(self, error_msg):
        """Format an error message.
        
        Args:
            error_msg (str): The error message
            
        Returns:
            The formatted error in the specified output format
        """
        if self.output_format == 'pandas':
            import pandas as pd
            return pd.DataFrame({'error': [error_msg]}) if error_msg else pd.DataFrame({'error': []})
        elif self.output_format == 'csv':
            return error_msg
        else:  # dict
            return [{"error": error_msg}]
    
    def _format_data(self, data):
        """Format data.
        
        Args:
            data (str): The data string
            
        Returns:
            The formatted data in the specified output format
        """
        if self.output_format == 'csv':
            return data
        elif self.output_format == 'pandas':
            import pandas as pd
            try:
                return pd.read_json(StringIO(data))
            except ValueError:
                return pd.DataFrame([{"error": "Invalid JSON output"}])
        else:  # dict
            try:
                retval = json.loads(data)
                return retval if retval else []
            except ValueError:
                return [{"error": f"Invalid JSON output : {data}"}]
    
    def _format_empty(self):
        """Format an empty result.
        
        Returns:
            An empty result in the specified output format
        """
        if self.output_format == 'pandas':
            import pandas as pd
            return pd.DataFrame()
        elif self.output_format == 'csv':
            return ""
        else:  # dict
            return []
    
    def format_statement_result(self, result):
        """Format a statement result.
        
        Args:
            result (dict): The raw statement result from the executor
            
        Returns:
            The formatted result in the specified output format
        """
        # Handle exceptions
        if "exception" in result:
            exception_msg = result["exception"]
            return self._format_exception(exception_msg)
        
        # Message on stderr or empty message
        message = result.get("error", "")
        
        if self.output_format == 'pandas':
            import pandas as pd
            return pd.DataFrame({'message': [message]}) if message else pd.DataFrame({'message': []})
        elif self.output_format == 'csv':
            return message
        else:  # dict
            # Count number of rows in the message
            try:
                return {'message': message, 'rowsaffected': message.count('\n')}
            except Exception:
                return {'message': message, 'rowsaffected': 0}