# `%load_ext pystackql.magics`  - loads the stackql magic with server_mode=True
from IPython.core.magic import magics_class
from .base_stackql_magic import BaseStackqlMagic

@magics_class
class StackqlServerMagic(BaseStackqlMagic):
    def __init__(self, shell):
        super().__init__(shell, server_mode=True)

def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(StackqlServerMagic)