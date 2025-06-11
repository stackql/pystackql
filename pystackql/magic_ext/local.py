# pystackql/magic_ext/local.py

"""
Local Jupyter magic extension for PyStackQL.

This module provides a Jupyter magic command for running StackQL queries
using a local StackQL binary.
"""

from IPython.core.magic import (magics_class, line_cell_magic)
from .base import BaseStackqlMagic
import argparse
import base64
from IPython.display import HTML, display

@magics_class
class StackqlMagic(BaseStackqlMagic):
    """Jupyter magic command for running StackQL queries in local mode."""
    
    def __init__(self, shell):
        """Initialize the StackqlMagic class.
        
        :param shell: The IPython shell instance.
        """
        super().__init__(shell, server_mode=False)

    @line_cell_magic
    def stackql(self, line, cell=None):
        """A Jupyter magic command to run StackQL queries.
        
        Can be used as both line and cell magic:
        - As a line magic: `%stackql QUERY`
        - As a cell magic: `%%stackql [OPTIONS]` followed by the QUERY in the next line.
        
        Available options for cell magic:
        - --no-display: Suppress result display
        - --csv-download: Add CSV download link to output (only works when --no-display is not set)
        
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

        if is_cell_magic and args and not args.no_display:
            if args.csv_download:
                # Display the DataFrame and CSV download link
                display(results)
                self._display_csv_download_link(results)
                return None
            else:
                return results
        elif not is_cell_magic:
            return results

    def _display_csv_download_link(self, dataframe):
        """Generate and display a CSV download link for the DataFrame.
        
        :param dataframe: The Pandas DataFrame to convert to CSV.
        """
        try:
            # Convert DataFrame to CSV string
            csv_content = dataframe.to_csv(index=False)
            
            # Encode the CSV content as base64 for data URI
            csv_base64 = base64.b64encode(csv_content.encode()).decode()
            
            # Create HTML download link
            download_html = f'''
            <div style="margin-top: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;">
                <strong>Download Options:</strong><br>
                <a href="data:text/csv;base64,{csv_base64}" 
                   download="stackql_results.csv" 
                   style="display: inline-block; margin-top: 5px; padding: 5px 10px; 
                          background-color: #007cba; color: white; text-decoration: none; 
                          border-radius: 3px; font-size: 12px;">
                    📁 Download as CSV
                </a>
            </div>
            '''
            
            # Display the HTML
            display(HTML(download_html))
            
        except Exception as e:
            # If there's an error generating the CSV, display a simple message
            error_html = f'''
            <div style="margin-top: 10px; padding: 10px; border: 1px solid #ff6b6b; border-radius: 5px; background-color: #ffe0e0;">
                <strong>CSV Download Error:</strong> {str(e)}
            </div>
            '''
            display(HTML(error_html))

def load_ipython_extension(ipython):
    """Load the non-server magic in IPython.
    
    This is called when running %load_ext pystackql.magic in a notebook.
    It registers the %stackql and %%stackql magic commands.
    
    :param ipython: The IPython shell instance
    """
    # Create an instance of the magic class and register it
    magic_instance = StackqlMagic(ipython)
    ipython.register_magics(magic_instance)