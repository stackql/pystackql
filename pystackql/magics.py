# pystackql/magics.py

"""
StackQL Jupyter magic extension (server mode).
"""
# Import and re-export the load_ipython_extension function
from .magic_ext.server import load_ipython_extension

# For direct imports (though less common)
from .magic_ext.server import StackqlServerMagic