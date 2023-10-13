import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystackql import StackQL
from pystackql.stackql_magic import StackqlMagic, load_ipython_extension
from .test_params import *

def pystackql_test_setup(func):
    def wrapper(self):
        try:
            del self.stackql
        except AttributeError:
            pass
        self.stackql = StackQL()
        func(self)
    return wrapper

class PyStackQLTestsBase(unittest.TestCase):
    pass

def setUpModule():
    print("downloading stackql binary...")
    PyStackQLTestsBase.stackql = StackQL()
    print("starting stackql server...")
    PyStackQLTestsBase.server_process = subprocess.Popen([PyStackQLTestsBase.stackql.bin_path, "srv", "--pgsrv.address", server_address, "--pgsrv.port", str(server_port)])
    time.sleep(5)

def tearDownModule():
    print("stopping stackql server...")
    if PyStackQLTestsBase.server_process:
        PyStackQLTestsBase.server_process.terminate()
        PyStackQLTestsBase.server_process.wait()

class PyStackQLNonServerModeTests(PyStackQLTestsBase):

    @pystackql_test_setup
    def test_01_properties_class_method(self):
        properties = self.stackql.properties()
        # Check that properties is a dictionary
        self.assertTrue(isinstance(properties, dict), "properties should be a dictionary")
        # List of keys we expect to be in the properties
        missing_keys = [key for key in expected_properties if key not in properties]
        self.assertTrue(len(missing_keys) == 0, f"Missing keys in properties: {', '.join(missing_keys)}")
        # Further type checks (as examples)
        self.assertIsInstance(properties["bin_path"], str, "bin_path should be of type str")
        self.assertIsInstance(properties["params"], list, "params should be of type list")
        self.assertIsInstance(properties["server_mode"], bool, "server_mode should be of type bool")
        self.assertIsInstance(properties["output"], str, "output should be of type str")
        # If all the assertions pass, then the properties are considered valid.
        print_test_result("Test properties method", True)

    @pystackql_test_setup
    def test_02_version_attribute(self):
        version = self.stackql.version
        self.assertIsNotNone(version)
        is_valid_semver = bool(re.match(expected_version_pattern, version))
        self.assertTrue(is_valid_semver)
        print_test_result("Test version attribute", is_valid_semver)

    @pystackql_test_setup
    def test_02a_package_version_attribute(self):
        package_version = self.stackql.package_version
        print(f"""PACKAGE VERSION: {package_version}""")
        self.assertIsNotNone(package_version)
        is_valid_semver = bool(re.match(expected_package_version_pattern, package_version))
        self.assertTrue(is_valid_semver)
        print_test_result("Test package_version attribute", is_valid_semver)

    @pystackql_test_setup
    def test_03_platform_attribute(self):
        platform_string = self.stackql.platform
        self.assertIsNotNone(platform_string)
        is_valid_platform = bool(re.match(expected_platform_pattern, platform_string))
        self.assertTrue(is_valid_platform)
        print_test_result("Test platform attribute", is_valid_platform)

    @pystackql_test_setup
    def test_04_bin_path_attribute(self):
        self.assertTrue(os.path.exists(self.stackql.bin_path))
        print_test_result("Test bin_path attribute with default download path", os.path.exists(self.stackql.bin_path))

    @pystackql_test_setup
    def test_05_set_custom_download_dir(self):
        this_platform = platform.system().lower()
        if this_platform == "windows":
            download_dir = custom_windows_download_dir
        else:
            download_dir = custom_mac_linux_download_dir
        self.stackql = StackQL(download_dir=download_dir)
        version = self.stackql.version
        self.assertIsNotNone(version)
        print_test_result("Test setting a custom download_dir", version is not None)

    @pystackql_test_setup
    def test_06_custom_params_and_csv_output(self):
        self.stackql = StackQL(output="csv")
        self.assertIn("csv", self.stackql.params)
        self.assertEqual(self.stackql.output, "csv")
        print_test_result("Test setting csv output", True)

    # @pystackql_test_setup
    # def test_07_executeStmt(self):
    #     result = self.stackql.executeStmt(registry_pull_google_query)
    #     expected_pattern = registry_pull_resp_pattern("google")
    #     self.assertTrue(re.search(expected_pattern, result), f"Expected pattern not found in result: {result}")
    #     result = self.stackql.executeStmt(registry_pull_aws_query)
    #     expected_pattern = registry_pull_resp_pattern("aws")
    #     self.assertTrue(re.search(expected_pattern, result), f"Expected pattern not found in result: {result}")
    #     print_test_result("Test executeStmt method", True)

    # @pystackql_test_setup
    # def test_08_execute(self):
    #     result = self.stackql.execute(google_query)
    #     try:
    #         # Convert the result to a pandas dataframe
    #         df = pd.DataFrame(result)
    #         # Check the dataframe structure
    #         columns_exist = 'num_instances' in df.columns and 'status' in df.columns
    #         has_rows = len(df) >= 1
    #         if columns_exist and has_rows:
    #             print_test_result("Test execute method", True)
    #         else:
    #             failure_messages = []
    #             if not columns_exist:
    #                 failure_messages.append("Columns 'num_instances' and 'status' should exist in the DataFrame")
    #             if not has_rows:
    #                 failure_messages.append("DataFrame should have one or more rows")
    #             debug_info = "\n".join(failure_messages)
    #             print_test_result("Test execute method", False)
    #             self.fail(debug_info)
    #     except Exception as e:
    #         debug_info = (f"{str(e)}"
    #           f"\n****DEBUG INFO****\n"
    #           f"Query: \n{google_query}\n"
    #           f"Result: \n{result}\n"
    #           f"****END DEBUG INFO****")
    #         print_test_result("Test execute method", False)
    #         self.fail(debug_info)

    # @pystackql_test_setup
    # def test_09_executeQueriesAsync(self):
    #     results = self.stackql.executeQueriesAsync(async_queries)
    #     failure_messages = []  # List to accumulate failure messages
    #     try:
    #         # Convert the results to a pandas DataFrame
    #         df = pd.DataFrame(results)
    #         # Check that the DataFrame has the required columns
    #         if 'region' not in df.columns:
    #             failure_messages.append("'region' column missing in DataFrame")
    #         if 'instanceType' not in df.columns:
    #             failure_messages.append("'instanceType' column missing in DataFrame")
    #         if 'num_instances' not in df.columns:
    #             failure_messages.append("'num_instances' column missing in DataFrame")
    #         # Check that all regions are represented in the DataFrame
    #         unique_regions_in_df = df['region'].unique()
    #         for region in regions:
    #             if region not in unique_regions_in_df:
    #                 failure_messages.append(f"Region '{region}' not found in DataFrame")
    #         if not failure_messages:
    #             print_test_result("Test executeQueriesAsync method", True)
    #         else:
    #             debug_info = "\n".join(failure_messages) + \
    #                         f"\n****DEBUG INFO****\n" + \
    #                         f"Queries: \n{async_queries}\n" + \
    #                         f"Result: \n{results}\n" + \
    #                         f"****END DEBUG INFO****"
    #             print_test_result("Test executeQueriesAsync method", False)
    #             self.fail(debug_info)
    #     except Exception as e:
    #         debug_info = (f"{str(e)}"
    #                     f"\n****DEBUG INFO****\n"
    #                     f"Queries: \n{async_queries}\n"
    #                     f"Result: \n{results}\n"
    #                     f"****END DEBUG INFO****")
    #         print_test_result("Test executeQueriesAsync method", False)
    #         self.fail(debug_info)

