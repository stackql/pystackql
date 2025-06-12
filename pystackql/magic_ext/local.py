# pystackql/magic_ext/local.py

"""
Local Jupyter magic extension for PyStackQL.

This module provides a Jupyter magic command for running StackQL queries
using a local StackQL binary.
"""

from IPython.core.magic import magics_class
from .base import BaseStackqlMagic

@magics_class
class StackqlMagic(BaseStackqlMagic):
    """Jupyter magic command for running StackQL queries in local mode."""
    
    def __init__(self, shell):
        """Initialize the StackqlMagic class.
        
        :param shell: The IPython shell instance.
        """
        super().__init__(shell, server_mode=False)

def load_ipython_extension(ipython):
    """Load the non-server magic in IPython.
    
    This is called when running %load_ext pystackql.magic in a notebook.
    It registers the %stackql and %%stackql magic commands.
    
    :param ipython: The IPython shell instance
    """
    # Create an instance of the magic class and register it
    magic_instance = StackqlMagic(ipython)
    ipython.register_magics(magic_instance)