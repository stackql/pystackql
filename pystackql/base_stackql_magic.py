from __future__ import print_function
import pandas as pd
import json, argparse
from IPython.core.magic import (Magics, line_cell_magic)
from string import Template

class BaseStackqlMagic(Magics):
    """Base Jupyter magic extension enabling running StackQL queries.

    This extension allows users to conveniently run StackQL queries against cloud 
    or SaaS reources directly from Jupyter notebooks, and visualize the results in a tabular 
    format using Pandas DataFrames.
    """
    def __init__(self, shell, server_mode):
        """Initialize the StackqlMagic class.

        :param shell: The IPython shell instance.
        """
        from . import StackQL
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