class PyStackQLServerModeTests(PyStackQLTestsBase):

    pass
    # @pystackql_test_setup
    # def test_10_server_mode_connectivity(self):
    #     self.stackql = StackQL(server_mode=True, server_address=server_address, server_port=server_port)
    #     self.assertTrue(self.stackql.server_mode, "StackQL should be in server mode")
    #     self.assertIsNotNone(self.stackql._conn, "Connection object should not be None")
    #     print_test_result("Test server mode connectivity", True, True)

    # @pystackql_test_setup
    # def test_11_executeStmt_server_mode(self):
    #     failure_messages = []  # List to accumulate failure messages
    #     result = None
    #     try:
    #         self.stackql = StackQL(server_mode=True, server_address=server_address, server_port=server_port)
    #         result = self.stackql.executeStmt(registry_pull_google_query)
    #         if result != "[]":
    #             failure_messages.append(f"Expected empty list, got: {result}")
    #     except Exception as e:
    #         failure_messages.append(f"Runtime error occurred: {str(e)}")
    #     if not failure_messages:
    #         print_test_result("Test executeStmt in server mode", True, True)
    #     else:
    #         debug_info = "\n".join(failure_messages) + \
    #                     f"\n****DEBUG INFO****\n" + \
    #                     f"Query: \n{registry_pull_google_query}\n" + \
    #                     (f"Result: \n{result}\n" if result else "") + \
    #                     f"****END DEBUG INFO****"
    #         print_test_result("Test executeStmt in server mode", False, True)
    #         self.fail(debug_info)

    # @pystackql_test_setup
    # def test_12_execute_server_mode_to_pandas(self):
    #     failure_messages = []  # List to accumulate failure messages
    #     result = None
    #     df = None
    #     try:
    #         self.stackql = StackQL(server_mode=True, server_address=server_address, server_port=server_port)
    #         result = self.stackql.execute(google_query)
    #         # If the result is a list of dictionaries, then proceed to convert to DataFrame
    #         if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
    #             df = pd.DataFrame(result)
    #             if 'num_instances' not in df.columns or 'status' not in df.columns:
    #                 failure_messages.append("Columns 'num_instances' and 'status' should exist in the DataFrame")
    #             if len(df) < 1:
    #                 failure_messages.append("DataFrame should have one or more rows")
    #         else:
    #             failure_messages.append(f"Unexpected result format: {result}")
    #     except Exception as e:
    #         failure_messages.append(f"Runtime error occurred: {str(e)}")
    #     if not failure_messages:
    #         print_test_result("Test execute method in server mode", True, True)
    #     else:
    #         debug_info = "\n".join(failure_messages) + \
    #                     f"\n****DEBUG INFO****\n" + \
    #                     f"Query: \n{google_query}\n" + \
    #                     (f"Result: \n{result}\n" if result else "") + \
    #                     (f"DataFrame: \n{df}\n" if df is not None else "") + \
    #                     f"****END DEBUG INFO****"
    #         print_test_result("Test execute method in server mode", False, True)
    #         self.fail(debug_info)

