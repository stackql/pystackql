from __future__ import print_function
import pandas as pd
import json, argparse
from IPython.core.magic import (Magics, magics_class, line_cell_magic)
from string import Template

@magics_class
class StackqlMagic(Magics):
    """
    A Jupyter magic extension enabling SQL querying against a StackQL database.
    
    This extension allows users to conveniently run SQL queries against the StackQL 
    database directly from Jupyter notebooks, and visualize the results in a tabular 
    format using Pandas DataFrames.
    """

    def __init__(self, shell):
        """
        Initialize the StackqlMagic class.
        
        :param shell: The IPython shell instance.
        """
        from . import StackQL
        super(StackqlMagic, self).__init__(shell)
        self.stackql_instance = StackQL(server_mode=True, output='pandas')

    def get_rendered_query(self, data):
        """
        Substitute placeholders in a query template with variables from the current namespace.
        
        :param data: SQL query template containing placeholders.
        :type data: str
        :return: A SQL query with placeholders substituted.
        :rtype: str
        """
        t = Template(data)
        return t.substitute(self.shell.user_ns)

    def run_query(self, query):
        """
        Execute a StackQL query
        
        :param query: StackQL query to be executed.
        :type query: str
        :return: Query results, returned as a Pandas DataFrame.
        :rtype: pandas.DataFrame
        """
        return self.stackql_instance.execute(query)
    
    @line_cell_magic
    def stackql(self, line, cell=None):
        """
        A Jupyter magic command to run SQL queries against the StackQL database.
        
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
            args = parser.parse_args(line.split())
            query_to_run = self.get_rendered_query(cell)
        else:
            args = None
            query_to_run = self.get_rendered_query(line)

        results = self.run_query(query_to_run)
        self.shell.user_ns['stackql_df'] = results

        if is_cell_magic and args and not args.no_display:
            return results
        elif not is_cell_magic:
            return results

def load_ipython_extension(ipython):
    """
    Enable the StackqlMagic extension in IPython.
    
    This function allows the extension to be loaded via the `%load_ext` command or 
    be automatically loaded by IPython at startup.
    """
    ipython.register_magics(StackqlMagic)
