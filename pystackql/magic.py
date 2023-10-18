# `%load_ext pystackql.magic` - loads the stackql magic with server_mode=False
from IPython.core.magic import (magics_class, line_cell_magic)
from .base_stackql_magic import BaseStackqlMagic
import argparse

@magics_class
class StackqlMagic(BaseStackqlMagic):
    def __init__(self, shell):
        super().__init__(shell, server_mode=False)

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

def load_ipython_extension(ipython):
    """Load the non-server magic in IPython."""
    ipython.register_magics(StackqlMagic)
