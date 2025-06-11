# pystackql/utils/download.py

"""
Download-related utility functions for PyStackQL.

This module contains functions for downloading and managing the StackQL binary.
"""

import os
import site
import platform
import requests


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