# pystackql/core/stackql.py

"""
Main StackQL class for PyStackQL.

This module provides the main StackQL class that serves as the primary
interface for executing StackQL queries.
"""

import os
import json
from .server import ServerConnection
from .query import QueryExecutor, AsyncQueryExecutor
from .output import OutputFormatter
from ..utils import setup_local_mode

class StackQL:
    """A class representing an instance of the StackQL query engine.
    
    :param server_mode: Connect to a StackQL server 
        (defaults to `False`)
    :type server_mode: bool, optional
    :param server_address: The address of the StackQL server 
        (`server_mode` only, defaults to `'127.0.0.1'`)
    :type server_address: str, optional
    :param server_port: The port of the StackQL server 
        (`server_mode` only, defaults to `5466`)
    :type server_port: int, optional
    :param backend_storage_mode: Specifies backend storage mode, options are 'memory' and 'file'
        (defaults to `'memory'`, this option is ignored in `server_mode`)
    :type backend_storage_mode: str, optional
    :param backend_file_storage_location: Specifies location for database file, only applicable when `backend_storage_mode` is 'file'
        (defaults to `'{cwd}/stackql.db'`, this option is ignored in `server_mode`)
    :type backend_file_storage_location: str, optional
    :param output: Determines the format of the output, options are 'dict', 'pandas', and 'csv' 
        (defaults to `'dict'`, `'csv'` is not supported in `server_mode`)
    :type output: str, optional
    :param sep: Seperator for values in CSV output 
        (defaults to `','`, `output='csv'` only)
    :type sep: str, optional
    :param header: Show column headers in CSV output 
        (defaults to `False`, `output='csv'` only)
    :type header: bool, optional
    :param download_dir: The download directory for the StackQL executable 
        (defaults to `site.getuserbase()`, not supported in `server_mode`)
    :type download_dir: str, optional
    :param app_root: Application config and cache root path
        (defaults to `{cwd}/.stackql`)
    :type app_root: str, optional    
    :param execution_concurrency_limit: Concurrency limit for query execution
        (defaults to `-1` - unlimited)
    :type execution_concurrency_limit: int, optional
    :param dataflow_dependency_max: Max dataflow weakly connected components for a given query
        (defaults to `50`)
    :type dataflow_dependency_max: int, optional
    :param dataflow_components_max: Max dataflow components for a given query
        (defaults to `50`)
    :type dataflow_components_max: int, optional
    :param api_timeout: API timeout 
        (defaults to `45`, not supported in `server_mode`)
    :type api_timeout: int, optional
    :param proxy_host: HTTP proxy host 
        (not supported in `server_mode`)
    :type proxy_host: str, optional
    :param proxy_password: HTTP proxy password 
        (only applicable when `proxy_host` is set)
    :type proxy_password: str, optional
    :param proxy_port: HTTP proxy port 
        (defaults to `-1`, only applicable when `proxy_host` is set)
    :type proxy_port: int, optional
    :param proxy_scheme: HTTP proxy scheme 
        (defaults to `'http'`, only applicable when `proxy_host` is set)
    :type proxy_scheme: str, optional
    :param proxy_user: HTTP proxy user 
        (only applicable when `proxy_host` is set)
    :type proxy_user: str, optional
    :param max_results: Max results per HTTP request 
        (defaults to `-1` for no limit, not supported in `server_mode`)
    :type max_results: int, optional
    :param page_limit: Max pages of results that will be returned per resource 
        (defaults to `20`, not supported in `server_mode`)
    :type page_limit: int, optional
    :param max_depth: Max depth for indirect queries: views and subqueries 
        (defaults to `5`, not supported in `server_mode`)
    :type max_depth: int, optional
    :param custom_registry: Custom StackQL provider registry URL 
        (e.g. https://registry-dev.stackql.app/providers) supplied using the class constructor 
    :type custom_registry: str, optional    
    :param custom_auth: Custom StackQL provider authentication object supplied using the class constructor 
        (not supported in `server_mode`)
    :type custom_auth: dict, optional
    :param debug: Enable debug logging 
        (defaults to `False`)
    :type debug: bool, optional
    :param debug_log_file: Path to debug log file 
        (defaults to `~/.pystackql/debug.log`, only available if debug is `True`)
    :type debug_log_file: str, optional

    --- Read-Only Attributes ---
    
    :param platform: The operating system platform
    :type platform: str, readonly
    :param package_version: The version number of the `pystackql` Python package
    :type package_version: str, readonly
    :param version: The version number of the `stackql` executable 
        (not supported in `server_mode`)
    :type version: str, readonly
    :param params: A list of command-line parameters passed to the `stackql` executable 
        (not supported in `server_mode`)
    :type params: list, readonly
    :param bin_path: The full path of the `stackql` executable 
        (not supported in `server_mode`).
    :type bin_path: str, readonly
    :param sha: The commit (short) sha for the installed `stackql` binary build 
        (not supported in `server_mode`).
    :type sha: str, readonly
    """

    def __init__(self, 
                 server_mode=False, 
                 server_address='127.0.0.1', 
                 server_port=5466,
                 output='dict',
                 sep=',',
                 header=False,
                 debug=False,
                 debug_log_file=None,
                **kwargs):
        """Constructor method
        """

        # Get package information from utils
        from ..utils import get_platform, get_package_version
        self.platform, this_os = get_platform()
        self.package_version = get_package_version("pystackql")
        
        # Setup debug logging
        self.debug = debug
        if debug:
            if debug_log_file is None:
                self.debug_log_file = os.path.join(os.path.expanduser("~"), '.pystackql', 'debug.log')
            else:
                self.debug_log_file = debug_log_file
            # Check if the path exists. If not, try to create it.
            log_dir = os.path.dirname(self.debug_log_file)
            if not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except OSError as e:
                    raise ValueError(f"Unable to create the log directory {log_dir}: {str(e)}")
        else:
            self.debug_log_file = None
        
        # Setup output formatter
        self.local_output_formatter = OutputFormatter(output)
        self.output = output.lower()

        # Server mode setup
        self.server_mode = server_mode
        
        if self.server_mode and self.output == 'csv':
            raise ValueError("CSV output is not supported in server mode, use 'dict' or 'pandas' instead.")
        elif self.output == 'csv':
            self.sep = sep
            self.header = header
        
        if self.server_mode:
            # Server mode - connect to a server via the postgres wire protocol
            self.server_address = server_address
            self.server_port = server_port
            self.server_connection = ServerConnection(server_address, server_port)
        else:
            # Local mode - execute the binary locally
            # Get all parameters from local variables (excluding 'self')
            local_params = locals().copy()
            local_params.pop('self')
            
            # Set up local mode - this sets the instance attributes and returns params
            self.params = setup_local_mode(self, **local_params)

            # Initialize query executor
            self.local_query_executor = QueryExecutor(
                self.bin_path, 
                self.params, 
                self.debug, 
                self.debug_log_file
            )
        
        # Initialize async query executor (only for local mode)
        if not self.server_mode:
            self.async_executor = AsyncQueryExecutor(
                self._sync_query_wrapper,
                output_format=self.output
            )        
    
    def _sync_query_wrapper(self, query):
        """Wrapper for synchronous query execution used by AsyncQueryExecutor.
        
        This method is exclusively used for local mode async queries.
        Server mode is not supported for async queries.
        
        Args:
            query (str): The query to execute
                
        Returns:
            The formatted query result
        """
        # Execute query
        query_result = self.local_query_executor.execute(query)
        
        # Format the result using the OutputFormatter
        # This will handle SQL type objects through the _format_data method
        return self.local_output_formatter.format_query_result(query_result)
    
    def properties(self):
        """Retrieves the properties of the StackQL instance.

        This method collects all the attributes of the StackQL instance and
        returns them in a dictionary format.

        :return: A dictionary containing the properties of the StackQL instance.
        :rtype: dict

        Example:
            ::

                {
                    "platform": "Darwin x86_64 (macOS-12.0.1-x86_64-i386-64bit), Python 3.10.9",
                    "output": "dict",
                    ...
                }
        """
        props = {}
        for var in vars(self):
            # Skip internal objects
            if var.startswith('_') or var in ['local_output_formatter', 'local_query_executor', 'async_executor', 'binary_manager', 'server_connection']:
                continue
            props[var] = getattr(self, var)
        return props

    def upgrade(self, showprogress=True):
        """Upgrades the StackQL binary to the latest version available.

        This method initiates an upgrade of the StackQL binary. Post-upgrade,
        it updates the `version` and `sha` attributes of the StackQL instance
        to reflect the newly installed version.

        :param showprogress: Indicates if progress should be displayed during the upgrade. Defaults to True.
        :type showprogress: bool, optional

        :return: A message indicating the new version of StackQL post-upgrade.
        :rtype: str
        """
        if self.server_mode:
            raise ValueError("The upgrade method is not supported in server mode.")
        
        # Use the binary manager to upgrade
        message = self.binary_manager.upgrade(showprogress)
        
        # Update the version and sha attributes
        self.version = self.binary_manager.version
        self.sha = self.binary_manager.sha
        
        return message

    def executeStmt(self, query, custom_auth=None, env_vars=None):
        """Executes a query using the StackQL instance and returns the output as a string.  
            This is intended for operations which do not return a result set, for example a mutation 
            operation such as an `INSERT` or a `DELETE` or life cycle method such as an `EXEC` operation
            or a `REGISTRY PULL` operation.

        This method determines the mode of operation (server_mode or local execution) based 
        on the `server_mode` attribute of the instance. If `server_mode` is True, it runs the query 
        against the server. Otherwise, it executes the query using a subprocess.

        :param query: The StackQL query string to be executed.
        :type query: str, list of dict objects, or Pandas DataFrame
        :param custom_auth: Custom authentication dictionary.
        :type custom_auth: dict, optional
        :param env_vars: Command-specific environment variables for this execution.
        :type env_vars: dict, optional        

        :return: The output result of the query in string format. If in `server_mode`, it 
                returns a JSON string representation of the result. 
        :rtype: dict, Pandas DataFrame or str (for `csv` output)

        Example:
            >>> from pystackql import StackQL
            >>> stackql = StackQL()
            >>> stackql_query = "REGISTRY PULL okta"
            >>> result = stackql.executeStmt(stackql_query)
            >>> result
        """
        if self.server_mode:
            result = self.server_connection.execute_query(query, is_statement=True)
            
            # Format result based on output type
            if self.output == 'pandas':
                import pandas as pd
                return pd.DataFrame(result)
            elif self.output == 'csv':
                # Return the string representation of the result
                return result[0]['message']
            else:
                return result
        else:
            # Execute the query
            result = self.local_query_executor.execute(query, custom_auth=custom_auth, env_vars=env_vars)
            
            # Format the result
            return self.local_output_formatter.format_statement_result(result)
    
    def execute(self, query, suppress_errors=True, custom_auth=None, env_vars=None):
        """
        Executes a StackQL query and returns the output based on the specified output format.

        This method supports execution both in server mode and locally using a subprocess. In server mode,
        the query is sent to a StackQL server, while in local mode, it runs the query using a local binary.

        :param query: The StackQL query string to be executed.
        :type query: str
        :param suppress_errors: If set to True, the method will return an empty list if an error occurs.
        :type suppress_errors: bool, optional
        :param custom_auth: Custom authentication dictionary.
        :type custom_auth: dict, optional        
        :param env_vars: Command-specific environment variables for this execution.
        :type env_vars: dict, optional

        :return: The output of the query, which can be a list of dictionary objects, a Pandas DataFrame, 
                    or a raw CSV string, depending on the configured output format.
        :rtype: list(dict) | pd.DataFrame | str

        :raises ValueError: If an unsupported output format is specified.

        :example:

            >>> stackql = StackQL()
            >>> query = '''
            ... SELECT SPLIT_PART(machineType, '/', -1) as machine_type, status, COUNT(*) as num_instances
            ... FROM google.compute.instances
            ... WHERE project = 'stackql-demo' AND zone = 'australia-southeast1-a'
            ... GROUP BY machine_type, status HAVING COUNT(*) > 2
            ... '''
            >>> result = stackql.execute(query)
        """
        if self.server_mode:
            result = self.server_connection.execute_query(query)
            
            # Format result based on output type
            if self.output == 'pandas':
                import pandas as pd
                import json
                from io import StringIO
                json_str = json.dumps(result)
                return pd.read_json(StringIO(json_str))
            elif self.output == 'csv':
                raise ValueError("CSV output is not supported in server_mode.")
            else:  # Assume 'dict' output
                return result
        else:
            # Apply HTTP debug setting
            if self.http_debug:
                suppress_errors = False
            
            # Execute the query
            output = self.local_query_executor.execute(query, custom_auth=custom_auth, env_vars=env_vars)
            
            # Format the result
            return self.local_output_formatter.format_query_result(output, suppress_errors)

    # async def executeQueriesAsync(self, queries):
    #     """Executes multiple StackQL queries asynchronously using the current StackQL instance.

    #     This method utilizes an asyncio event loop to concurrently run a list of provided 
    #     StackQL queries. Each query is executed independently, and the combined results of 
    #     all the queries are returned as a list of JSON objects if 'dict' output mode is selected,
    #     or as a concatenated DataFrame if 'pandas' output mode is selected.

    #     The order of the results in the returned list or DataFrame may not necessarily 
    #     correspond to the order of the queries in the input list due to the asynchronous nature 
    #     of execution.

    #     :param queries: A list of StackQL query strings to be executed concurrently.
    #     :type queries: list[str], required
    #     :return: A list of results corresponding to each query. Each result is a JSON object or a DataFrame.
    #     :rtype: list[dict] or pd.DataFrame
    #     :raises ValueError: If method is used in `server_mode` on an unsupported OS (anything other than Linux).
    #     :raises ValueError: If an unsupported output mode is selected (anything other than 'dict' or 'pandas').

    #     Example:
    #         >>> from pystackql import StackQL
    #         >>> stackql = StackQL()        
    #         >>> queries = [
    #         >>> \"\"\"SELECT '%s' as region, instanceType, COUNT(*) as num_instances 
    #         ... FROM aws.ec2.instances 
    #         ... WHERE region = '%s' 
    #         ... GROUP BY instanceType\"\"\" % (region, region)
    #         >>> for region in regions ]
    #         >>> result = stackql.executeQueriesAsync(queries)

    #     Note:
    #         - When operating in `server_mode`, this method is not supported.
    #     """
    #     if self.server_mode:
    #         raise ValueError(
    #             "The executeQueriesAsync method is not supported in server mode. "
    #             "Please use the standard execute method with individual queries instead, "
    #             "or switch to local mode if you need to run multiple queries concurrently."
    #         )

    #     return await self.async_executor.execute_queries(queries)
    
    async def executeQueriesAsync(self, queries):
        """Executes multiple StackQL queries asynchronously using the current StackQL instance.

        This method utilizes an asyncio event loop to concurrently run a list of provided 
        StackQL queries. Each query is executed independently, and the combined results of 
        all the queries are returned as a list of JSON objects if 'dict' output mode is selected,
        or as a concatenated DataFrame if 'pandas' output mode is selected.

        The order of the results in the returned list or DataFrame may not necessarily 
        correspond to the order of the queries in the input list due to the asynchronous nature 
        of execution.

        :param queries: A list of StackQL query strings to be executed concurrently.
        :type queries: list[str], required
        :return: A list of results corresponding to each query. Each result is a JSON object or a DataFrame.
        :rtype: list[dict] or pd.DataFrame
        :raises ValueError: If server_mode is True (async is only supported in local mode).
        :raises ValueError: If an unsupported output mode is selected (anything other than 'dict' or 'pandas').

        Example:
            >>> from pystackql import StackQL
            >>> stackql = StackQL()        
            >>> queries = [
            >>> \"\"\"SELECT '%s' as region, instanceType, COUNT(*) as num_instances 
            ... FROM aws.ec2.instances 
            ... WHERE region = '%s' 
            ... GROUP BY instanceType\"\"\" % (region, region)
            >>> for region in regions ]
            >>> result = stackql.executeQueriesAsync(queries)

        Note:
            - This method is only supported in local mode.
        """
        if self.server_mode:
            raise ValueError(
                "The executeQueriesAsync method is not supported in server mode. "
                "Please use the standard execute method with individual queries instead, "
                "or switch to local mode if you need to run multiple queries concurrently."
            )

        # Verify that async_executor is available (should only be initialized in local mode)
        if not hasattr(self, 'async_executor'):
            raise RuntimeError("Async executor not initialized. This should not happen.")

        return await self.async_executor.execute_queries(queries)

    def test_connection(self):
        """Tests if the server connection is working by executing a simple query.
        
        This method is only valid when server_mode=True.
        
        Returns:
            bool: True if the connection is working, False otherwise.
            
        Raises:
            ValueError: If called when not in server mode.
        """
        if not self.server_mode:
            raise ValueError("The test_connectivity method is only available in server mode.")
        
        try:
            result = self.server_connection.execute_query("SELECT 'test' as test_value")
            return (isinstance(result, list) and 
                    len(result) == 1 and 
                    'test_value' in result[0] and 
                    result[0]['test_value'] == 'test')
        except Exception as e:
            if self.debug:
                print(f"Connection test failed: {str(e)}")
            return False
