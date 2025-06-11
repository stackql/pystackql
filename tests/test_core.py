# tests/test_core.py

"""
Core functionality tests for PyStackQL.

This module tests the basic attributes and properties of the StackQL class.
"""

import os
import re
import sys
import platform
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add the current directory to the path so we can import test_constants
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pystackql import StackQL
from tests.test_constants import (
    EXPECTED_PROPERTIES, 
    EXPECTED_VERSION_PATTERN, 
    EXPECTED_PACKAGE_VERSION_PATTERN,
    EXPECTED_PLATFORM_PATTERN,
    get_custom_download_dir,
    print_test_result,
    pystackql_test_setup
)

class TestStackQLCore:
    """Tests for core PyStackQL functionality."""
    
    StackQL = StackQL  # For use with pystackql_test_setup decorator
    
    @pystackql_test_setup()
    def test_properties_method(self):
        """Test that the properties() method returns the expected properties."""
        properties = self.stackql.properties()
        
        # Check that properties is a dictionary
        assert isinstance(properties, dict), "properties should be a dictionary"
        
        # Check that all expected properties are present
        missing_keys = [key for key in EXPECTED_PROPERTIES if key not in properties]
        assert len(missing_keys) == 0, f"Missing keys in properties: {', '.join(missing_keys)}"
        
        # Check property types
        assert isinstance(properties["bin_path"], str), "bin_path should be of type str"
        assert isinstance(properties["params"], list), "params should be of type list"
        assert isinstance(properties["server_mode"], bool), "server_mode should be of type bool"
        assert isinstance(properties["output"], str), "output should be of type str"
        
        print_test_result(f"Properties method test\nPROPERTIES: {properties}", True)
    
    @pystackql_test_setup()
    def test_version_attribute(self):
        """Test that the version attribute contains a valid version string."""
        version = self.stackql.version
        assert version is not None, "version should not be None"
        
        is_valid_semver = bool(re.match(EXPECTED_VERSION_PATTERN, version))
        assert is_valid_semver, f"version '{version}' does not match expected pattern"
        
        print_test_result(f"Version attribute test\nVERSION: {version}", is_valid_semver)
    
    @pystackql_test_setup()
    def test_package_version_attribute(self):
        """Test that the package_version attribute contains a valid version string."""
        package_version = self.stackql.package_version
        assert package_version is not None, "package_version should not be None"
        
        is_valid_semver = bool(re.match(EXPECTED_PACKAGE_VERSION_PATTERN, package_version))
        assert is_valid_semver, f"package_version '{package_version}' does not match expected pattern"
        
        print_test_result(f"Package version attribute test\nPACKAGE VERSION: {package_version}", is_valid_semver)
    
    @pystackql_test_setup()
    def test_platform_attribute(self):
        """Test that the platform attribute contains valid platform information."""
        platform_string = self.stackql.platform
        assert platform_string is not None, "platform should not be None"
        
        is_valid_platform = bool(re.match(EXPECTED_PLATFORM_PATTERN, platform_string))
        assert is_valid_platform, f"platform '{platform_string}' does not match expected pattern"
        
        print_test_result(f"Platform attribute test\nPLATFORM: {platform_string}", is_valid_platform)
    
    @pystackql_test_setup()
    def test_bin_path_attribute(self):
        """Test that the bin_path attribute points to an existing binary."""
        assert os.path.exists(self.stackql.bin_path), f"Binary not found at {self.stackql.bin_path}"
        
        print_test_result(f"Binary path attribute test\nBINARY PATH: {self.stackql.bin_path}", 
                          os.path.exists(self.stackql.bin_path))
    
    @pystackql_test_setup(download_dir=get_custom_download_dir())
    def test_custom_download_dir(self):
        """Test that a custom download_dir is used correctly."""
        # Check that version is not None (binary was found)
        version = self.stackql.version
        assert version is not None, "version should not be None"
        
        # Check that the binary exists at the expected location in the custom directory
        expected_download_dir = get_custom_download_dir()
        binary_name = 'stackql' if platform.system().lower() != 'windows' else 'stackql.exe'
        expected_binary_path = os.path.join(expected_download_dir, binary_name)
        
        # Check if binary exists
        if not os.path.exists(expected_binary_path):
            # Give it time to download if needed
            import time
            time.sleep(5)
        
        assert os.path.exists(expected_binary_path), f"No binary found at {expected_binary_path}"
        
        print_test_result(f"Custom download directory test\nCUSTOM_DOWNLOAD_DIR: {expected_download_dir}", 
                          version is not None and os.path.exists(expected_binary_path))
    
    @pytest.mark.skip(reason="Skipping upgrade test to avoid unnecessary downloads during regular testing")
    @pystackql_test_setup()
    def test_upgrade_method(self):
        """Test that the upgrade method updates the binary."""
        initial_version = self.stackql.version
        initial_sha = self.stackql.sha
        
        # Perform the upgrade
        upgrade_message = self.stackql.upgrade()
        
        # Check that we got a valid message
        assert "stackql upgraded to version" in upgrade_message, "Upgrade message not as expected"
        
        # Verify that the version attributes were updated
        assert self.stackql.version is not None, "version should not be None after upgrade"
        assert self.stackql.sha is not None, "sha should not be None after upgrade"
        
        print_test_result(f"Upgrade method test\nINITIAL VERSION: {initial_version}, SHA: {initial_sha}\n"
                         f"NEW VERSION: {self.stackql.version}, SHA: {self.stackql.sha}", 
                         "stackql upgraded to version" in upgrade_message)

if __name__ == "__main__":
    pytest.main(["-v", __file__])