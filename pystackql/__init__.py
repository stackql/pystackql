from .stackql_magic import load_ipython_extension

from .util import (
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
	"""A class representing an instance of the StackQL query engine.

	:param platform: the operating system platform (read only)
	:type platform: str

	:param parse_json: whether to parse the output as JSON, defaults to `False` 
		unless overridden by setting `output` to `csv`, `table` or `text` as a `kwarg` in the `StackQL` object constructor (read only)
	:type parse_json: bool

	:param params: a list of command-line parameters passed to the StackQL executable, populated by the class constructor (read only)
	:type params: list
	
	:param download_dir: the download directory for the StackQL executable - defaults to site.getuserbase() unless overridden in the `StackQL` object constructor (read only)
	:type download_dir: str
	
	:param bin_path: the full path of the StackQL executable (read only)
	:type bin_path: str
	
	:param version: the version number of the StackQL executable (read only)
	:type version: str
	
	:param package_version: the version number of the pystackql Python package (read only)
	:type package_version: str	
	
	:param sha: the commit (short) sha for the installed `stackql` binary build (read only)
	:type sha: str
	
	:param auth: StackQL provider authentication object supplied using the class constructor (read only)
	:type auth: dict
	
	:param server_mode: Connect to a stackql server - defaults to `False` unless overridden in the `StackQL` object constructor (read only)
	:type server_mode: bool
	
	:param server_address: The address of the stackql server - defaults to `0.0.0.0` unless overridden in the `StackQL` object constructor (read only), only used if `server_mode` (read only)
	:type auth: str

	:param server_port: The port of the stackql server - defaults to `5466` unless overridden in the `StackQL` object constructor (read only), only used if `server_mode` (read only)
	:type auth: int
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

	def __init__(self, **kwargs):
		"""Constructor method
		"""
		# get platform and set property
		self.platform = _get_platform()

		# get each kwarg and set property
		self.parse_json = True
		self.params = ["exec"]
		output_set = False
		for key, value in kwargs.items():
			self.params.append("--%s" % key)
			if key == "output":
				output_set = True
				if value != "json":
					self.parse_json = False
			if key == "auth":
				authobj, authstr = _format_auth(value)
				value = authstr
				self.auth = authobj
			if key == "download_dir":
				self.download_dir = value
			self.params.append(value)
		if not output_set:
			self.params.append("--output")
			self.params.append("json")

		# set fq path
		binary = _get_binary_name(self.platform)
		# if download_dir not set, use site.getuserbase()
		if not hasattr(self, 'download_dir'):
			self.download_dir = _get_download_dir()
		self.bin_path = os.path.join(self.download_dir, binary)

		# get and set version
		if os.path.exists(self.bin_path):
			self.version, self.sha = _get_version(self.bin_path)
		else:
			_setup(self.download_dir, self.platform)
			self.version, self.sha = _get_version(self.bin_path)

		# get package version
		self.package_version = _get_package_version("pystackql")

		# server_mode props, connects to a server via the postgres wire protocol
		self.server_mode = kwargs.get("server_mode", False)
		if self.server_mode:
			self.server_address = kwargs.get("server_address", "0.0.0.0")
			self.server_port = kwargs.get("server_port", 5466)
   			# establish the connection
			self._conn = None
			if self.server_mode:
				self._conn = self._connect_to_server()			

	def properties(self):
		"""
		Retrieves the properties of the StackQL instance.

		This method collects all the attributes of the StackQL instance and
		returns them in a dictionary format.

		Returns:
			dict: A dictionary containing the properties of the StackQL instance.

		Example:
			{
				"platform": "Darwin x86_64 (macOS-12.0.1-x86_64-i386-64bit), Python 3.10.9",
				"parse_json": True,
				...
			}
		"""
		props = {}
		for var in vars(self):
			if var == "server_process":
				continue
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