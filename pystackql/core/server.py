# pystackql/core/server.py

"""
Server connection management for PyStackQL.

This module handles connections to a StackQL server using the Postgres wire protocol.
"""

class ServerConnection:
    """Manages connections to a StackQL server.
    
    This class handles connecting to and querying a StackQL server
    using the Postgres wire protocol.
    """
    
    def __init__(self, server_address='127.0.0.1', server_port=5466):
        """Initialize the ServerConnection.
        
        Args:
            server_address (str, optional): Address of the server. Defaults to '127.0.0.1'.
            server_port (int, optional): Port of the server. Defaults to 5466.
        """
        self.server_address = server_address
        self.server_port = server_port
        self._conn = None
        
        # Import psycopg on demand to avoid dependency issues
        try:
            global psycopg, dict_row
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise ImportError("psycopg is required in server mode but is not installed. "
                             "Please install psycopg and try again.")
        
        # Connect to the server
        self._connect()
    
    def _connect(self):
        """Connect to the StackQL server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._conn = psycopg.connect(
                dbname='stackql',
                user='stackql',
                host=self.server_address,
                port=self.server_port,
                autocommit=True,
                row_factory=dict_row
            )
            return True
        except psycopg.OperationalError as oe:
            print(f"OperationalError while connecting to the server: {oe}")
        except Exception as e:
            print(f"Unexpected error while connecting to the server: {e}")
        return False
    
    def is_connected(self):
        """Check if the connection to the server is active.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._conn is not None and not self._conn.closed
    
    def ensure_connected(self):
        """Ensure the connection to the server is active.
        
        If the connection is closed, attempt to reconnect.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.is_connected():
            return self._connect()
        return True
    
    def execute_query(self, query, is_statement=False):
        """Execute a query on the server.
        
        Args:
            query (str): The query to execute
            is_statement (bool, optional): Whether this is a statement (non-SELECT). Defaults to False.
            
        Returns:
            list: Results of the query as a list of dictionaries
            
        Raises:
            ConnectionError: If no active connection is available
        """
        if not self.ensure_connected():
            raise ConnectionError("No active connection to the server")
        
        try:
            with self._conn.cursor() as cur:
                cur.execute(query)
                if is_statement:
                    # Return status message for non-SELECT statements
                    result_msg = cur.statusmessage
                    return [{'message': result_msg}]
                try:
                    # Fetch results for SELECT queries
                    rows = cur.fetchall()
                    return rows
                except psycopg.ProgrammingError as e:
                    # Handle cases with no results
                    if "no results to fetch" in str(e):
                        return []
                    else:
                        raise
        except psycopg.OperationalError as oe:
            print(f"OperationalError during query execution: {oe}")
            # Try to reconnect and retry once
            if self._connect():
                return self.execute_query(query, is_statement)
        except Exception as e:
            print(f"Unexpected error during query execution: {e}")
        
        return []
    
    def execute_query_with_new_connection(self, query):
        """Execute a query with a new connection.
        
        This method creates a new connection to the server, executes the query,
        and then closes the connection.
        
        Args:
            query (str): The query to execute
            
        Returns:
            list: Results of the query as a list of dictionaries
        """
        try:
            with psycopg.connect(
                dbname='stackql',
                user='stackql',
                host=self.server_address,
                port=self.server_port,
                row_factory=dict_row
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    try:
                        rows = cur.fetchall()
                    except psycopg.ProgrammingError as e:
                        if str(e) == "no results to fetch":
                            rows = []
                        else:
                            raise
                    return rows
        except psycopg.OperationalError as oe:
            print(f"OperationalError while connecting to the server: {oe}")
        except Exception as e:
            print(f"Unexpected error while connecting to the server: {e}")
        
        return []
    
    def close(self):
        """Close the connection to the server."""
        if self._conn and not self._conn.closed:
            self._conn.close()