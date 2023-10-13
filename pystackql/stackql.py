from ._util import (
    _get_package_version,
    _get_platform,
    _get_download_dir,
    _get_binary_name,
    _setup,
    _get_version,
    _format_auth,
    _execute_queries_in_parallel
)
import sys, subprocess, json, os, asyncio, functools, psycopg2
from concurrent.futures import ProcessPoolExecutor
from psycopg2.extras import RealDictCursor

class StackQL:
	"""
	A class representing an instance of the StackQL query engine.

	download_dir: The download directory for the StackQL executable.
		:type download_dir: str
		:default: site.getuserbase()
		:note: only applicable when server_mode=False.

	server_mode: Connect to a StackQL server.
		:type server_mode: bool
		:default: False
	
	server_address: The address of the StackQL server.
		:type server_address: str
		:default: '0.0.0.0'
		:note: only applicable when server_mode=True.
	
	server_port: The port of the StackQL server.
		:type server_port: int
		:default: 5466
		:note: only applicable when server_mode=True.
	
	output: Determines the format of the output, options are 'dict', 'pandas', and 'csv'.
		:type output: str
		:default: 'dict'
		:options: ['dict', 'pandas', 'csv']
		:note: 'csv' is not supported in server_mode
	
	delimiter: (Only if output='csv') Delimiter character for CSV output.
		:type delimiter: str
		:default: ','

	hide_headers: (Only if output='csv') Whether to hide headers in CSV output.
		:type hide_headers: bool
		:default: False

	api_timeout: (server_mode=False only) API timeout.
		:type api_timeout: int
		:default: 45
	
	proxy_host: (server_mode=False only) HTTP proxy host.
		:type proxy_host: str
		:default: None
	
	proxy_password: (server_mode=False only) HTTP proxy password.
		:type proxy_password: str
		:default: None

	proxy_port: (server_mode=False only) HTTP proxy port.
		:type proxy_port: int
		:default: -1
	
	proxy_scheme: (server_mode=False only) HTTP proxy scheme.
		:type proxy_scheme: str
		:default: 'http'
	
	proxy_user: (server_mode=False only) HTTP proxy user.
		:type proxy_user: str
		:default: None
	
	max_results: (server_mode=False only) Max results per HTTP request.
		:type max_results: int
		:default: -1
	
	page_limit: (server_mode=False only) Max pages of results that will be returned per resource.
		:type page_limit: int
		:default: 20
	
	max_depth: (server_mode=False only) Max depth for indirect queries: views and subqueries.
		:type max_depth: int
		:default: 5
	
	--- Read-Only Attributes ---
	
	platform: The operating system platform.
		:type platform: str
	
	package_version: The version number of the pystackql Python package.
		:type package_version: str
	
	version: (server_mode=False only) The version number of the StackQL executable.
		:type version: str
	
	params: (server_mode=False only) A list of command-line parameters passed to the StackQL executable.
		:type params: list
	
	bin_path: (server_mode=False only) The full path of the StackQL executable.
		:type bin_path: str
	
	sha: (server_mode=False only) The commit (short) sha for the installed `stackql` binary build.
		:type sha: str
	
	auth: (server_mode=False only) StackQL provider authentication object supplied using the class constructor.
		:type auth: dict
	"""

	def _connect_to_server(self):
		"""Establishes a connection to the server using psycopg.
		
		Returns:
			Connection object if successful, or None if an error occurred.
		"""
		try:
			conn = psycopg2.connect(
				dbname='stackql',
				user='stackql',
				host=self.server_address,
				port=self.server_port
			)
			return conn
		except psycopg2.OperationalError as oe:
			print(f"OperationalError while connecting to the server: {oe}")
		except Exception as e:
			# Catching all other possible psycopg2 exceptions (and possibly other unexpected exceptions).
			# You might want to log this or handle it differently in a real-world scenario.
			print(f"Unexpected error while connecting to the server: {e}")
		return None

	def _run_server_query(self, query):
		"""
		Runs a query against the server using psycopg2.
		
		:param query: SQL query to be executed on the server.
		:type query: str
		:return: List of result rows if the query fetches results; empty list if there are no results.
		:rtype: list
		:raises: psycopg2.ProgrammingError for issues related to the SQL query, 
				unless the error is "no results to fetch", in which case an empty list is returned.
		"""
		conn = self._connect_to_server()
		try:
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.execute(query)
			rows = cur.fetchall()
			cur.close()
			return rows
		except psycopg2.ProgrammingError as e:
			if str(e) == "no results to fetch":
				return []
			else:
				raise

	def _run_query(self, query):
		"""
		Internal method to execute a StackQL query using a subprocess.

		The method spawns a subprocess to run the StackQL binary with the specified query and parameters.
		It waits for the subprocess to complete and captures its stdout as the output. This approach ensures 
		that resources like pipes are properly cleaned up after the subprocess completes.

		:param query: The StackQL query string to be executed.
		:type query: str

		:return: The output result of the query, which can either be the actual query result or an error message.
		:rtype: str

		Possible error messages include:
		- Indications that the StackQL binary wasn't found.
		- Generic error messages for other exceptions encountered during the query execution.

		:raises FileNotFoundError: If the StackQL binary isn't found.
		:raises Exception: For any other exceptions during the execution, providing a generic error message.
		"""		
		local_params = self.params.copy()
		local_params.insert(1, query)
		try:
			with subprocess.Popen([self.bin_path] + local_params,
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as iqlPopen:
				stdout, _ = iqlPopen.communicate()
				return stdout.decode('utf-8')
		except FileNotFoundError:
			return "ERROR %s not found" % self.bin_path
		except Exception as e:
			return "ERROR %s %s" % (str(e), e.__doc__)

	def __init__(self, 
				 server_mode=False, 
				 server_address='0.0.0.0', 
				 server_port=5466, 
				 download_dir=None, 
				 output='dict',
				 custom_auth=None,
				 delimiter=',', 
				 hide_headers=False, 
				 api_timeout=45, 
				 proxy_host=None, 
				 proxy_password=None, 
				 proxy_port=-1, 
				 proxy_scheme='http', 
				 proxy_user=None, 
				 max_results=-1, 
				 page_limit=20, 
				 max_depth=5):
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
		
		if self.server_mode:
			# server mode, connect to a server via the postgres wire protocol
			self.server_address = server_address
			self.server_port = server_port
   			# establish the connection
			self._conn = self._connect_to_server()
		else:
			# local mode, executes the binary locally
			self.params = []
			self.params.append("exec")

			# get or download the stackql binary
			binary = _get_binary_name(this_os)
			# if download_dir not set, use site.getuserbase()
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

			# if custom_auth is set, use it
			if custom_auth is not None:
				authobj, authstr = _format_auth(custom_auth)
				self.auth = authobj
				self.params.append("--auth")
				self.params.append(authstr)

			# csv output
			if output == 'csv':
				self.delimiter = delimiter
				self.params.append("--delimiter")
				self.params.append(delimiter)

				self.hide_headers = hide_headers
				if self.hide_headers:
					self.params.append("--hideheaders")

			# app behavioural properties
			self.max_results = max_results
			self.params.append("--http.response.maxResults")
			self.params.append(max_results)

			self.page_limit = page_limit
			self.params.append("--http.response.pageLimit")
			self.params.append(page_limit)

			self.max_depth = max_depth
			self.params.append("--indirect.depth.max")
			self.params.append(max_depth)

			self.api_timeout = api_timeout
			self.params.append("--apirequesttimeout")
			self.params.append(api_timeout)

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
		"""
		Retrieves the properties of the StackQL instance.

		This method collects all the attributes of the StackQL instance and
		returns them in a dictionary format.

		Returns:
			dict: A dictionary containing the properties of the StackQL instance.

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
		"""
		Upgrades the StackQL binary to the latest version available.

		This method initiates an upgrade of the StackQL binary. Post-upgrade,
		it updates the `version` and `sha` attributes of the StackQL instance
		to reflect the newly installed version.

		Parameters:
			showprogress (bool, optional): Indicates if progress should be displayed
										during the upgrade. Defaults to True.

		Prints:
			str: A message indicating the new version of StackQL post-upgrade.

		Example:
			stackql upgraded to version v0.5.396
		"""
		_setup(self.download_dir, self.platform, showprogress)
		self.version, self.sha = _get_version(self.bin_path)
		print("stackql upgraded to version %s" % (self.version))

	def executeStmt(self, query):
		"""Executes a query using the StackQL instance and returns the output as a string.  
			This is intended for operations which do not return a result set, for example a mutation 
			operation such as an `INSERT` or a `DELETE` or life cycle method such as an `EXEC` operation.

		This method determines the mode of operation (server_mode or local execution) based 
		on the `server_mode` attribute of the instance. If `server_mode` is True, it runs the query 
		against the server. Otherwise, it executes the query using a subprocess.

		:param query: The StackQL query string to be executed.
		:type query: str

		:return: The output result of the query in string format. If in `server_mode`, it 
				returns a JSON string representation of the result. 
		:rtype: str

		Note: In `server_mode`, the method internally converts the result from the server to a 
			JSON string before returning.
		"""
		if self.server_mode:
			# Use server mode
			result = self._run_server_query(query)
			return json.dumps(result)
		else:
			return self._run_query(query)
	
	def execute(self, query):
		"""Executes a query using the StackQL instance and returns the output as a string 
			or JSON object depending on the value of `parse_json` property.

		Depending on the `server_mode` attribute of the instance, this method either runs the 
		query against the StackQL server or executes it locally using a subprocess. 

		If the `parse_json` attribute is set to True, the method tries to return the result 
		as a JSON object. If parsing fails (in local execution), it returns an error message 
		within a JSON string.

		:param query: The StackQL query string to be executed.
		:type query: str

		:return: The output result of the query. Depending on the `parse_json` attribute and 
				the mode of execution, the result can be a JSON object, a JSON string, or a 
				raw string.
		:rtype: str or dict

		Note: If `server_mode` is enabled and `parse_json` is True, the result is directly 
			returned as a JSON object.
		"""
		if self.server_mode:
			# Use server mode
			result = self._run_server_query(query)
			if self.parse_json:
				return result  # Directly return the parsed result as a JSON object
			else:
				return json.dumps(result)  # Convert it into a string and then return
		else:
			output = self._run_query(query)
			if self.parse_json:
				try:
					return json.loads(output)
				except ValueError:
					return '[{"error": "%s"}]' % output.strip()
			return output

	async def _execute_queries_async(self, queries_list):
		loop = asyncio.get_event_loop()

		# Use functools.partial to bind the necessary arguments
		func = functools.partial(_execute_queries_in_parallel, self, queries_list)

		with ProcessPoolExecutor() as executor:
			results = await loop.run_in_executor(executor, func)

		# Process results based on their type:
		combined = []
		for res in results:
			if isinstance(res, str):
				combined.extend(json.loads(res))
			elif isinstance(res, list):
				combined.extend(res)
			else:
				# Optionally handle other types, or raise an error.
				pass

		return combined

	def executeQueriesAsync(self, queries):
		"""
		Executes multiple StackQL queries asynchronously using the current StackQL instance.

		This method utilizes an asyncio event loop to concurrently run a list of provided 
		StackQL queries. Each query is executed independently, and the combined results of 
		all the queries are returned as a list of JSON objects.

		Note: The order of the results in the returned list may not necessarily correspond
		to the order of the queries in the input list due to the asynchronous nature of execution.

		:param queries: A list of StackQL query strings to be executed concurrently.
		:type queries: list[str], required

		:return: A list of results corresponding to each query. Each result is a JSON object.
		:rtype: list[dict]

		Example:
			>>> queries = [
			>>> "SELECT '%s' as region, instanceType, COUNT(*) as num_instances FROM aws.ec2.instances WHERE region = '%s' GROUP BY instanceType" % (region, region)
			>>> for region in regions ]
			>>> res = stackql.executeQueriesAsync(queries)
		"""
		
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		combined_results = loop.run_until_complete(self._execute_queries_async(queries))
		loop.close()
		return combined_results