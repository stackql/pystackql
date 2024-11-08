import json, sys, platform, re, time, unittest, subprocess
import pandas as pd
from termcolor import colored
import unittest.mock as mock

server_port = 5466
server_address = "127.0.0.1"

expected_properties = [
    "bin_path", "download_dir", "package_version", "params", 
    "output", "platform", "server_mode", "sha", "version"
]

expected_version_pattern = r'^v?(\d+\.\d+\.\d+)$'
expected_package_version_pattern = r'^(\d+\.\d+\.\d+)$'

expected_platform_pattern = r'^(Windows|Linux|Darwin) (\w+) \(([^)]+)\), Python (\d+\.\d+\.\d+)$'
# custom_windows_download_dir = 'C:\\temp'
# custom_mac_linux_download_dir = '/tmp'
def get_custom_download_dir(platform_name):
    custom_download_dirs = {
        'windows': 'C:\\temp',
        'darwin': '/tmp',
        'linux': '/tmp'
    }
    return custom_download_dirs.get(platform_name, '/tmp')

registry_pull_google_query = "REGISTRY PULL google"
registry_pull_aws_query = "REGISTRY PULL aws"
registry_pull_okta_query = "REGISTRY PULL okta"
registry_pull_github_query = "REGISTRY PULL github"
registry_pull_homebrew_query = "REGISTRY PULL homebrew"

def registry_pull_resp_pattern(provider):
    return r"%s provider, version 'v\d+\.\d+\.\d+' successfully installed\s*" % provider

test_gcp_project_id = "test-gcp-project"
test_gcp_zone = "australia-southeast2-a"

github_query = "select login from github.users.users"

google_query = f"""
SELECT status, count(*) as num_instances
FROM google.compute.instances
WHERE project = '{test_gcp_project_id}' 
AND zone = '{test_gcp_zone}'
GROUP BY status
"""
google_show_services_query = "SHOW SERVICES IN google"

aws_query = f"""
SELECT
instance_type,
count(*) as num_instances
FROM aws.ec2.instances
WHERE region = 'ap-southeast-2'
GROUP BY instance_type
"""

test_aws_regions = ["ap-southeast-2", "ap-southeast-4"]

async_queries = [
    f"""
    SELECT region, COUNT(*) as num_functions
    FROM aws.lambda.functions
    WHERE region = '{region}'
    """
    for region in test_aws_regions
]

def print_test_result(test_name, condition=True, server_mode=False, is_ipython=False, is_async=False):
    status_header = colored("[PASSED] ", 'green') if condition else colored("[FAILED] ", 'red')
    headers = [status_header]
    
    if server_mode:
        headers.append(colored("[SERVER MODE]", 'yellow'))
    if is_ipython:
        headers.append(colored("[MAGIC EXT]", 'blue'))
    if is_async:
        headers.append(colored("[ASYNC]", 'magenta'))
    
    headers.append(test_name)
    message = " ".join(headers)
    
    print("\n" + message)
