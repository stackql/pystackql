# pystackql/utils/helpers.py

"""
Utility functions for PyStackQL package.

This module contains helper functions for binary management, platform detection,
and other utilities needed by the PyStackQL package.
"""

import subprocess
import platform
import json
import site
import os
import requests
import zipfile

# Conditional import for package metadata retrieval
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # This is for Python versions earlier than 3.8
    from importlib_metadata import version, PackageNotFoundError


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


def get_download_dir():
    """Gets the directory to download the stackql binary.
    
    Returns:
        str: The directory path
    """
    # check if site.getuserbase() dir exists
    if not os.path.exists(site.getuserbase()):
        # if not, create it
        os.makedirs(site.getuserbase())
    return site.getuserbase()


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


def get_download_url():
    """Gets the download URL for the stackql binary based on the platform.
    
    Returns:
        str: The download URL
        
    Raises:
        Exception: If the platform is not supported
    """
    system_val = platform.system()
    machine_val = platform.machine()

    if system_val == 'Linux' and machine_val == 'x86_64':
        return 'https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip'
    elif system_val == 'Windows':
        return 'https://releases.stackql.io/stackql/latest/stackql_windows_amd64.zip'
    elif system_val == 'Darwin':
        return 'https://storage.googleapis.com/stackql-public-releases/latest/stackql_darwin_multiarch.pkg'
    else:
        raise Exception(f"ERROR: [get_download_url] unsupported OS type: {system_val} {machine_val}")


def download_file(url, path, showprogress=True):
    """Downloads a file from a URL to a local path.
    
    Args:
        url (str): The URL to download from
        path (str): The local path to save the file to
        showprogress (bool, optional): Whether to show a progress bar. Defaults to True.
        
    Raises:
        Exception: If the download fails
    """
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 1024
        with open(path, 'wb') as f:
            chunks = 0
            for data in r.iter_content(block_size):
                chunks += 1
                f.write(data)
                downloaded_size = chunks * block_size
                progress_bar = '#' * int(downloaded_size / total_size_in_bytes * 20)
                if showprogress:
                    print(f'\r[{progress_bar.ljust(20)}] {int(downloaded_size / total_size_in_bytes * 100)}%', end='')

        print("\nDownload complete.")
    except Exception as e:
        print(f"ERROR: [download_file] {str(e)}")
        exit(1)


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


def format_auth(auth):
    """Formats an authentication object for use with stackql.
    
    Args:
        auth: The authentication object, can be a string or a dict
        
    Returns:
        tuple: (auth_obj, auth_str)
            - auth_obj: The authentication object as a dict
            - auth_str: The authentication object as a JSON string
            
    Raises:
        Exception: If the authentication object is invalid
    """
    try:
        if auth is not None:
            if isinstance(auth, str):
                authobj = json.loads(auth)
                authstr = auth
            elif isinstance(auth, dict):
                authobj = auth
                authstr = json.dumps(auth)
            return authobj, authstr
        else:
            raise Exception("ERROR: [format_auth] auth key supplied with no value")
    except Exception as e:
        error_message = e.args[0]
        print(f"ERROR: [format_auth] {error_message}")
        exit(1)