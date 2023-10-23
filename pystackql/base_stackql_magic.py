from __future__ import print_function
from IPython.core.magic import (Magics)
from string import Template
import pandas as pd

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
        # Check if the query starts with "registry pull" (case insensitive)
        if query.strip().lower().startswith("registry pull"):
            return self.stackql_instance.executeStmt(query)
        
        return self.stackql_instance.execute(query)
