import sys, os, unittest, asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pystackql import StackQL
from .test_params import *

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
    print("downloading aws provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_aws_query)
    print(res)
    print("downloading google provider for tests...")
    res = PyStackQLTestsBase.stackql.executeStmt(registry_pull_google_query)
    print(res)
    print("starting stackql server...")
    PyStackQLTestsBase.server_process = subprocess.Popen([PyStackQLTestsBase.stackql.bin_path, "srv", "--pgsrv.address", server_address, "--pgsrv.port", str(server_port)])
    time.sleep(30)

def tearDownModule():
    print("stopping stackql server...")
    if PyStackQLTestsBase.server_process:
        PyStackQLTestsBase.server_process.terminate()
        PyStackQLTestsBase.server_process.wait()

class PyStackQLAsyncTests(PyStackQLTestsBase):

    @async_test_decorator
    async def test_executeQueriesAsync_server_mode_default_output(self):
        stackql = StackQL(server_mode=True)
        result = await stackql.executeQueriesAsync(async_queries)
        is_valid_result = isinstance(result, list) and all(isinstance(res, dict) for res in result)
        self.assertTrue(is_valid_result, f"Result is not a valid list of dicts: {result}")
        print_test_result(f"[ASYNC] Test executeQueriesAsync in server_mode with default output\nRESULT_COUNT: {len(result)}", is_valid_result, True)

    @async_test_decorator
    async def test_executeQueriesAsync_server_mode_pandas_output(self):
        stackql = StackQL(server_mode=True, output='pandas')
        result = await stackql.executeQueriesAsync(async_queries)
        is_valid_dataframe = isinstance(result, pd.DataFrame) and not result.empty
        self.assertTrue(is_valid_dataframe, f"Result is not a valid DataFrame: {result}")
        print_test_result(f"[ASYNC] Test executeQueriesAsync in server_mode with pandas output\nRESULT_COUNT: {len(result)}", is_valid_dataframe, True)

def main():
    unittest.main(verbosity=0)

if __name__ == '__main__':
    main()