class MockInteractiveShell:
    """A mock class for IPython's InteractiveShell."""
    user_ns = {}  # Mock user namespace

    def register_magics(self, magics):
        """Mock method to 'register' magics."""
        self.magics = magics

    @staticmethod
    def instance():
        """Return a mock instance of the shell."""
        return MockInteractiveShell()

class StackQLMagicTests(PyStackQLTestsBase):

    def setUp(self):
        """Set up for the magic tests."""
        self.shell = MockInteractiveShell.instance()
        load_ipython_extension(self.shell)
        self.stackql_magic = StackqlMagic(shell=self.shell)

    # def test_14_magic_cell_query(self):
    #     failure_messages = []  # List to accumulate failure messages
    #     df = None
    #     try:
    #         # Test the cell magic functionality
    #         df = self.stackql_magic.stackql("", google_query)  # Cell magic uses both line and cell arguments
    #         if not isinstance(df, pd.DataFrame):
    #             failure_messages.append("Result is not a pandas DataFrame")
    #         if 'num_instances' not in df.columns or 'status' not in df.columns:
    #             failure_messages.append("Expected columns 'num_instances' and 'status' are missing in DataFrame")
    #     except Exception as e:
    #         failure_messages.append(f"Runtime error occurred: {str(e)}")
    #     if not failure_messages:
    #         print_test_result("test cell magic", True, True, True)
    #     else:
    #         debug_info = "\n".join(failure_messages) + \
    #                     f"\n****DEBUG INFO****\n" + \
    #                     f"Query: \n{google_query}\n" + \
    #                     (f"DataFrame: \n{df}\n" if df is not None else "") + \
    #                     f"****END DEBUG INFO****"
    #         print_test_result("test cell magic", False, True, True)
    #         self.fail(debug_info)

    # def test_15_magic_cell_query_no_display(self):
    #     failure_messages = []  # List to accumulate failure messages
    #     df = None
    #     try:
    #         # Test the cell magic functionality with the --no-display option
    #         df = self.stackql_magic.stackql("--no-display", google_query)
    #         if df is not None:
    #             failure_messages.append("Expected result to be None, but it wasn't.")
    #     except Exception as e:
    #         failure_messages.append(f"Runtime error occurred: {str(e)}")
    #     if not failure_messages:
    #         print_test_result("test cell magic with --no-display", True, True, True)
    #     else:
    #         debug_info = "\n".join(failure_messages) + \
    #                     f"\n****DEBUG INFO****\n" + \
    #                     f"Query: \n{google_query}\n" + \
    #                     (f"Result: \n{df}\n" if df is not None else "") + \
    #                     f"****END DEBUG INFO****"
    #         print_test_result("test cell magic with --no-display", False, True, True)
    #         self.fail(debug_info)

def main():
    unittest.main(verbosity=0)

if __name__ == '__main__':
    main()
