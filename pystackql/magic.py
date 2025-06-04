# pystackql/magic.py

"""
StackQL Jupyter magic extension (non-server mode).
"""
# Import and re-export the load_ipython_extension function
from .magic_ext.local import load_ipython_extension

# For direct imports (though less common)
from .magic_ext.local import StackqlMagic