from ._util import (
    _get_package_version,
    _get_platform,
    _get_download_dir,
    _get_binary_name,
	_is_binary_local,
    _setup,
    _get_version,
    _format_auth
)
import sys, subprocess, json, os, asyncio, functools
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd
import tempfile

from io import StringIO

class StackQL:
	"""A class representing an instance of the StackQL query engine.
	
	:param server_mode: Connect to a StackQL server 
		(defaults to `False`)
	:type server_mode: bool, optional
	:param server_address: The address of the StackQL server 
		(`server_mode` only, defaults to `'127.0.0.1'`)
	:type server_address: str, optional
	:param server_port: The port of the StackQL server 
		(`server_mode` only, defaults to `5466`)
	:type server_port: int, optional
	:param backend_storage_mode: Specifies backend storage mode, options are 'memory' and 'file'
		(defaults to `'memory'`, this option is ignored in `server_mode`)
	:type backend_storage_mode: str, optional
	:param backend_file_storage_location: Specifies location for database file, only applicable when `backend_storage_mode` is 'file'
		(defaults to `'{cwd}/stackql.db'`, this option is ignored in `server_mode`)
	:type backend_file_storage_location: str, optional
	:param output: Determines the format of the output, options are 'dict', 'pandas', and 'csv' 
		(defaults to `'dict'`, `'csv'` is not supported in `server_mode`)
	:type output: str, optional
	:param sep: Seperator for values in CSV output 
		(defaults to `','`, `output='csv'` only)
	:type sep: str, optional
	:param header: Show column headers in CSV output 
		(defaults to `False`, `output='csv'` only)
	:type header: bool, optional
	:param download_dir: The download directory for the StackQL executable 
		(defaults to `site.getuserbase()`, not supported in `server_mode`)
	:type download_dir: str, optional
	:param app_root: Application config and cache root path
		(defaults to `{cwd}/.stackql`)
	:type app_root: str, optional	
	:param execution_concurrency_limit: Concurrency limit for query execution
		(defaults to `-1` - unlimited)
	:type execution_concurrency_limit: int, optional
	:param dataflow_dependency_max: Max dataflow weakly connected components for a given query
		(defaults to `50`)
	:type dataflow_dependency_max: int, optional
	:param dataflow_components_max: Max dataflow dependency depth for a given query
		(defaults to `50`)
	:type dataflow_components_max: int, optional
	:param api_timeout: API timeout 
		(defaults to `45`, not supported in `server_mode`)
	:type api_timeout: int, optional
	:param proxy_host: HTTP proxy host 
		(not supported in `server_mode`)
	:type proxy_host: str, optional
	:param proxy_password: HTTP proxy password 
		(only applicable when `proxy_host` is set)
	:type proxy_password: str, optional
	:param proxy_port: HTTP proxy port 
		(defaults to `-1`, only applicable when `proxy_host` is set)
	:type proxy_port: int, optional
	:param proxy_scheme: HTTP proxy scheme 
		(defaults to `'http'`, only applicable when `proxy_host` is set)
	:type proxy_scheme: str, optional
	:param proxy_user: HTTP proxy user 
		(only applicable when `proxy_host` is set)
	:type proxy_user: str, optional
	:param max_results: Max results per HTTP request 
		(defaults to `-1` for no limit, not supported in `server_mode`)
	:type max_results: int, optional
	:param page_limit: Max pages of results that will be returned per resource 
		(defaults to `20`, not supported in `server_mode`)
	:type page_limit: int, optional
	:param max_depth: Max depth for indirect queries: views and subqueries 
		(defaults to `5`, not supported in `server_mode`)
	:type max_depth: int, optional
	:param custom_registry: Custom StackQL provider registry URL 
		(e.g. https://registry-dev.stackql.app/providers) supplied using the class constructor 
	:type custom_registry: str, optional	
	:param custom_auth: Custom StackQL provider authentication object supplied using the class constructor 
		(not supported in `server_mode`)
	:type custom_auth: dict, optional
	:param debug: Enable debug logging 
		(defaults to `False`)
	:type debug: bool, optional
	:param debug_log_file: Path to debug log file 
		(defaults to `~/.pystackql/debug.log`, only available if debug is `True`)
	:type debug_log_file: str, optional

	--- Read-Only Attributes ---
	
	:param platform: The operating system platform
	:type platform: str, readonly
	:param package_version: The version number of the `pystackql` Python package
	:type package_version: str, readonly
	:param version: The version number of the `stackql` executable 
		(not supported in `server_mode`)
	:type version: str, readonly
	:param params: A list of command-line parameters passed to the `stackql` executable 
		(not supported in `server_mode`)
	:type params: list, readonly
	:param bin_path: The full path of the `stackql` executable 
		(not supported in `server_mode`).
	:type bin_path: str, readonly
	:param sha: The commit (short) sha for the installed `stackql` binary build 
		(not supported in `server_mode`).
	:type sha: str, readonly
	"""

	def _debug_log(self, message):
		with open(self.debug_log_file, "a") as log_file:
			log_file.write(message + "\n")

	def _connect_to_server(self):
		"""Establishes a connection to the server using psycopg.

		:return: Connection object if successful, or `None` if an error occurred.
		:rtype: Connection or None
		:raises `psycopg.OperationalError`: Failed to connect to the server.
		"""
		try:
			conn = psycopg.connect(
				dbname='stackql',
				user='stackql',
				host=self.server_address,
				port=self.server_port,
				autocommit=True,
				row_factory=dict_row  # Use dict_row to get rows as dictionaries
			)
			return conn
		except psycopg.OperationalError as oe:
			print(f"OperationalError while connecting to the server: {oe}")
		except Exception as e:
			print(f"Unexpected error while connecting to the server: {e}")
		return None

	def _run_server_query(self, query, is_statement=False):
		"""Run a query against the server using the existing connection in server mode."""
		if not self._conn:
			raise ConnectionError("No active connection found. Ensure _connect_to_server is called.")

		try:
			with self._conn.cursor() as cur:
				cur.execute(query)
				if is_statement:
					# Return status message for non-SELECT statements
					result_msg = cur.statusmessage
					return [{'message': result_msg}]
				try:
					# Fetch results for SELECT queries
					rows = cur.fetchall()
					return rows
				except psycopg.ProgrammingError as e:
					# Handle cases with no results
					if "no results to fetch" in str(e):
						return []
					else:
						raise
		except psycopg.OperationalError as oe:
			print(f"OperationalError during query execution: {oe}")
		except Exception as e:
			print(f"Unexpected error during query execution: {e}")


	def _run_query(self, query, custom_auth=None, env_vars=None):
		"""Internal method to execute a StackQL query using a subprocess.

		The method spawns a subprocess to run the StackQL binary with the specified query and parameters.
		It waits for the subprocess to complete and captures its stdout as the output. This approach ensures 
		that resources like pipes are properly cleaned up after the subprocess completes.

		:param query: The StackQL query string to be executed.
		:type query: str
		:param custom_auth: Custom authentication dictionary.
		:type custom_auth: dict, optional
		:param env_vars: Command-specific environment variables for the subprocess.
		:type env_vars: dict, optional

		:return: The output result of the query, which can either be the actual query result or an error message.
		:rtype: dict

		Example:
			::

				{
					"data": "[{\"machine_type\": \"n1-standard-1\", \"status\": \"RUNNING\", \"num_instances\": 3}, ...]",
					"error": "stderr message if present",
					"exception": "ERROR: {\"exception\": \"<exception message>\", \"doc\": \"<exception doc>\", \"params\": \"<params>\", \"stdout\": \"<stdout>\", \"stderr\": \"<stderr>\"}
				}
		
		Possible error messages include:
		- Indications that the StackQL binary wasn't found.
		- Generic error messages for other exceptions encountered during the query execution.

		:raises FileNotFoundError: If the StackQL binary isn't found.
		:raises Exception: For any other exceptions during the execution, providing a generic error message.
		"""
		local_params = self.params.copy()
		local_params.insert(1, f'"{query}"')
		script_path = None

		# Handle custom authentication if provided
		if custom_auth:
			if '--auth' in local_params:
				# override auth set in the constructor with the command-specific auth
				auth_index = local_params.index('--auth')
				local_params.pop(auth_index)  # remove --auth
				local_params.pop(auth_index)  # remove the auth string
			authstr = json.dumps(custom_auth)
			local_params.extend(["--auth", f"'{authstr}'"])

		output = {}
		env_command_prefix = ""

		# Determine platform and set environment command prefix accordingly
		if env_vars:
			if self.platform.startswith("Windows"):
				with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w") as script_file:
					# Write environment variable setup and command to script file
					for key, value in env_vars.items():
						script_file.write(f'$env:{key} = "{value}";\n')
					script_file.write(f"{self.bin_path} " + " ".join(local_params) + "\n")
					script_path = script_file.name
				full_command = f"powershell -File {script_path}"
			else:
				# For Linux/Mac, use standard env variable syntax
				env_command_prefix = "env " + " ".join([f'{key}="{value}"' for key, value in env_vars.items()]) + " "
				full_command = env_command_prefix + " ".join([self.bin_path] + local_params)
		else:
			full_command = " ".join([self.bin_path] + local_params)

		try:
			with subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as iqlPopen:
				stdout, stderr = iqlPopen.communicate()

				if self.debug:
					self._debug_log(f"query: {query}")
					self._debug_log(f"stdout: {stdout}")
					self._debug_log(f"stderr: {stderr}")

				# Process stdout and stderr
				if stderr:
					output["error"] = stderr.decode('utf-8') if isinstance(stderr, bytes) else str(stderr)
				if stdout:
					output["data"] = stdout.decode('utf-8') if isinstance(stdout, bytes) else str(stdout)

		except FileNotFoundError:
			output["exception"] = f"ERROR: {self.bin_path} not found"
		except Exception as e:
			error_details = {
				"exception": str(e),
				"doc": e.__doc__,
				"params": local_params,
				"stdout": stdout.decode('utf-8') if 'stdout' in locals() and isinstance(stdout, bytes) else "",
				"stderr": stderr.decode('utf-8') if 'stderr' in locals() and isinstance(stderr, bytes) else ""
			}
			output["exception"] = f"ERROR: {json.dumps(error_details)}"
		finally:
			# Clean up the temporary script file
			if script_path is not None:
				os.remove(script_path) 
			return output

	def __init__(self, 
				 server_mode=False, 
				 server_address='127.0.0.1', 
				 server_port=5466,
				 backend_storage_mode='memory',
				 backend_file_storage_location='stackql.db', 
				 download_dir=None, 
				 app_root=None,
				 execution_concurrency_limit=-1,
				 dataflow_dependency_max=50,
				 dataflow_components_max=50,
				 output='dict',
				 custom_registry=None,
				 custom_auth=None,
				 sep=',', 
				 header=False, 
				 api_timeout=45, 
				 proxy_host=None, 
				 proxy_password=None, 
				 proxy_port=-1, 
				 proxy_scheme='http', 
				 proxy_user=None, 
				 max_results=-1, 
				 page_limit=20, 
				 max_depth=5,
				 debug=False,
				 http_debug=False,
				 debug_log_file=None):
		"""Constructor method
		"""
        # read only properties
		self.platform, this_os = _get_platform()
		self.package_version = _get_package_version("pystackql")

		# common constructor args
		# Check and assign the output if it is allowed, else raise ValueError
		ALLOWED_OUTPUTS = {'dict', 'pandas', 'csv'}
		if output.lower() not in ALLOWED_OUTPUTS:
			raise ValueError(f"Invalid output. Expected one of {ALLOWED_OUTPUTS}, got {output}.")
		self.output = output.lower()
		self.server_mode = server_mode
		if self.server_mode and self.output == 'csv':
			raise ValueError("CSV output is not supported in server mode, use 'dict' or 'pandas' instead.")
		
		self.debug = debug
		
		if debug:
			if debug_log_file is None:
				self.debug_log_file = os.path.join(os.path.expanduser("~"), '.pystackql', 'debug.log')
			else:
				self.debug_log_file = debug_log_file
			# Check if the path exists. If not, try to create it.
			log_dir = os.path.dirname(self.debug_log_file)
			if not os.path.exists(log_dir):
				try:
					os.makedirs(log_dir, exist_ok=True)  # exist_ok=True will not raise an error if the directory exists.
				except OSError as e:
					raise ValueError(f"Unable to create the log directory {log_dir}: {str(e)}")

		if self.server_mode:
			# server mode, connect to a server via the postgres wire protocol
			# Attempt to import psycopg only if server_mode is True
			global psycopg, dict_row
			try:
				import psycopg
				from psycopg.rows import dict_row  # For returning results as dictionaries
			except ImportError:
				raise ImportError("psycopg is required in server mode but is not installed. Please install psycopg and try again.")

			self.server_address = server_address
			self.server_port = server_port
			# establish the connection
			self._conn = self._connect_to_server()		
		else:
			# local mode, executes the binary locally
			self.params = []
			self.params.append("exec")

			self.params.append("--output")
			if self.output == "csv":
				self.params.append("csv")
			else:
				self.params.append("json")

			# backend storage settings
			if backend_storage_mode == 'file':
				self.params.append("--sqlBackend")
				self.params.append(json.dumps({ "dsn": f"file:{backend_file_storage_location}" }))

			# get or download the stackql binary
			binary = _get_binary_name(this_os)

			# check if the binary exists locally for Linux
			if this_os == 'Linux' and _is_binary_local(this_os) and download_dir is None:
				self.bin_path = '/usr/local/bin/stackql'
				self.download_dir = '/usr/local/bin'
				# get and set version
				self.version, self.sha = _get_version(self.bin_path)
			else:
				# if download_dir not set, use site.getuserbase() or the provided path
				if download_dir is None:
					self.download_dir = _get_download_dir()
				else:
					self.download_dir = download_dir
				self.bin_path = os.path.join(self.download_dir, binary)
				# get and set version
				if os.path.exists(self.bin_path):
					self.version, self.sha = _get_version(self.bin_path)
				else:
					# not installed, download
					_setup(self.download_dir, this_os)
					self.version, self.sha = _get_version(self.bin_path)

			# if app_root is set, use it
			if app_root is not None:
				self.app_root = app_root
				self.params.append("--approot")
				self.params.append(app_root)

			# set execution_concurrency_limit
			self.execution_concurrency_limit = execution_concurrency_limit
			self.params.append("--execution.concurrency.limit")
			self.params.append(str(execution_concurrency_limit))

			# set dataflow_dependency_max and dataflow_components_max
			self.dataflow_dependency_max = dataflow_dependency_max
			self.params.append("--dataflow.dependency.max")
			self.params.append(str(dataflow_dependency_max))

			self.dataflow_components_max = dataflow_components_max
			self.params.append("--dataflow.components.max")
			self.params.append(str(dataflow_components_max))

			# if custom_auth is set, use it
			if custom_auth is not None:
				authobj, authstr = _format_auth(custom_auth)
				self.auth = authobj
				self.params.append("--auth")
				self.params.append(authstr)

			# if custom_registry is set, use it
			if custom_registry is not None:
				self.custom_registry = custom_registry
				self.params.append("--registry")
				self.params.append(json.dumps({ "url": custom_registry }))

			# csv output
			if self.output == "csv":
				self.sep = sep
				self.params.append("--delimiter")
				self.params.append(sep)

				self.header = header
				if not self.header:
					self.params.append("--hideheaders")

			# app behavioural properties
			self.max_results = max_results
			self.params.append("--http.response.maxResults")
			self.params.append(str(max_results))

			self.page_limit = page_limit
			self.params.append("--http.response.pageLimit")
			self.params.append(str(page_limit))

			self.max_depth = max_depth
			self.params.append("--indirect.depth.max")
			self.params.append(str(max_depth))

			self.api_timeout = api_timeout
			self.params.append("--apirequesttimeout")
			self.params.append(str(api_timeout))

			if http_debug:
				self.http_debug = True
				self.params.append("--http.log.enabled")
			else:
				self.http_debug = False

			# proxy settings
			if proxy_host is not None:
				self.proxy_host = proxy_host
				self.params.append("--http.proxy.host")
				self.params.append(proxy_host)				

				self.proxy_port = proxy_port
				self.params.append("--http.proxy.port")
				self.params.append(proxy_port)

				self.proxy_user = proxy_user
				self.params.append("--http.proxy.user")
				self.params.append(proxy_user)

				self.proxy_password = proxy_password
				self.params.append("--http.proxy.password")
				self.params.append(proxy_password)

				# Check and assign the proxy_scheme if it is allowed, else raise ValueError
				ALLOWED_PROXY_SCHEMES = {'http', 'https'}
				if proxy_scheme.lower() not in ALLOWED_PROXY_SCHEMES:
					raise ValueError(f"Invalid proxy_scheme. Expected one of {ALLOWED_PROXY_SCHEMES}, got {proxy_scheme}.")
				self.proxy_scheme = proxy_scheme.lower()
				self.params.append("--http.proxy.scheme")
				self.params.append(proxy_scheme)				

	def properties(self):
		"""Retrieves the properties of the StackQL instance.

		This method collects all the attributes of the StackQL instance and
		returns them in a dictionary format.

		:return: A dictionary containing the properties of the StackQL instance.
		:rtype: dict

		Example:
			::

				{
					"platform": "Darwin x86_64 (macOS-12.0.1-x86_64-i386-64bit), Python 3.10.9",
					"parse_json": True,
					...
				}
		"""
		props = {}
		for var in vars(self):
			props[var] = getattr(self, var)
		return props

	def upgrade(self, showprogress=True):
		"""Upgrades the StackQL binary to the latest version available.

		This method initiates an upgrade of the StackQL binary. Post-upgrade,
		it updates the `version` and `sha` attributes of the StackQL instance
		to reflect the newly installed version.

		:param showprogress: Indicates if progress should be displayed during the upgrade. Defaults to True.
		:type showprogress: bool, optional

		:return: A message indicating the new version of StackQL post-upgrade.
		:rtype: str
		"""
		_setup(self.download_dir, self.platform, showprogress)
		self.version, self.sha = _get_version(self.bin_path)
		print("stackql upgraded to version %s" % (self.version))

	def executeStmt(self, query, custom_auth=None, env_vars=None):
		"""Executes a query using the StackQL instance and returns the output as a string.  
			This is intended for operations which do not return a result set, for example a mutation 
			operation such as an `INSERT` or a `DELETE` or life cycle method such as an `EXEC` operation
			or a `REGISTRY PULL` operation.

		This method determines the mode of operation (server_mode or local execution) based 
		on the `server_mode` attribute of the instance. If `server_mode` is True, it runs the query 
		against the server. Otherwise, it executes the query using a subprocess.

		:param query: The StackQL query string to be executed.
		:type query: str, list of dict objects, or Pandas DataFrame
		:param custom_auth: Custom authentication dictionary.
		:type custom_auth: dict, optional
		:param env_vars: Command-specific environment variables for this execution.
		:type env_vars: dict, optional		

		:return: The output result of the query in string format. If in `server_mode`, it 
				returns a JSON string representation of the result. 
		:rtype: dict, Pandas DataFrame or str (for `csv` output)

		Example:
			>>> from pystackql import StackQL
			>>> stackql = StackQL()
			>>> stackql_query = "REGISTRY PULL okta"
			>>> result = stackql.executeStmt(stackql_query)
			>>> result
		"""
		if self.server_mode:
			result = self._run_server_query(query, is_statement=True)
			if self.output == 'pandas':
				return pd.DataFrame(result)
			elif self.output == 'csv':
				# return the string representation of the result
				return result[0]['message']
			else:
				return result
		else:

			# returns either...
			# {'error': '<error message>'} if something went wrong; or
			# {'message': '<message>'} if the statement was executed successfully

			result = self._run_query(query, custom_auth=custom_auth, env_vars=env_vars)
		
			if "exception" in result:
				exception_msg = result["exception"]
				if self.output == 'pandas':
					return pd.DataFrame({'error': [exception_msg]}) if exception_msg else pd.DataFrame({'error': []})
				elif self.output == 'csv':
					return exception_msg
				else:
					return {"error": exception_msg}

			# message on stderr
			message = result.get("error", "")

			if self.output == 'pandas':
				return pd.DataFrame({'message': [message]}) if message else pd.DataFrame({'message': []})
			elif self.output == 'csv':
				return message
			else:
				# count number of rows in the message
				try:
					return {'message': message, 'rowsaffected': message.count('\n')}
				except Exception as e:
					return {'message': message, 'rowsaffected': 0}
	
	def execute(self, query, suppress_errors=True, custom_auth=None, env_vars=None):
		"""
		Executes a StackQL query and returns the output based on the specified output format.

		This method supports execution both in server mode and locally using a subprocess. In server mode,
		the query is sent to a StackQL server, while in local mode, it runs the query using a local binary.

		:param query: The StackQL query string to be executed.
		:type query: str
		:param suppress_errors: If set to True, the method will return an empty list if an error occurs.
		:type suppress_errors: bool, optional
		:param custom_auth: Custom authentication dictionary.
		:type custom_auth: dict, optional		
		:param env_vars: Command-specific environment variables for this execution.
		:type env_vars: dict, optional

		:return: The output of the query, which can be a list of dictionary objects, a Pandas DataFrame, 
					or a raw CSV string, depending on the configured output format.
		:rtype: list(dict) | pd.DataFrame | str

		:raises ValueError: If an unsupported output format is specified.

		:example:

			>>> stackql = StackQL()
			>>> query = '''
			... SELECT SPLIT_PART(machineType, '/', -1) as machine_type, status, COUNT(*) as num_instances
			... FROM google.compute.instances
			... WHERE project = 'stackql-demo' AND zone = 'australia-southeast1-a'
			... GROUP BY machine_type, status HAVING COUNT(*) > 2
			... '''
			>>> result = stackql.execute(query)
		"""
		if self.server_mode:
			result = self._run_server_query(query)
			if self.output == 'pandas':
				json_str = json.dumps(result)
				return pd.read_json(StringIO(json_str))
			elif self.output == 'csv':
				raise ValueError("CSV output is not supported in server_mode.")
			else: # Assume 'dict' output
				return result
		else:

			# returns either...
			# [{'error': <error json str>}] if something went wrong; or
			# [{<row1>},...] if the statement was executed successfully, messages to stderr 

			if self.http_debug:
				suppress_errors = False

			output = self._run_query(query, custom_auth=custom_auth, env_vars=env_vars)
			
			if "exception" in output:
				exception_msg = output["exception"]
				if self.output == 'pandas':
					return pd.DataFrame({'error': [exception_msg]}) if exception_msg else pd.DataFrame({'error': []})					
				elif self.output == 'csv':
					return exception_msg
				else:
					return [{"error": exception_msg}]

			if "data" in output:
				data = output["data"]
				# theres data, return it
				if self.output == 'csv':
					return data
				elif self.output == 'pandas':
					try:
						return pd.read_json(StringIO(data))
					except ValueError:
						return pd.DataFrame([{"error": "Invalid JSON output"}])
				else: # Assume 'dict' output
					try:
						retval = json.loads(data)
						return retval if retval else []
					except ValueError:
						return [{"error": f"Invalid JSON output : {data}"}]

			if "error" in output and not suppress_errors:
				# theres no data but there is stderr from the request, could be an expected error like a 404
				err_msg = output["error"]
				if self.output == 'csv':
					return err_msg
				elif self.output == 'pandas':
					return pd.DataFrame([{"error": err_msg}])
				else:
					return [{"error": err_msg}]

			return []

	# asnyc query support
	#

	def _run_server_query_with_new_connection(self, query):
		"""Run a query against a StackQL postgres wire protocol server with a new connection.
		"""
		try:
			# Establish a new connection using credentials and configurations
			with psycopg.connect(
				dbname='stackql',
				user='stackql',
				host=self.server_address,
				port=self.server_port,
				row_factory=dict_row
			) as conn:
				# Execute the query with a new cursor
				with conn.cursor() as cur:
					cur.execute(query)
					try:
						rows = cur.fetchall()
					except psycopg.ProgrammingError as e:
						if str(e) == "no results to fetch":
							rows = []
						else:
							raise
					return rows
		except psycopg.OperationalError as oe:
			print(f"OperationalError while connecting to the server: {oe}")
		except Exception as e:
			print(f"Unexpected error while connecting to the server: {e}")

	def _sync_query(self, query, new_connection=False):
		"""Synchronous function to perform the query.
		"""
		if self.server_mode and new_connection:
			# Directly get the list of dicts; no JSON string conversion needed.
			result = self._run_server_query_with_new_connection(query)
		elif self.server_mode:
			# Also directly get the list of dicts here.
			result = self._run_server_query(query)  # Assuming this is a method that exists
		else:
			# Convert the JSON string to a Python object (list of dicts).
			query_results = self._run_query(query)
			if "exception" in query_results:
				result = [{"error": query_results["exception"]}]
			if "error" in query_results:
				result = [{"error": query_results["error"]}]
			if "data" in query_results:
				result = json.loads(query_results["data"]) 
		# Convert the result to a DataFrame if necessary.
		if self.output == 'pandas':
			return pd.DataFrame(result)
		else:
			return result

	async def executeQueriesAsync(self, queries):
		"""Executes multiple StackQL queries asynchronously using the current StackQL instance.

		This method utilizes an asyncio event loop to concurrently run a list of provided 
		StackQL queries. Each query is executed independently, and the combined results of 
		all the queries are returned as a list of JSON objects if 'dict' output mode is selected,
		or as a concatenated DataFrame if 'pandas' output mode is selected.

		The order of the results in the returned list or DataFrame may not necessarily 
		correspond to the order of the queries in the input list due to the asynchronous nature 
		of execution.

		:param queries: A list of StackQL query strings to be executed concurrently.
		:type queries: list[str], required
		:return: A list of results corresponding to each query. Each result is a JSON object or a DataFrame.
		:rtype: list[dict] or pd.DataFrame
		:raises ValueError: If method is used in `server_mode` on an unsupported OS (anything other than Linux).
		:raises ValueError: If an unsupported output mode is selected (anything other than 'dict' or 'pandas').

		Example:
			>>> from pystackql import StackQL
			>>> stackql = StackQL()		
			>>> queries = [
			>>> \"\"\"SELECT '%s' as region, instanceType, COUNT(*) as num_instances 
			... FROM aws.ec2.instances 
			... WHERE region = '%s' 
			... GROUP BY instanceType\"\"\" % (region, region)
			>>> for region in regions ]
			>>> result = stackql.executeQueriesAsync(queries)

		Note:
			- When operating in `server_mode`, this method is not supported.
		"""
		if self.server_mode:
			raise ValueError("executeQueriesAsync are not supported in sever_mode.")
		if self.output not in ['dict', 'pandas']:
			raise ValueError("executeQueriesAsync supports only 'dict' or 'pandas' output modes.")
		async def main():
			with ThreadPoolExecutor() as executor:
				# New connection is created for each query in server_mode, reused otherwise.
				new_connection = self.server_mode
				# Gather results from all the async calls.
				loop = asyncio.get_event_loop()
				futures = [loop.run_in_executor(executor, self._sync_query, query, new_connection) for query in queries]
				results = await asyncio.gather(*futures)
			# Concatenate DataFrames if output mode is 'pandas'.
			if self.output == 'pandas':
				return pd.concat(results, ignore_index=True)
			else:
				return [item for sublist in results for item in sublist]
		# Running the async function
		return await main()
