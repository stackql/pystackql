# pystackql/magic_ext/base.py

"""
Base Jupyter magic extension for PyStackQL.

This module provides the base class for PyStackQL Jupyter magic extensions.
"""

from __future__ import print_function
from IPython.core.magic import Magics
from string import Template

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
    
    def _display_with_csv_download(self, df):
        """Display DataFrame with CSV download link.
        
        :param df: The DataFrame to display and make downloadable.
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
            
            # Display the DataFrame first
            IPython.display.display(df)
            
            # # Create and display the download button
            # download_html = f'''
            # <div style="margin-top: 10px;">
            #     <a href="{download_link}" download="stackql_results.csv" 
            #        style="display: inline-block; padding: 8px 16px; background-color: #007cba; 
            #               color: white; text-decoration: none; border-radius: 4px; 
            #               font-family: Arial, sans-serif; font-size: 14px; border: none; cursor: pointer;">
            #         📥 Download CSV
            #     </a>
            # </div>
            # '''

            # Create and display the download button
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
            # If CSV generation fails, just display the DataFrame normally
            IPython.display.display(df)
            print(f"Error generating CSV download: {e}")