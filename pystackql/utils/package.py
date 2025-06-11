# pystackql/utils/package.py

"""
Package related utility functions for PyStackQL.

"""

# Conditional import for package metadata retrieval
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # This is for Python versions earlier than 3.8
    from importlib_metadata import version, PackageNotFoundError

def get_package_version(package_name):
    """Gets the version of the specified package.
    
    Args:
        package_name (str): The name of the package
        
    Returns:
        str: The version of the package or None if not found
    """
    try:
        pkg_version = version(package_name)
        if pkg_version is None:
            print(f"Warning: Retrieved version for '{package_name}' is None!")
        return pkg_version
    except PackageNotFoundError:
        print(f"Warning: Package '{package_name}' not found!")
        return None
