# pystackql/utils/platform.py

"""
Platform-related utility functions for PyStackQL.

This module contains functions for platform detection and package information.
"""

import os
import platform

def is_binary_local(system_platform):
    """Checks if the binary exists at the specified local path.
    
    Args:
        system_platform (str): The operating system platform
        
    Returns:
        bool: True if the binary exists at the expected local path
    """
    if system_platform == 'Linux' and os.path.exists('/usr/local/bin/stackql'):
        return True
    return False

def get_platform():
    """Gets the current platform information.
    
    Returns:
        tuple: (platform_string, system_value)
            - platform_string: A string with platform details
            - system_value: The operating system name
    """
    system_val = platform.system()
    machine_val = platform.machine()
    platform_val = platform.platform()
    python_version_val = platform.python_version()
    return (
        f"{system_val} {machine_val} ({platform_val}), Python {python_version_val}", 
        system_val
    )