import sys, os, unittest, asyncio, re
from unittest.mock import MagicMock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystackql import StackQL, magic, magics, StackqlMagic, StackqlServerMagic
from .test_params import *

def pystackql_test_setup(**kwargs):
    def decorator(func):
        def wrapper(self, *args):
            try:
                del self.stackql
            except AttributeError:
                pass
            self.stackql = StackQL(**kwargs)
            func(self, *args)
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
    print("downloading google provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_google_query)
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
        print_test_result(f"""Test 01 properties method\nPROPERTIES: {properties}""", True)

    @pystackql_test_setup()
    def test_02_version_attribute(self):
        version = self.stackql.version
        self.assertIsNotNone(version)
        is_valid_semver = bool(re.match(expected_version_pattern, version))
        self.assertTrue(is_valid_semver)
        print_test_result(f"""Test 02 version attribute\nVERSION: {version}""", is_valid_semver)

    @pystackql_test_setup()
    def test_03_package_version_attribute(self):
        package_version = self.stackql.package_version
        self.assertIsNotNone(package_version)
        is_valid_semver = bool(re.match(expected_package_version_pattern, package_version))
        self.assertTrue(is_valid_semver)
        print_test_result(f"""Test 03 package_version attribute\nPACKAGE VERSION: {package_version}""", is_valid_semver)

    @pystackql_test_setup()
    def test_04_platform_attribute(self):
        platform_string = self.stackql.platform
        self.assertIsNotNone(platform_string)
        is_valid_platform = bool(re.match(expected_platform_pattern, platform_string))
        self.assertTrue(is_valid_platform)
        print_test_result(f"""Test 04 platform attribute\nPLATFORM: {platform_string}""", is_valid_platform)

    @pystackql_test_setup()
    def test_05_bin_path_attribute(self):
        self.assertTrue(os.path.exists(self.stackql.bin_path))
        print_test_result(f"""Test 05 bin_path attribute with default download path\nBINARY PATH: {self.stackql.bin_path}""", os.path.exists(self.stackql.bin_path))

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
        print_test_result(f"""Test 06 setting a custom download_dir\nCUSTOM_DOWNLOAD_DIR: {expected_download_dir}""", version is not None and os.path.exists(expected_binary_path))

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
        print_test_result(f"""Test 07 csv output with defaults (comma delimited without headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup(output="csv", sep="|")
    def test_08_csv_output_with_pipe_separator(self):
        # Check if sep is set to '|'
        self.assertEqual(self.stackql.sep, "|", "Separator is not set to '|'")
        # Check if params list has --delimiter and |
        self.assertIn("--delimiter", self.stackql.params)
        self.assertIn("|", self.stackql.params)
        # Check if --hideheaders is in params list
        self.assertIn("--hideheaders", self.stackql.params)
        print_test_result(f"""Test 08 csv output with custom sep (pipe delimited without headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup(output="csv", header=True)
    def test_09_csv_output_with_header(self):
        # Check if header is set to True
        self.assertTrue(self.stackql.header, "Header is not set to True")
        # Check if params list does not have --hideheaders
        self.assertNotIn("--hideheaders", self.stackql.params)
        print_test_result(f"""Test 09 csv output with headers (comma delimited with headers)\nPARAMS: {self.stackql.params}""", True)

    @pystackql_test_setup()
    def test_10_executeStmt(self):
        okta_result_dict = self.stackql.executeStmt(registry_pull_okta_query)
        okta_result = okta_result_dict["message"]
        expected_pattern = registry_pull_resp_pattern("okta")
        self.assertTrue(re.search(expected_pattern, okta_result), f"Expected pattern not found in result: {okta_result}")
        print_test_result(f"""Test 10 executeStmt method\nRESULTS:\n{okta_result_dict}""", True)

    @pystackql_test_setup(output="csv")
    def test_11_executeStmt_with_csv_output(self):
        github_result = self.stackql.executeStmt(registry_pull_github_query)
        expected_pattern = registry_pull_resp_pattern("github")
        self.assertTrue(re.search(expected_pattern, github_result), f"Expected pattern not found in result: {github_result}")
        print_test_result(f"""Test 11 executeStmt method with csv output\nRESULTS:\n{github_result}""", True)

    @pystackql_test_setup(output="pandas")
    def test_12_executeStmt_with_pandas_output(self):
        homebrew_result_df = self.stackql.executeStmt(registry_pull_homebrew_query)
        homebrew_result = homebrew_result_df['message'].iloc[0]
        expected_pattern = registry_pull_resp_pattern("homebrew")
        self.assertTrue(re.search(expected_pattern, homebrew_result), f"Expected pattern not found in result: {homebrew_result}")
        print_test_result(f"""Test 12 executeStmt method with pandas output\nRESULTS:\n{homebrew_result_df}""", True)

    @pystackql_test_setup()
    def test_13_execute_with_defaults(self):
        result = self.stackql.execute(google_show_services_query)
        is_valid_data_resp = (
            isinstance(result, list) 
            and all(isinstance(item, dict) and 'error' not in item for item in result)
        )
        # Truncate the result message if it's too long
        truncated_result = (
            str(result)[:500] + '...' if len(str(result)) > 500 else str(result)
        )
        self.assertTrue(is_valid_data_resp, f"Result is not valid: {truncated_result}")
        print_test_result(f"Test 13 execute with defaults\nRESULT: {truncated_result}", is_valid_data_resp)


    def test_14_execute_with_defaults_null_response(self):
        result = self.stackql.execute("SELECT 1 WHERE 1=0")
        is_valid_empty_resp = isinstance(result, list) and len(result) == 0
        self.assertTrue(is_valid_empty_resp, f"Result is not a empty list: {result}")
        print_test_result(f"Test 14 execute with defaults (empty response)\nRESULT: {result}", is_valid_empty_resp)        

    @pystackql_test_setup(output='pandas')
    @patch('pystackql.StackQL.execute')
    def test_15_execute_with_pandas_output(self, mock_execute):
        # mocking the response for pandas DataFrame
        mock_execute.return_value = pd.DataFrame({
            'status': ['RUNNING', 'TERMINATED'], 
            'num_instances': [2, 1]
        })

        result = self.stackql.execute(google_query)
        is_valid_dataframe = isinstance(result, pd.DataFrame)
        self.assertTrue(is_valid_dataframe, f"Result is not a valid DataFrame: {result}")
        # Check datatypes of the columns
        expected_dtypes = {
            'status': 'object',
            'num_instances': 'int64'
        }
        for col, expected_dtype in expected_dtypes.items():
            actual_dtype = result[col].dtype
            self.assertEqual(actual_dtype, expected_dtype, f"Column '{col}' has dtype '{actual_dtype}' but expected '{expected_dtype}'")
        print_test_result(f"Test 15 execute with pandas output\nRESULT COUNT: {len(result)}", is_valid_dataframe)

    @pystackql_test_setup(output='csv')
    @patch('pystackql.StackQL.execute')
    def test_16_execute_with_csv_output(self, mock_execute):
        # mocking the response for csv output
        mock_execute.return_value = "status,num_instances\nRUNNING,2\nTERMINATED,1\n" 
        result = self.stackql.execute(google_query)
        is_valid_csv = isinstance(result, str) and result.count("\n") >= 1 and result.count(",") >= 1
        self.assertTrue(is_valid_csv, f"Result is not a valid CSV: {result}")
        print_test_result(f"Test 16 execute with csv output\nRESULT_COUNT: {len(result.splitlines())}", is_valid_csv)

    @pystackql_test_setup()
    def test_17_execute_default_auth_dict_output(self):
        result = self.stackql.execute(github_query)
        # Expected result based on default auth
        expected_result = [
            {"login": "stackql-devops-1"}
        ]
        self.assertTrue(isinstance(result, list), "Result should be a list")
        self.assertEqual(result, expected_result, f"Expected result: {expected_result}, got: {result}")
        print_test_result(f"Test 17 execute with default auth and dict output\nRESULT: {result}", result == expected_result)


    @pystackql_test_setup()
    def test_18_execute_custom_auth_env_vars(self):
        # Set up custom environment variables for authentication
        env_vars = {
            'command_specific_username': os.getenv('CUSTOM_STACKQL_GITHUB_USERNAME'),
            'command_specific_password': os.getenv('CUSTOM_STACKQL_GITHUB_PASSWORD')
        }
        # Define custom authentication configuration
        custom_auth = {
            "github": {
                "type": "basic",
                "username_var": "command_specific_username",
                "password_var": "command_specific_password"
            }
        }
        result = self.stackql.execute(github_query, custom_auth=custom_auth, env_vars=env_vars)
        # Expected result based on custom auth
        expected_result = [
            {"login": "stackql-devops-2"}
        ]
        self.assertTrue(isinstance(result, list), "Result should be a list")
        self.assertEqual(result, expected_result, f"Expected result: {expected_result}, got: {result}")
        print_test_result(f"Test 18 execute with custom auth and command-specific environment variables\nRESULT: {result}", result == expected_result)


@unittest.skipIf(platform.system() == "Windows", "Skipping async tests on Windows")
class PyStackQLAsyncTests(PyStackQLTestsBase):

    @async_test_decorator
    async def test_01_async_executeQueriesAsync(self):
        stackql = StackQL()
        results = await stackql.executeQueriesAsync(async_queries)
        is_valid_results = all(isinstance(res, dict) for res in results)
        print_test_result(f"Test 01 executeQueriesAsync with default (dict) output\nRESULT_COUNT: {len(results)}", is_valid_results, is_async=True)

    @async_test_decorator
    async def test_02_async_executeQueriesAsync_with_pandas_output(self):
        stackql = StackQL(output='pandas')
        result = await stackql.executeQueriesAsync(async_queries)
        is_valid_dataframe = isinstance(result, pd.DataFrame) and not result.empty
        print_test_result(f"Test 02 executeQueriesAsync with pandas output\nRESULT_COUNT: {len(result)}", is_valid_dataframe, is_async=True)

    @async_test_decorator
    async def test_03_async_executeQueriesAsync_with_csv_output(self):
        stackql = StackQL(output='csv')
        exception_caught = False
        try:
            # This should raise a ValueError since 'csv' output mode is not supported
            await stackql.executeQueriesAsync(async_queries)
        except ValueError as ve:
            exception_caught = str(ve) == "executeQueriesAsync supports only 'dict' or 'pandas' output modes."
        except Exception as e:
            pass
        print_test_result(f"Test 03 executeQueriesAsync with unsupported csv output", exception_caught, is_async=True)

class PyStackQLServerModeNonAsyncTests(PyStackQLTestsBase):

    @pystackql_test_setup(server_mode=True)
    def test_01_server_mode_connectivity(self):
        self.assertTrue(self.stackql.server_mode, "StackQL should be in server mode")
        self.assertIsNotNone(self.stackql._conn, "Connection object should not be None")
        print_test_result("Test 01 server mode connectivity", True, True)

    @pystackql_test_setup(server_mode=True)
    def test_02_server_mode_executeStmt(self):
        result = self.stackql.executeStmt(registry_pull_google_query)
        # Checking if the result is a list containing a single dictionary with a key 'message' and value 'OK'
        is_valid_response = isinstance(result, list) and len(result) == 1 and result[0].get('message') == 'OK'
        print_test_result(f"Test 02 executeStmt in server mode\n{result}", is_valid_response, True)

    @pystackql_test_setup(server_mode=True, output='pandas')
    def test_03_server_mode_executeStmt_with_pandas_output(self):
        result_df = self.stackql.executeStmt(registry_pull_google_query)
        # Verifying if the result is a dataframe with a column 'message' containing the value 'OK' in its first row
        is_valid_response = isinstance(result_df, pd.DataFrame) and 'message' in result_df.columns and result_df['message'].iloc[0] == 'OK'
        print_test_result(f"Test 03 executeStmt in server mode with pandas output\n{result_df}", is_valid_response, True)

    @pystackql_test_setup(server_mode=True)
    @patch('pystackql.stackql.StackQL._run_server_query')
    def test_04_server_mode_execute_default_output(self, mock_run_server_query):
        # Mocking the response as a list of dictionaries
        mock_result = [
            {'status': 'RUNNING', 'num_instances': 2},
            {'status': 'TERMINATED', 'num_instances': 1}
        ]
        mock_run_server_query.return_value = mock_result

        result = self.stackql.execute(google_query)
        is_valid_dict_output = isinstance(result, list) and all(isinstance(row, dict) for row in result)
        print_test_result(f"""Test 04 execute in server_mode with default output\nRESULT_COUNT: {len(result)}""", is_valid_dict_output, True)
        # Check `_run_server_query` method
        mock_run_server_query.assert_called_once_with(google_query)

    @pystackql_test_setup(server_mode=True, output='pandas')
    @patch('pystackql.stackql.StackQL._run_server_query')
    def test_05_server_mode_execute_pandas_output(self, mock_run_server_query):
        # Mocking the response for pandas DataFrame
        mock_df = pd.DataFrame({
            'status': ['RUNNING', 'TERMINATED'],
            'num_instances': [2, 1]
        })
        mock_run_server_query.return_value = mock_df.to_dict(orient='records')
        result = self.stackql.execute(google_query)
        is_valid_dataframe = isinstance(result, pd.DataFrame)
        self.assertTrue(is_valid_dataframe, f"Result is not a valid DataFrame: {result}")
        # Check datatypes of the columns
        expected_dtypes = {
            'status': 'object',
            'num_instances': 'int64'
        }        
        for col, expected_dtype in expected_dtypes.items():
            actual_dtype = result[col].dtype
            self.assertEqual(actual_dtype, expected_dtype, f"Column '{col}' has dtype '{actual_dtype}' but expected '{expected_dtype}'")
        print_test_result(f"Test 05 execute in server_mode with pandas output\nRESULT COUNT: {len(result)}", is_valid_dataframe)
        # Check `_run_server_query` method
        mock_run_server_query.assert_called_once_with(google_query)

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
    
    def test_01_line_magic_query(self):
        checks = self.run_magic_test(line=self.query, cell=None)
        self.print_test_result("Test 01 Line magic query test", *checks)

    def test_02_cell_magic_query(self):
        checks = self.run_magic_test(line="", cell=self.query)
        self.print_test_result("Test 02 Cell magic query test", *checks)

    def test_03_cell_magic_query_no_output(self):
        checks = self.run_magic_test(line="--no-display", cell=self.query, expect_none=True)
        self.print_test_result("Test 03 Cell magic query test (with --no-display)", *checks)

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

    def test_04_line_magic_statement(self):
        checks, result = self.run_magic_statement_test(line=self.statement, cell=None)
        self.print_test_result(f"Test 04 Line magic statement test\n{result}", *checks)

    def test_05_cell_magic_statement(self):
        checks, result = self.run_magic_statement_test(line="", cell=self.statement)
        self.print_test_result(f"Test 05 Cell magic statement test\n{result}", *checks)

    def test_06_cell_magic_statement_no_output(self):
        checks, result = self.run_magic_statement_test(line="--no-display", cell=self.statement, expect_none=True)
        self.print_test_result(f"Test 06 Cell magic statement test (with --no-display)\n{result}", *checks)

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
