# pystackql/utils/binary.py

"""
Binary management utility functions for PyStackQL.

This module contains functions for managing the StackQL binary.
"""

import os
import subprocess
from .download import get_download_url, download_file, get_download_dir
from .platform import get_platform


def get_binary_name(system_platform):
    """Gets the binary name based on the platform.
    
    Args:
        system_platform (str): The operating system platform
        
    Returns:
        str: The name of the binary
    """
    if system_platform.startswith('Windows'):
        return r'stackql.exe'
    elif system_platform.startswith('Darwin'):
        return r'stackql/Payload/stackql'
    else:
        return r'stackql'


def get_binary_version(bin_path):
    """Gets the version of the stackql binary.
    
    Args:
        bin_path (str): The path to the binary
        
    Returns:
        tuple: (version, sha)
            - version: The version number
            - sha: The git commit sha
            
    Raises:
        FileNotFoundError: If the binary is not found
        Exception: If the version cannot be determined
    """
    try:
        iqlPopen = subprocess.Popen([bin_path] + ["--version"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Use communicate to fetch the outputs and wait for the process to finish
        output, _ = iqlPopen.communicate()
        # Decode the output
        decoded_output = output.decode('utf-8')
        # Split to get the version tokens
        version_tokens = decoded_output.split('\n')[0].split(' ')
        version = version_tokens[1]
        sha = version_tokens[3].replace('(', '').replace(')', '')
        return version, sha
    except FileNotFoundError:
        print(f"ERROR: [get_binary_version] {bin_path} not found")
        exit(1)
    except Exception as e:
        error_message = e.args[0]
        print(f"ERROR: [get_binary_version] {error_message}")        
        exit(1)
    finally:
        # Ensure the subprocess is terminated and streams are closed
        iqlPopen.terminate()
        if hasattr(iqlPopen, 'stdout') and iqlPopen.stdout:
            iqlPopen.stdout.close()


def setup_binary(download_dir, system_platform, showprogress=False):
    """Sets up the stackql binary by downloading and extracting it.
    
    Args:
        download_dir (str): The directory to download to
        system_platform (str): The operating system platform
        showprogress (bool, optional): Whether to show download progress. Defaults to False.
        
    Raises:
        Exception: If the setup fails
    """
    try:
        print('installing stackql...')
        binary_name = get_binary_name(system_platform)
        url = get_download_url()
        print(f"Downloading latest version of stackql from {url} to {download_dir}")

        # Paths
        archive_file_name = os.path.join(download_dir, os.path.basename(url))
        binary_path = os.path.join(download_dir, binary_name)

        # Download and extract
        download_file(url, archive_file_name, showprogress)

        # Handle extraction
        if system_platform.startswith('Darwin'):
            unpacked_file_name = os.path.join(download_dir, 'stackql')
            command = f'pkgutil --expand-full {archive_file_name} {unpacked_file_name}'
            if os.path.exists(unpacked_file_name):
                os.system(f'rm -rf {unpacked_file_name}')
            os.system(command)

        else:  # Handle Windows and Linux
            import zipfile
            with zipfile.ZipFile(archive_file_name, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            # Specific check for Windows to ensure `stackql.exe` is extracted
            if system_platform.startswith("Windows"):
                if not os.path.exists(binary_path) and os.path.exists(os.path.join(download_dir, "stackql")):
                    os.rename(os.path.join(download_dir, "stackql"), binary_path)

        # Confirm binary presence and set permissions
        if os.path.exists(binary_path):
            print(f"StackQL executable successfully located at: {binary_path}")
            os.chmod(binary_path, 0o755)
        else:
            print(f"ERROR: Expected binary '{binary_path}' not found after extraction.")
            exit(1)

    except Exception as e:
        print(f"ERROR: [setup_binary] {str(e)}")
        exit(1)