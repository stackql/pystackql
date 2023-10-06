import unittest
import json, os, sys, platform, re
import pandas as pd
from termcolor import colored

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystackql import StackQL

def pystackql_test_setup(func):
    def wrapper(self):
        if hasattr(self, 'stackql') and self.stackql:
            del self.stackql
        self.stackql = StackQL()
        func(self)
    return wrapper

class PyStackQLTest(unittest.TestCase):

    def print_test_result(self, test_name, condition):
        if condition:
            print(colored('\n' + "[PASSED] " + test_name, 'green'))
        else:
            print(colored('\n' + "[FAILED] " + test_name, 'red'))

    @pystackql_test_setup
    def test_properties_class_method(self):
        properties = self.stackql.properties()
        
        # Check that properties is a dictionary
        self.assertTrue(isinstance(properties, dict), "properties should be a dictionary")
        
        # List of keys we expect to be in the properties
        expected_keys = [
            "bin_path", "download_dir", "package_version", "params", 
            "parse_json", "platform", "server_mode", "sha", "version"
        ]
        missing_keys = [key for key in expected_keys if key not in properties]
        self.assertTrue(len(missing_keys) == 0, f"Missing keys in properties: {', '.join(missing_keys)}")

        # Further type checks (as examples)
        self.assertIsInstance(properties["bin_path"], str, "bin_path should be of type str")
        self.assertIsInstance(properties["params"], list, "params should be of type list")
        self.assertIsInstance(properties["parse_json"], bool, "parse_json should be of type bool")

        # If all the assertions pass, then the properties are considered valid.
        self.print_test_result("test_properties_class_method", True)

    @pystackql_test_setup
    def test_version_attribute(self):
        version = self.stackql.version
        self.assertIsNotNone(version)
        semver_pattern = r'^v?(\d+\.\d+\.\d+)$'  # should be 'vN.N.N' or 'N.N.N'
        is_valid_semver = bool(re.match(semver_pattern, version))
        self.assertTrue(is_valid_semver)
        self.print_test_result("test_version_attribute", is_valid_semver)

    @pystackql_test_setup
    def test_platform_attribute(self):
        platform_string = self.stackql.platform
        self.assertIsNotNone(platform_string)
        platform_pattern = r'^(Windows|Linux|Darwin) (\w+) \(([^)]+)\), Python (\d+\.\d+\.\d+)$'
        is_valid_platform = bool(re.match(platform_pattern, platform_string))
        self.assertTrue(is_valid_platform)
        self.print_test_result("test_platform_attribute", is_valid_platform)

    @pystackql_test_setup
    def test_set_custom_download_dir(self):
        this_platform = platform.system().lower()
        if this_platform == "windows":
            download_dir = 'C:\\temp'
        else:
            download_dir = '/tmp'
        self.stackql = StackQL(download_dir=download_dir)
        version = self.stackql.version
        self.assertIsNotNone(version)
        self.print_test_result("test_set_custom_download_dir", version is not None)

    # @pystackql_test_setup
    # def test_server_mode_and_defaults(self):
    #     self.stackql = StackQL(server_mode=True)
    #     self.assertTrue(self.stackql.server_mode)
    #     self.assertEqual(self.stackql.server_address, "0.0.0.0")
    #     self.assertEqual(self.stackql.server_port, 5466)
    #     self.print_test_result("test_server_mode_and_defaults", self.stackql.server_mode)

    # @pystackql_test_setup
    # def test_server_mode_custom_address_and_port(self):
    #     custom_address = "127.0.0.1"
    #     custom_port = 5000
    #     self.stackql = StackQL(server_mode=True, server_address=custom_address, server_port=custom_port)
    #     self.assertEqual(self.stackql.server_address, custom_address)
    #     self.assertEqual(self.stackql.server_port, custom_port)
    #     self.print_test_result("test_server_mode_custom_address_and_port", self.stackql.server_mode)

    @pystackql_test_setup
    def test_custom_params_and_table_output(self):
        self.stackql = StackQL(output="table")
        self.assertIn("table", self.stackql.params)
        self.assertFalse(self.stackql.parse_json)
        self.print_test_result("test_custom_params_and_table_output", not self.stackql.parse_json)

    @pystackql_test_setup
    def test_binary_setup(self):
        self.assertTrue(os.path.exists(self.stackql.bin_path))
        self.print_test_result("test_binary_setup", os.path.exists(self.stackql.bin_path))

    @pystackql_test_setup
    def test_executeStmt(self):
        # Insert operation
        insert_query = f"""
        INSERT INTO google.compute.disks(
            project, zone, data__name, data__sizeGb)
        SELECT
            '{os.environ['GCP_PROJECT']}',
            '{os.environ['GCP_ZONE']}',
            '{os.environ['GCP_DISK_NAME']}',
            '10';
        """
        result = self.stackql.executeStmt(insert_query)
        self.assertIn("Expected_Response_Content", result)  # Replace Expected_Response_Content with expected content

        # Delete operation to clean up
        delete_query = f"""
        DELETE FROM google.compute.disks
        WHERE project = '{os.environ['GCP_PROJECT']}'
        AND zone = '{os.environ['GCP_ZONE']}'
        AND disk = '{os.environ['GCP_DISK_NAME']}';
        """
        result = self.stackql.executeStmt(delete_query)
        self.assertIn("Expected_Delete_Response_Content", result)  # Replace with expected response content

        self.print_test_result("test_executeStmt", True)

    @pystackql_test_setup
    def test_execute(self):
        query = f"""
        SELECT status, count(*) as num_instances
        FROM google.compute.instances
        WHERE project = '{os.environ['GCP_PROJECT']}' 
        AND zone = '{os.environ['GCP_ZONE']}'
        GROUP BY status
        """
        result = self.stackql.execute(query)
        # You can assert based on expected results
        self.assertIsInstance(result, (str, dict))
        self.print_test_result("test_execute", True)

    @pystackql_test_setup
    def test_executeQueriesAsync(self):
        regions = os.environ.get('REGIONS').split(',')
        queries = [
            f"""
            SELECT '{region}' as region, instanceType, COUNT(*) as num_instances
            FROM aws.ec2.instances
            WHERE region = '{region}'
            GROUP BY instanceType
            """
            for region in regions
        ]
        results = self.stackql.executeQueriesAsync(queries)
        # Assert based on the expected number of results or their content
        self.assertEqual(len(results), len(regions))
        self.print_test_result("test_executeQueriesAsync", True)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
