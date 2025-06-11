# pystackql/core/binary.py

"""
Binary management module for PyStackQL.

This module handles the installation, version checking, and management
of the StackQL binary executable.
"""

import os
from ..utils import (
    is_binary_local,
    get_platform,
    get_download_dir,
    get_binary_name,
    setup_binary,
    get_binary_version
)

class BinaryManager:
    """Manages the StackQL binary installation and versions.
    
    This class is responsible for ensuring the StackQL binary is available
    and correctly configured for use.
    """
    
    def __init__(self, download_dir=None):
        """Initialize the BinaryManager.
        
        Args:
            download_dir (str, optional): Directory to store the binary. Defaults to None.
        """
        self.platform_info, self.system = get_platform()
        
        # Determine binary location
        if self.system == 'Linux' and is_binary_local(self.system) and download_dir is None:
            self.bin_path = '/usr/local/bin/stackql'
            self.download_dir = '/usr/local/bin'
        else:
            # Use provided download_dir or default
            self.download_dir = download_dir if download_dir else get_download_dir()
            self.bin_path = os.path.join(self.download_dir, get_binary_name(self.system))
        
        # Check if binary exists and get version
        self._ensure_binary_exists()
        
    def _ensure_binary_exists(self):
        """Ensure the binary exists, download it if not."""
        if os.path.exists(self.bin_path):
            # Binary exists, get version
            self.version, self.sha = get_binary_version(self.bin_path)
        else:
            # Binary doesn't exist, download it
            setup_binary(self.download_dir, self.system)
            self.version, self.sha = get_binary_version(self.bin_path)
    
    def upgrade(self, showprogress=True):
        """Upgrade the StackQL binary to the latest version.
        
        Args:
            showprogress (bool, optional): Whether to show download progress. Defaults to True.
            
        Returns:
            str: A message indicating the new version
        """
        setup_binary(self.download_dir, self.system, showprogress)
        self.version, self.sha = get_binary_version(self.bin_path)
        return f"stackql upgraded to version {self.version}"
    
    def get_version_info(self):
        """Get the version information for the binary.
        
        Returns:
            dict: Version information including version and sha
        """
        return {
            "version": self.version,
            "sha": self.sha
        }