import sys, os, unittest, asyncio, re
from unittest.mock import MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystackql import StackQL, magic, magics, StackqlMagic, StackqlServerMagic
from .test_params import *

def pystackql_test_setup(**kwargs):
    def decorator(func):
        def wrapper(self):
            try:
                del self.stackql
            except AttributeError:
                pass
            self.stackql = StackQL(**kwargs)
            func(self)
        return wrapper
    return decorator

def async_test_decorator(func):
    def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return asyncio.run(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)
    return wrapper

class PyStackQLTestsBase(unittest.TestCase):
    pass

def setUpModule():
    print("downloading stackql binary...")
    PyStackQLTestsBase.stackql = StackQL()
	# Check whether code is running in GitHub Actions
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'

    if not is_github_actions:
        # Ensure you have the latest version of stackql, only when running locally
        print("Running tests outside of GitHub Actions, upgrading stackql binary...")
        PyStackQLTestsBase.stackql.upgrade()

    print("downloading aws provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_aws_query)
    print(res)
    print("downloading awscc provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_awscc_query)
    print(res)    
    print("downloading google provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_google_query)
    print(res)
    print("starting stackql server...")
    PyStackQLTestsBase.server_process = subprocess.Popen([PyStackQLTestsBase.stackql.bin_path, "srv", "--pgsrv.address", server_address, "--pgsrv.port", str(server_port)])
    time.sleep(10)

def tearDownModule():
    print("stopping stackql server...")
    if PyStackQLTestsBase.server_process:
        PyStackQLTestsBase.server_process.terminate()
        PyStackQLTestsBase.server_process.wait()

class PyStackQLNonServerModeTests(PyStackQLTestsBase):

    @pystackql_test_setup()
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
        print_test_result(f"""Test properties method\nPROPERTIES: {properties}""", True)

    @pystackql_test_setup()
    def test_02_version_attribute(self):
        version = self.stackql.version
        self.assertIsNotNone(version)
        is_valid_semver = bool(re.match(expected_version_pattern, version))
        self.assertTrue(is_valid_semver)
        print_test_result(f"""Test version attribute\nVERSION: {version}""", is_valid_semver)

    @pystackql_test_setup()
    def test_03_package_version_attribute(self):
        package_version = self.stackql.package_version
        self.assertIsNotNone(package_version)
        is_valid_semver = bool(re.match(expected_package_version_pattern, package_version))
        self.assertTrue(is_valid_semver)
        print_test_result(f"""Test package_version attribute\nPACKAGE VERSION: {package_version}""", is_valid_semver)

    @pystackql_test_setup()
    def test_04_platform_attribute(self):
        platform_string = self.stackql.platform
        self.assertIsNotNone(platform_string)
        is_valid_platform = bool(re.match(expected_platform_pattern, platform_string))
        self.assertTrue(is_valid_platform)
        print_test_result(f"""Test platform attribute\nPLATFORM: {platform_string}""", is_valid_platform)

    @pystackql_test_setup()
    def test_05_bin_path_attribute(self):
        self.assertTrue(os.path.exists(self.stackql.bin_path))
        print_test_result(f"""Test bin_path attribute with default download path\nBINARY PATH: {self.stackql.bin_path}""", os.path.exists(self.stackql.bin_path))

    @pystackql_test_setup(download_dir=get_custom_download_dir(platform.system().lower()))
    def test_06_set_custom_download_dir(self):
        # Checking that version is not None
        version = self.stackql.version
        self.assertIsNotNone(version)
        # Checking that download_dir is correctly set
        expected_download_dir = get_custom_download_dir(platform.system().lower())
        self.assertEqual(self.stackql.download_dir, expected_download_dir, "Download directory is not set correctly.")
        # Checking that the binary exists at the expected location
        binary_name = 'stackql' if platform.system().lower() != 'windows' else 'stackql.exe'
        expected_binary_path = os.path.join(expected_download_dir, binary_name)
        self.assertTrue(os.path.exists(expected_binary_path), f"No binary found at {expected_binary_path}")
        # Final test result print
        print_test_result(f"""Test setting a custom download_dir\nCUSTOM_DOWNLOAD_DIR: {expected_download_dir}""", version is not None and os.path.exists(expected_binary_path))

    @pystackql_test_setup(output="csv")
    def test_07_csv_output_with_defaults(self):
        # Check if output is set correctly
        self.assertEqual(self.stackql.output, "csv", "Output type is not set to 'csv'")
        # Check if sep is set to default (',')
        self.assertEqual(self.stackql.sep, ",", "Separator is not set to default ','")
        # Check if header is set to default (should be False)
        self.assertFalse(self.stackql.header, "Header is not set to default (False)")
        # Check if params list has --output and csv
        self.assertIn("--output", self.stackql.params)
        self.assertIn("csv", self.stackql.params)
        # Check if params list has default --delimiter and ,
        self.assertIn("--delimiter", self.stackql.params)
        self.assertIn(",", self.stackql.params)
        # Check if params list has --hideheaders (default header value is False)
        self.assertIn("--hideheaders", self.stackql.params)
        print_test_result(f"""Test csv output with defaults (comma delimited without headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup(output="csv", sep="|")
    def test_08_csv_output_with_pipe_separator(self):
        # Check if sep is set to '|'
        self.assertEqual(self.stackql.sep, "|", "Separator is not set to '|'")
        # Check if params list has --delimiter and |
        self.assertIn("--delimiter", self.stackql.params)
        self.assertIn("|", self.stackql.params)
        # Check if --hideheaders is in params list
        self.assertIn("--hideheaders", self.stackql.params)
        print_test_result(f"""Test csv output with custom sep (pipe delimited without headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup(output="csv", header=True)
    def test_09_csv_output_with_header(self):
        # Check if header is set to True
        self.assertTrue(self.stackql.header, "Header is not set to True")
        # Check if params list does not have --hideheaders
        self.assertNotIn("--hideheaders", self.stackql.params)
        print_test_result(f"""Test csv output with headers (comma delimited with headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup()
    def test_10_executeStmt(self):
        okta_result_dict = self.stackql.executeStmt(registry_pull_okta_query)
        okta_result = okta_result_dict["message"]
        expected_pattern = registry_pull_resp_pattern("okta")
        self.assertTrue(re.search(expected_pattern, okta_result), f"Expected pattern not found in result: {okta_result}")
        github_result_dict = self.stackql.executeStmt(registry_pull_github_query)
        github_result = github_result_dict["message"]
        expected_pattern = registry_pull_resp_pattern("github")
        self.assertTrue(re.search(expected_pattern, github_result), f"Expected pattern not found in result: {github_result}")
        print_test_result(f"""Test executeStmt method\nRESULTS:\n{okta_result_dict}\n{github_result_dict}""", True)

    @pystackql_test_setup(output="csv")
    def test_10a_executeStmt_with_csv_output(self):
        okta_result = self.stackql.executeStmt(registry_pull_okta_query)
        expected_pattern = registry_pull_resp_pattern("okta")
        self.assertTrue(re.search(expected_pattern, okta_result), f"Expected pattern not found in result: {okta_result}")
        github_result = self.stackql.executeStmt(registry_pull_github_query)
        expected_pattern = registry_pull_resp_pattern("github")
        self.assertTrue(re.search(expected_pattern, github_result), f"Expected pattern not found in result: {github_result}")
        print_test_result(f"""Test executeStmt method with csv output\nRESULTS:\n{okta_result}\n{github_result}""", True)

    @pystackql_test_setup(output="pandas")
    def test_10b_executeStmt_with_pandas_output(self):
        okta_result_df = self.stackql.executeStmt(registry_pull_okta_query)
        okta_result = okta_result_df['message'].iloc[0]
        expected_pattern = registry_pull_resp_pattern("okta")
        self.assertTrue(re.search(expected_pattern, okta_result), f"Expected pattern not found in result: {okta_result}")
        github_result_df = self.stackql.executeStmt(registry_pull_github_query)
        github_result = github_result_df['message'].iloc[0]
        expected_pattern = registry_pull_resp_pattern("github")
        self.assertTrue(re.search(expected_pattern, github_result), f"Expected pattern not found in result: {github_result}")
        print_test_result(f"""Test executeStmt method with pandas output\nRESULTS:\n{okta_result_df}\n{github_result_df}""", True)

    @pystackql_test_setup()
    def test_11_execute_with_defaults(self):
        result = self.stackql.execute(google_query)
        is_valid_data_resp = isinstance(result, list) and all(isinstance(item, dict) for item in result)
        self.assertTrue(is_valid_data_resp, f"Result is not valid: {result}")
        print_test_result(f"Test execute with defaults\nRESULT: {result}", is_valid_data_resp)

    def test_11a_execute_with_defaults_null_response(self):
        result = self.stackql.execute("SELECT 1 WHERE 1=0")
        is_valid_empty_resp = isinstance(result, list) and len(result) == 0
        self.assertTrue(is_valid_empty_resp, f"Result is not a empty list: {result}")
        print_test_result(f"Test execute with defaults (empty response)\nRESULT: {result}", is_valid_empty_resp)        

    @pystackql_test_setup(output='pandas')
    def test_12_execute_with_pandas_output(self):
        result = self.stackql.execute(aws_query)
        is_valid_dataframe = isinstance(result, pd.DataFrame)
        self.assertTrue(is_valid_dataframe, f"Result is not a valid DataFrame: {result}")
        # Check datatypes of the columns
        expected_dtypes = {
            'year': 'int64',
            'num_buckets': 'int64'
        }
        for col, expected_dtype in expected_dtypes.items():
            actual_dtype = result[col].dtype
            self.assertEqual(actual_dtype, expected_dtype, f"Column '{col}' has dtype '{actual_dtype}' but expected '{expected_dtype}'")
        print_test_result(f"Test execute with pandas output\nRESULT COUNT: {len(result)}", is_valid_dataframe)

    @pystackql_test_setup(output='csv')
    def test_13_execute_with_csv_output(self):
        result = self.stackql.execute(aws_query)
        is_valid_csv = isinstance(result, str) and result.count("\n") >= 1 and result.count(",") >= 1
        self.assertTrue(is_valid_csv, f"Result is not a valid CSV: {result}")
        print_test_result(f"Test execute with csv output\nRESULT_COUNT: {len(result.splitlines())}", is_valid_csv)

class PyStackQLAsyncTests(PyStackQLTestsBase):

    @async_test_decorator
    async def test_14_executeQueriesAsync(self):
        stackql = StackQL()
        results = await stackql.executeQueriesAsync(async_queries)
        is_valid_results = all(isinstance(res, dict) for res in results)
        print_test_result(f"[ASYNC] Test executeQueriesAsync with default (dict) output\nRESULT_COUNT: {len(results)}", is_valid_results)

    @async_test_decorator
    async def test_15_executeQueriesAsync_with_pandas_output(self):
        stackql = StackQL(output='pandas')
        result = await stackql.executeQueriesAsync(async_queries)
        is_valid_dataframe = isinstance(result, pd.DataFrame) and not result.empty
        print_test_result(f"[ASYNC] Test executeQueriesAsync with pandas output\nRESULT_COUNT: {len(result)}", is_valid_dataframe)

    @async_test_decorator
    async def test_16_executeQueriesAsync_with_csv_output(self):
        stackql = StackQL(output='csv')
        exception_caught = False
        try:
            # This should raise a ValueError since 'csv' output mode is not supported
            await stackql.executeQueriesAsync(async_queries)
        except ValueError as ve:
            exception_caught = str(ve) == "executeQueriesAsync supports only 'dict' or 'pandas' output modes."
        except Exception as e:
            pass
        print_test_result(f"[ASYNC] Test executeQueriesAsync with unsupported csv output", exception_caught)

class PyStackQLServerModeNonAsyncTests(PyStackQLTestsBase):

    @pystackql_test_setup(server_mode=True)
    def test_19_server_mode_connectivity(self):
        self.assertTrue(self.stackql.server_mode, "StackQL should be in server mode")
        self.assertIsNotNone(self.stackql._conn, "Connection object should not be None")
        print_test_result("Test server mode connectivity", True, True)

    @pystackql_test_setup(server_mode=True)
    def test_20_executeStmt_server_mode(self):
        result = self.stackql.executeStmt(registry_pull_google_query)
        # Checking if the result is a list containing a single dictionary with a key 'message' and value 'OK'
        is_valid_response = isinstance(result, list) and len(result) == 1 and result[0].get('message') == 'OK'
        print_test_result(f"Test executeStmt in server mode\n{result}", is_valid_response, True)

    @pystackql_test_setup(server_mode=True, output='pandas')
    def test_20a_executeStmt_server_mode_with_pandas_output(self):
        result_df = self.stackql.executeStmt(registry_pull_google_query)
        # Verifying if the result is a dataframe with a column 'message' containing the value 'OK' in its first row
        is_valid_response = isinstance(result_df, pd.DataFrame) and 'message' in result_df.columns and result_df['message'].iloc[0] == 'OK'
        print_test_result(f"Test executeStmt in server mode with pandas output\n{result_df}", is_valid_response, True)

    @pystackql_test_setup(server_mode=True)
    def test_21_execute_server_mode_default_output(self):
        result = self.stackql.execute(google_query)
        is_valid_dict_output = isinstance(result, list) and all(isinstance(row, dict) for row in result)
        print_test_result(f"""Test execute in server_mode with default output\nRESULT_COUNT: {len(result)}""", is_valid_dict_output, True)

    @pystackql_test_setup(server_mode=True, output='pandas')
    def test_22_execute_server_mode_pandas_output(self):
        result = self.stackql.execute(aws_query)
        is_valid_dataframe = isinstance(result, pd.DataFrame)
        self.assertTrue(is_valid_dataframe, f"Result is not a valid DataFrame: {result}")
        # Check datatypes of the columns
        expected_dtypes = {
            'year': 'int64',
            'num_buckets': 'int64'
        }
        for col, expected_dtype in expected_dtypes.items():
            actual_dtype = result[col].dtype
            self.assertEqual(actual_dtype, expected_dtype, f"Column '{col}' has dtype '{actual_dtype}' but expected '{expected_dtype}'")
        print_test_result(f"Test execute in server_mode with pandas output\nRESULT COUNT: {len(result)}", is_valid_dataframe)

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

class BaseStackQLMagicTests:
    MAGIC_CLASS = None  # To be overridden by child classes
    server_mode = None  # To be overridden by child classes
    def setUp(self):
        """Set up for the magic tests."""
        assert self.MAGIC_CLASS, "MAGIC_CLASS should be set by child classes"
        self.shell = MockInteractiveShell.instance()
        if self.server_mode:
            magics.load_ipython_extension(self.shell)
        else:
            magic.load_ipython_extension(self.shell)
        self.stackql_magic = self.MAGIC_CLASS(shell=self.shell)
        self.query = "SELECT 1 as fred"
        self.expected_result = pd.DataFrame({"fred": [1]})
        self.statement = "REGISTRY PULL github"

    def print_test_result(self, test_name, *checks):
        all_passed = all(checks)
        print_test_result(f"{test_name}", all_passed, self.server_mode, True)

    def run_magic_test(self, line, cell, expect_none=False):
        # Mock the run_query method to return a known DataFrame.
        self.stackql_magic.run_query = MagicMock(return_value=self.expected_result)
        # Execute the magic with our query.
        result = self.stackql_magic.stackql(line=line, cell=cell)
        # Validate the outcome.
        checks = []
        if expect_none:
            checks.append(result is None)
        else:
            checks.append(result.equals(self.expected_result))
        checks.append('stackql_df' in self.shell.user_ns)
        checks.append(self.shell.user_ns['stackql_df'].equals(self.expected_result))
        return checks
    
    def test_line_magic_query(self):
        checks = self.run_magic_test(line=self.query, cell=None)
        self.print_test_result("Line magic query test", *checks)

    def test_cell_magic_query(self):
        checks = self.run_magic_test(line="", cell=self.query)
        self.print_test_result("Cell magic query test", *checks)

    def test_cell_magic_query_no_output(self):
        checks = self.run_magic_test(line="--no-display", cell=self.query, expect_none=True)
        self.print_test_result("Cell magic query test (with --no-display)", *checks)

    def run_magic_statement_test(self, line, cell, expect_none=False):
        # Execute the magic with our statement.
        result = self.stackql_magic.stackql(line=line, cell=cell)
        # Validate the outcome.
        checks = []
        # Check that the output contains expected content
        if expect_none:
            checks.append(result is None)
        else:
            if self.server_mode:
                checks.append("OK" in result["message"].iloc[0])
            else:
                pattern = registry_pull_resp_pattern('github')
                message = result["message"].iloc[0] if "message" in result.columns else ""
                checks.append(bool(re.search(pattern, message)))        
        # Check dataframe exists and is populated as expected
        checks.append('stackql_df' in self.shell.user_ns)
        if self.server_mode:
            checks.append("OK" in self.shell.user_ns['stackql_df']["message"].iloc[0])
        else:
            pattern = registry_pull_resp_pattern('github')
            message = self.shell.user_ns['stackql_df']["message"].iloc[0] if 'stackql_df' in self.shell.user_ns else ""
            checks.append(bool(re.search(pattern, message)))
        return checks, result

    def test_line_magic_statement(self):
        checks, result = self.run_magic_statement_test(line=self.statement, cell=None)
        self.print_test_result(f"Line magic statement test\n{result}", *checks)

    def test_cell_magic_statement(self):
        checks, result = self.run_magic_statement_test(line="", cell=self.statement)
        self.print_test_result(f"Cell magic statement test\n{result}", *checks)

    def test_cell_magic_statement_no_output(self):
        checks, result = self.run_magic_statement_test(line="--no-display", cell=self.statement, expect_none=True)
        self.print_test_result(f"Cell magic statement test (with --no-display)\n{result}", *checks)

class StackQLMagicTests(BaseStackQLMagicTests, unittest.TestCase):

    MAGIC_CLASS = StackqlMagic
    server_mode = False

class StackQLServerMagicTests(BaseStackQLMagicTests, unittest.TestCase):
    MAGIC_CLASS = StackqlServerMagic
    server_mode = True

def main():
    unittest.main(verbosity=0)

if __name__ == '__main__':
    main()
