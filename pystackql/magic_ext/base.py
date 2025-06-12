# pystackql/magic_ext/base.py

"""
Base Jupyter magic extension for PyStackQL.

This module provides the base class for PyStackQL Jupyter magic extensions.
"""

from __future__ import print_function
from IPython.core.magic import Magics, line_cell_magic
from string import Template
import argparse

class BaseStackqlMagic(Magics):
    """Base Jupyter magic extension enabling running StackQL queries.

    This extension allows users to conveniently run StackQL queries against cloud 
    or SaaS resources directly from Jupyter notebooks, and visualize the results in a tabular 
    format using Pandas DataFrames.
    """
    def __init__(self, shell, server_mode):
        """Initialize the BaseStackqlMagic class.

        :param shell: The IPython shell instance.
        :param server_mode: Whether to use server mode.
        """
        from ..core import StackQL
        super(BaseStackqlMagic, self).__init__(shell)
        self.stackql_instance = StackQL(server_mode=server_mode, output='pandas')
        self.server_mode = server_mode
          
    def get_rendered_query(self, data):
        """Substitute placeholders in a query template with variables from the current namespace.
        
        :param data: SQL query template containing placeholders.
        :type data: str
        :return: A SQL query with placeholders substituted.
        :rtype: str
        """
        t = Template(data)
        return t.substitute(self.shell.user_ns)

    def run_query(self, query):
        """Execute a StackQL query
        
        :param query: StackQL query to be executed.
        :type query: str
        :return: Query results, returned as a Pandas DataFrame.
        :rtype: pandas.DataFrame
        """
        # Check if the query starts with "registry pull" (case insensitive)
        if query.strip().lower().startswith("registry pull"):
            return self.stackql_instance.executeStmt(query)
        
        return self.stackql_instance.execute(query)
    
    @line_cell_magic
    def stackql(self, line, cell=None):
        """A Jupyter magic command to run StackQL queries.
        
        Can be used as both line and cell magic:
        - As a line magic: `%stackql QUERY`
        - As a cell magic: `%%stackql [OPTIONS]` followed by the QUERY in the next line.
        
        :param line: The arguments and/or StackQL query when used as line magic.
        :param cell: The StackQL query when used as cell magic.
        :return: StackQL query results as a named Pandas DataFrame (`stackql_df`).
        """
        is_cell_magic = cell is not None

        if is_cell_magic:
            parser = argparse.ArgumentParser()
            parser.add_argument("--no-display", action="store_true", help="Suppress result display.")
            parser.add_argument("--csv-download", action="store_true", help="Add CSV download link to output.")
            args = parser.parse_args(line.split())
            query_to_run = self.get_rendered_query(cell)
        else:
            args = None
            query_to_run = self.get_rendered_query(line)

        results = self.run_query(query_to_run)
        self.shell.user_ns['stackql_df'] = results

        if is_cell_magic and args and args.no_display:
            return None
        elif is_cell_magic and args and args.csv_download and not args.no_display:
            # First display the DataFrame 
            import IPython.display
            IPython.display.display(results)
            # Then add the download button without displaying the DataFrame again
            self._display_with_csv_download(results)
            return results
        elif is_cell_magic and args and not args.no_display:
            return results
        elif not is_cell_magic:
            return results
        else:
            return results
    
    def _display_with_csv_download(self, df):
        """Display a CSV download link for the DataFrame without displaying the DataFrame again.
        
        :param df: The DataFrame to make downloadable.
        """
        import IPython.display
        
        try:
            # Generate CSV data
            import io
            import base64
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Encode to base64 for data URI
            csv_base64 = base64.b64encode(csv_data.encode()).decode()
            
            # Create download link
            download_link = f'data:text/csv;base64,{csv_base64}'
            
            # Only display the download button, not the DataFrame
            download_html = f'''
            <div style="margin-top: 15px; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;">
                <a href="{download_link}" download="stackql_results.csv" 
                style="display: inline-flex; align-items: center; gap: 8px; padding: 9px 16px; 
                        background-color: #2196F3; color: white; text-decoration: none; 
                        border-radius: 4px; font-size: 14px; font-weight: 500; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08); transition: all 0.2s ease;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download CSV
                </a>
            </div>
            '''
            IPython.display.display(IPython.display.HTML(download_html))
            
        except Exception as e:
            # If CSV generation fails, just print an error message without displaying anything
            print(f"Error generating CSV download: {e}")