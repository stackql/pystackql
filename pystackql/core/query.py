# pystackql/core/query.py

"""
Query execution module for PyStackQL.

This module handles the execution of StackQL queries via the binary or server.
"""

import json
import os
import shlex
import subprocess
import tempfile
from io import StringIO
import asyncio
from concurrent.futures import ThreadPoolExecutor

class QueryExecutor:
    """Executes StackQL queries using a subprocess.
    
    This class is responsible for executing StackQL queries using either
    a local binary or a server connection.
    """
    
    def __init__(self, binary_path, params=None, debug=False, debug_log_file=None):
        """Initialize the QueryExecutor.
        
        Args:
            binary_path (str): Path to the StackQL binary
            params (list, optional): Additional parameters for the binary. Defaults to None.
            debug (bool, optional): Whether to enable debug logging. Defaults to False.
            debug_log_file (str, optional): Path to debug log file. Defaults to None.
        """
        self.bin_path = binary_path
        self.params = params or []
        self.debug = debug
        self.debug_log_file = debug_log_file
        
        # Determine platform for command formatting
        import platform
        self.platform = platform.system()
    
    def _debug_log(self, message):
        """Log a debug message.
        
        Args:
            message (str): The message to log
        """
        if self.debug and self.debug_log_file:
            with open(self.debug_log_file, "a") as log_file:
                log_file.write(message + "\n")
    
    def execute(self, query, custom_auth=None, env_vars=None):
        """Execute a StackQL query.
        
        Args:
            query (str): The query to execute
            custom_auth (dict, optional): Custom authentication dictionary. Defaults to None.
            env_vars (dict, optional): Environment variables for the subprocess. Defaults to None.
            
        Returns:
            dict: The query results
        """
        local_params = self.params.copy()
        script_path = None

        # Format query for platform
        if self.platform.startswith("Windows"):
            # Escape double quotes and wrap in double quotes for Windows
            escaped_query = query.replace('"', '\\"')
            safe_query = f'"{escaped_query}"'
        else:
            # Use shlex.quote for Unix-like systems
            safe_query = shlex.quote(query)

        local_params.insert(1, safe_query)
        
        # Handle custom authentication if provided
        if custom_auth:
            if '--auth' in local_params:
                # override auth set in the constructor with the command-specific auth
                auth_index = local_params.index('--auth')
                local_params.pop(auth_index)  # remove --auth
                local_params.pop(auth_index)  # remove the auth string
            authstr = json.dumps(custom_auth)
            local_params.extend(["--auth", f"'{authstr}'"])

        output = {}
        env_command_prefix = ""

        # Determine platform and set environment command prefix accordingly
        if env_vars:
            if self.platform.startswith("Windows"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w") as script_file:
                    # Write environment variable setup and command to script file
                    for key, value in env_vars.items():
                        script_file.write(f'$env:{key} = "{value}";\n')
                    script_file.write(f"{self.bin_path} " + " ".join(local_params) + "\n")
                    script_path = script_file.name
                full_command = f"powershell -File {script_path}"
            else:
                # For Linux/Mac, use standard env variable syntax
                env_command_prefix = "env " + " ".join([f'{key}="{value}"' for key, value in env_vars.items()]) + " "
                full_command = env_command_prefix + " ".join([self.bin_path] + local_params)
        else:
            full_command = " ".join([self.bin_path] + local_params)

        try:
            # Replace newlines to ensure command works in shell
            full_command = full_command.replace("\n", " ")

            # Execute the command
            result = subprocess.run(
                full_command,
                shell=True,
                text=True,
                capture_output=True
            )

            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode

            # Log debug information if enabled
            if self.debug:
                self._debug_log(f"fullcommand: {full_command}")
                self._debug_log(f"returncode: {returncode}")
                self._debug_log(f"stdout: {stdout}")
                self._debug_log(f"stderr: {stderr}")

            # Process stdout and stderr
            if stderr:
                output["error"] = stderr.decode('utf-8') if isinstance(stderr, bytes) else str(stderr)
            if stdout:
                output["data"] = stdout.decode('utf-8') if isinstance(stdout, bytes) else str(stdout)

        except FileNotFoundError:
            output["exception"] = f"ERROR: {self.bin_path} not found"
        except Exception as e:
            error_details = {
                "exception": str(e),
                "doc": e.__doc__,
                "params": local_params,
                "stdout": stdout.decode('utf-8') if 'stdout' in locals() and isinstance(stdout, bytes) else "",
                "stderr": stderr.decode('utf-8') if 'stderr' in locals() and isinstance(stderr, bytes) else ""
            }
            output["exception"] = f"ERROR: {json.dumps(error_details)}"
        finally:
            # Clean up the temporary script file
            if script_path is not None:
                os.remove(script_path) 
            return output


class AsyncQueryExecutor:
    """Executes StackQL queries asynchronously.
    
    This class provides methods for executing multiple StackQL queries
    concurrently using asyncio.
    """
    
    def __init__(self, sync_query_func, server_mode=False, output_format='dict'):
        """Initialize the AsyncQueryExecutor.
        
        Args:
            sync_query_func (callable): Function to execute a single query synchronously
            server_mode (bool, optional): Whether to use server mode. Defaults to False.
            output_format (str, optional): Output format (dict or pandas). Defaults to 'dict'.
        """
        self.sync_query_func = sync_query_func
        self.server_mode = server_mode
        self.output_format = output_format
    
    async def execute_queries(self, queries):
        """Execute multiple queries asynchronously.
        
        Args:
            queries (list): List of query strings to execute
            
        Returns:
            list or DataFrame: Results of all queries
            
        Raises:
            ValueError: If output_format is not supported
        """
        if self.output_format not in ['dict', 'pandas']:
            raise ValueError("executeQueriesAsync supports only 'dict' or 'pandas' output modes.")
        
        async def main():
            with ThreadPoolExecutor() as executor:
                # New connection is created for each query in server_mode, reused otherwise
                new_connection = self.server_mode
                
                # Create tasks for each query
                loop = asyncio.get_event_loop()
                futures = [
                    loop.run_in_executor(
                        executor, 
                        lambda q=query: self.sync_query_func(q, new_connection),
                        # Pass query as a default argument to avoid late binding issues
                    ) 
                    for query in queries
                ]
                
                # Gather results from all the async calls
                results = await asyncio.gather(*futures)
                
            return results
        
        # Run the async function and process results
        results = await main()
        
        # Process results based on output format
        if self.output_format == 'pandas':
            import pandas as pd
            return pd.concat(results, ignore_index=True)
        else:
            # Flatten the list of results
            return [item for sublist in results for item in sublist]