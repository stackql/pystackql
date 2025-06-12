# # pystackql/magic_ext/server.py

# """
# Server Jupyter magic extension for PyStackQL.

# This module provides a Jupyter magic command for running StackQL queries
# using a StackQL server connection.
# """

# from IPython.core.magic import (magics_class, line_cell_magic)
# from IPython.display import display, HTML
# from .base import BaseStackqlMagic
# import argparse
# import base64
# import io

# @magics_class
# class StackqlServerMagic(BaseStackqlMagic):
#     """Jupyter magic command for running StackQL queries in server mode."""
    
#     def __init__(self, shell):
#         """Initialize the StackqlServerMagic class.
        
#         :param shell: The IPython shell instance.
#         """
#         super().__init__(shell, server_mode=True)

#     @line_cell_magic
#     def stackql(self, line, cell=None):
#         """A Jupyter magic command to run StackQL queries.
        
#         Can be used as both line and cell magic:
#         - As a line magic: `%stackql QUERY`
#         - As a cell magic: `%%stackql [OPTIONS]` followed by the QUERY in the next line.
        
#         :param line: The arguments and/or StackQL query when used as line magic.
#         :param cell: The StackQL query when used as cell magic.
#         :return: StackQL query results as a named Pandas DataFrame (`stackql_df`).
#         """
#         is_cell_magic = cell is not None

#         if is_cell_magic:
#             parser = argparse.ArgumentParser()
#             parser.add_argument("--no-display", action="store_true", help="Suppress result display.")
#             parser.add_argument("--csv-download", action="store_true", help="Add CSV download link to output.")
#             args = parser.parse_args(line.split())
#             query_to_run = self.get_rendered_query(cell)
#         else:
#             args = None
#             query_to_run = self.get_rendered_query(line)

#         results = self.run_query(query_to_run)
#         self.shell.user_ns['stackql_df'] = results

#         if is_cell_magic and args and args.no_display:
#             return None
#         elif is_cell_magic and args and args.csv_download and not args.no_display:
#             self._display_with_csv_download(results)
#             return results
#         elif is_cell_magic and args and not args.no_display:
#             return results
#         elif not is_cell_magic:
#             return results
#         else:
#             return results

#     def _display_with_csv_download(self, df):
#         """Display DataFrame with CSV download link.
        
#         :param df: The DataFrame to display and make downloadable.
#         """
#         import IPython.display
        
#         try:
#             # Generate CSV data
#             import io
#             import base64
#             csv_buffer = io.StringIO()
#             df.to_csv(csv_buffer, index=False)
#             csv_data = csv_buffer.getvalue()
            
#             # Encode to base64 for data URI
#             csv_base64 = base64.b64encode(csv_data.encode()).decode()
            
#             # Create download link
#             download_link = f'data:text/csv;base64,{csv_base64}'
            
#             # Display the DataFrame first
#             IPython.display.display(df)
            
#             # Create and display the download button
#             download_html = f'''
#             <div style="margin-top: 10px;">
#                 <a href="{download_link}" download="stackql_results.csv" 
#                    style="display: inline-block; padding: 8px 16px; background-color: #007cba; 
#                           color: white; text-decoration: none; border-radius: 4px; 
#                           font-family: Arial, sans-serif; font-size: 14px; border: none; cursor: pointer;">
#                     📥 Download CSV
#                 </a>
#             </div>
#             '''
#             IPython.display.display(IPython.display.HTML(download_html))
            
#         except Exception as e:
#             # If CSV generation fails, just display the DataFrame normally
#             IPython.display.display(df)
#             print(f"Error generating CSV download: {e}")
        
# def load_ipython_extension(ipython):
#     """Load the server magic in IPython."""
#     # Create an instance of the magic class and register it
#     magic_instance = StackqlServerMagic(ipython)
#     ipython.register_magics(magic_instance)

# pystackql/magic_ext/server.py

"""
Server Jupyter magic extension for PyStackQL.

This module provides a Jupyter magic command for running StackQL queries
using a StackQL server connection.
"""

from IPython.core.magic import (magics_class, line_cell_magic)
from .base import BaseStackqlMagic
import argparse

@magics_class
class StackqlServerMagic(BaseStackqlMagic):
    """Jupyter magic command for running StackQL queries in server mode."""
    
    def __init__(self, shell):
        """Initialize the StackqlServerMagic class.
        
        :param shell: The IPython shell instance.
        """
        super().__init__(shell, server_mode=True)

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
            self._display_with_csv_download(results)
            return results
        elif is_cell_magic and args and not args.no_display:
            return results
        elif not is_cell_magic:
            return results
        else:
            return results

def load_ipython_extension(ipython):
    """Load the server magic in IPython."""
    # Create an instance of the magic class and register it
    magic_instance = StackqlServerMagic(ipython)
    ipython.register_magics(magic_instance)