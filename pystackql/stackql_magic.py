# stackql_magic.py
from IPython.core.magic import magics_class
from .base_stackql_magic import BaseStackqlMagic

@magics_class
class StackqlMagic(BaseStackqlMagic):
    def __init__(self, shell):
        super().__init__(shell, server_mode=False)

def load_non_server_magic(ipython):
    """Load the non-server magic in IPython."""
    ipython.register_magics(StackqlMagic)
