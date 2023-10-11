import json, os, sys, platform, re, time, unittest, subprocess
import pandas as pd
from termcolor import colored
import unittest.mock as mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

server_port = 5466

expected_properties = [
    "bin_path", "download_dir", "package_version", "params", 
    "parse_json", "platform", "server_mode", "sha", "version"
]

expected_version_pattern = r'^v?(\d+\.\d+\.\d+)$'
expected_package_version_pattern = r'^(\d+\.\d+\.\d+)$'

expected_platform_pattern = r'^(Windows|Linux|Darwin) (\w+) \(([^)]+)\), Python (\d+\.\d+\.\d+)$'
custom_windows_download_dir = 'C:\\temp'
custom_mac_linux_download_dir = '/tmp'
registry_pull_google_query = "REGISTRY PULL google"
registry_pull_aws_query = "REGISTRY PULL aws"

def registry_pull_resp_pattern(provider):
    return r"%s provider, version 'v\d+\.\d+\.\d+' successfully installed" % provider

google_query = f"""
SELECT status, count(*) as num_instances
FROM google.compute.instances
WHERE project = '{os.environ['GCP_PROJECT']}' 
AND zone = '{os.environ['GCP_ZONE']}'
GROUP BY status
"""

regions = os.environ.get('AWS_REGIONS').split(',')

async_queries = [
    f"""
    SELECT '{region}' as region, instanceType, COUNT(*) as num_instances
    FROM aws.ec2.instances
    WHERE region = '{region}'
    GROUP BY instanceType
    """
    for region in regions
]

def print_test_result(test_name, condition, server_mode=False, is_ipython=False):
    status_header = colored("[PASSED] ", 'green') if condition else colored("[FAILED] ", 'red')
    headers = [status_header]
    
    if server_mode:
        headers.append(colored("[SERVER MODE]", 'yellow'))
    if is_ipython:
        headers.append(colored("[MAGIC EXT]", 'blue'))
    
    headers.append(test_name)
    message = " ".join(headers)
    
    print("\n" + message)