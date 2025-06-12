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
        
        This method processes SQL type objects from StackQL:
        - SQL NULL values: {'String': '', 'Valid': False} → None
        - Regular values: {'String': 'value', 'Valid': True} → 'value'
        - Empty strings: {'String': '', 'Valid': True} → '' (preserved as empty string)
        
        Args:
            data (str): The data string
            
        Returns:
            The formatted data in the specified output format
        """
        if self.output_format == 'csv':
            return data
        
        try:
            # Attempt to parse JSON first
            raw_json_data = json.loads(data)
        except json.JSONDecodeError as e:
            # Handle specific JSON parsing errors
            error_result = [{"error": f"Invalid JSON format: {str(e)}", "position": e.pos, "line": e.lineno, "column": e.colno}]
            return pd.DataFrame(error_result) if self.output_format == 'pandas' else error_result
        except TypeError as e:
            # Handle cases where data is not a string or buffer
            error_result = [{"error": f"Invalid data type for JSON parsing: {str(e)}", "data_type": str(type(data))}]
            return pd.DataFrame(error_result) if self.output_format == 'pandas' else error_result
        except Exception as e:
            # Catch any other unexpected errors
            error_result = [{"error": f"Unexpected error parsing JSON: {str(e)}", "exception_type": type(e).__name__}]
            return pd.DataFrame(error_result) if self.output_format == 'pandas' else error_result
        
        try:
            # Process the JSON data to clean up SQL type objects
            processed_json_data = self._process_sql_types(raw_json_data)
            
            # Handle empty data
            if not processed_json_data:
                return pd.DataFrame() if self.output_format == 'pandas' else []
            
            if self.output_format == 'pandas':
                import pandas as pd
                # Convert the preprocessed JSON data to a DataFrame
                return pd.DataFrame(processed_json_data)
            
            # Return the preprocessed dictionary data
            return processed_json_data
            
        except Exception as e:
            # Handle any errors during processing
            error_msg = f"Error processing data: {str(e)}"
            if self.output_format == 'pandas':
                import pandas as pd
                return pd.DataFrame([{"error": error_msg}])
            return [{"error": error_msg}]
        
    def _process_sql_types(self, data):
        """Process SQL type objects in the data.
        
        Args:
            data: The parsed JSON data
            
        Returns:
            The processed data with SQL type objects transformed
        """
        # Handle lists (most common case from StackQL)
        if isinstance(data, list):
            return [self._process_sql_types(item) for item in data]
        
        # Handle dictionaries (individual records or nested objects)
        elif isinstance(data, dict):
            # Check if this is an SQL type object
            if 'Valid' in data and len(data) <= 2 and ('String' in data or 'Int64' in data or 'Float64' in data):
                # This is an SQL type object - transform it
                if data.get('Valid', False):
                    # Valid: True -> return the actual value
                    for type_key in ['String', 'Int64', 'Float64']:
                        if type_key in data:
                            return data.get(type_key)
                    return None  # Fallback if no value field found
                else:
                    # Valid: False -> return None (SQL NULL)
                    return None
            else:
                # Regular dictionary - process each value
                result = {}
                for key, value in data.items():
                    result[key] = self._process_sql_types(value)
                return result
        
        # All other data types (strings, numbers, booleans, None) - return as is
        return data

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
            return {'message': message.rstrip('\n')}