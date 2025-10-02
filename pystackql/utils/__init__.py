# pystackql/utils/__init__.py

"""
Utility functions for PyStackQL package.
"""
from .package import get_package_version

from .platform import (
    get_platform,
    is_binary_local
)

from .binary import (
    get_binary_name,
    get_binary_version,
    setup_binary
)

from .download import (
    get_download_dir,
    get_download_url,
    download_file
)

from .auth import format_auth
from .params import setup_local_mode, generate_params_for_execution

__all__ = [
    # Platform utilities
    'get_platform',
    'get_package_version',
    'is_binary_local',
    
    # Binary utilities
    'get_binary_name',
    'get_binary_version',
    'setup_binary',
    
    # Download utilities
    'get_download_dir',
    'get_download_url',
    'download_file',
    
    # Auth utilities
    'format_auth',
    
    # Parameter utilities
    'setup_local_mode',
    'generate_params_for_execution'
]