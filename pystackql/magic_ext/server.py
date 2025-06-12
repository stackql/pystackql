# pystackql/magic_ext/server.py

"""
Server Jupyter magic extension for PyStackQL.

This module provides a Jupyter magic command for running StackQL queries
using a StackQL server connection.
"""

from IPython.core.magic import magics_class
from .base import BaseStackqlMagic

@magics_class
class StackqlServerMagic(BaseStackqlMagic):
    """Jupyter magic command for running StackQL queries in server mode."""
    
    def __init__(self, shell):
        """Initialize the StackqlServerMagic class.
        
        :param shell: The IPython shell instance.
        """
        super().__init__(shell, server_mode=True)

def load_ipython_extension(ipython):
    """Load the server magic in IPython."""
    # Create an instance of the magic class and register it
    magic_instance = StackqlServerMagic(ipython)
    ipython.register_magics(magic_instance)