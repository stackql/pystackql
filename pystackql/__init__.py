import sys, subprocess, platform, json, site, os, requests, zipfile, asyncio, functools
from concurrent.futures import ProcessPoolExecutor

def _get_platform():
	return platform.system()

def _get_download_dir():
	# check if site.getuserbase() dir exists
	if not os.path.exists(site.getuserbase()):
		# if not, create it
		os.makedirs(site.getuserbase())
	return site.getuserbase()

def _get_binary_name(platform):
	if platform == 'Windows':
		return r'stackql.exe'
	elif platform == 'Darwin':
		return r'stackql/Payload/stackql'
	else:
		return r'stackql'

def _get_url(platform):
	if platform == 'Linux':
		return 'https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip'
	elif platform == 'Windows':
		return 'https://releases.stackql.io/stackql/latest/stackql_windows_amd64.zip'
	elif platform == 'Darwin':
		return 'https://storage.googleapis.com/stackql-public-releases/latest/stackql_darwin_multiarch.pkg'
	else:
		raise Exception("ERROR: [_get_url] unsupported OS type: %s" % (platform))

def _download_file(url, path, showprogress=True):
	try:
		r = requests.get(url, stream=True)
		r.raise_for_status()
		total_size_in_bytes = int(r.headers.get('content-length', 0))
		block_size = 1024
		with open(path, 'wb') as f:
			chunks = 0
			for data in r.iter_content(block_size):
				chunks += 1
				f.write(data)
				downloaded_size = chunks * block_size
				progress_bar = '#' * int(downloaded_size / total_size_in_bytes * 20)
				if showprogress:
					print(f'\r[{progress_bar.ljust(20)}] {int(downloaded_size / total_size_in_bytes * 100)}%', end='')

		print("\nDownload complete.")
	except Exception as e:
		print("ERROR: [_download_file] %s" % (str(e)))
		exit(1)

def _setup(download_dir, platform, showprogress=False):
	print('installing stackql...')
	try:
		binary_name = _get_binary_name(platform)
		url = _get_url(platform)
		print("downloading latest version of stackql from %s to %s" % (url, download_dir))
		archive_file_name = os.path.join(download_dir, os.path.basename(url))
		_download_file(url, archive_file_name, showprogress)
		if platform == 'Darwin':
			unpacked_file_name = os.path.join(download_dir, 'stackql')
			command = 'pkgutil --expand-full {} {}'.format(archive_file_name, unpacked_file_name)
			os.system(command)
		else:
			with zipfile.ZipFile(archive_file_name, 'r') as zip_ref:
				zip_ref.extractall(download_dir) 

		os.chmod(os.path.join(download_dir, binary_name), 0o755)
	except Exception as e:
		print("ERROR: [_setup] %s" % (str(e)))
		exit(1)

def _get_version(bin_path):
	try:
		iqlPopen = subprocess.Popen([bin_path] + ["--version"],
							stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		output = iqlPopen.stdout.read()
		iqlPopen.terminate()
		version_tokens = str(output, 'utf-8').split('\n')[0].split(' ')
		version = version_tokens[1]
		sha = version_tokens[3].replace('(', '').replace(')', '')
		return(version, sha)
	except FileNotFoundError:
		print("ERROR: [_get_version] %s not found" % (bin_path))
		exit(1)
	except Exception as e:
		error_message = e.args[0]
		print("ERROR: [_get_version] %s" % (error_message))		
		exit(1)

def _format_auth(auth):
	try:
		if auth is not None:
			if isinstance(auth, str):
				authobj = json.loads(auth)
				authstr = auth
			elif isinstance(auth, dict):
				authobj = auth
				authstr = json.dumps(auth)
			return authobj, authstr
		else:
			raise Exception("ERROR: [_format_auth] auth key supplied with no value")
	except Exception as e:
		error_message = e.args[0]
		print("ERROR: [_format_auth] %s" % (error_message))
		exit(1)

def _execute_queries_in_parallel(stackql_instance, queries):
    return [stackql_instance.execute(query) for query in queries]

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
	:param sha: the commit (short) sha for the installed `stackql` binary build (read only)
	:type sha: str
	:param auth: StackQL provider authentication object supplied using the class constructor (read only)
	:type auth: dict
	:param server_mode: Run stackql in server mode - defaults to `False` unless overridden in the `StackQL` object constructor (read only)
	:type auth: bool
	:param server_pid: Process ID for stackql server process (read only - only when in server mode)
	:type auth: int	
	"""

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

		# start server in the background if server_mode is True
		self.server_mode = kwargs.get("server_mode", False)
		self.server_process = None
		if self.server_mode:
			self.server_process = subprocess.Popen([self.bin_path, "srv", "--pgsrv.port", "5444"])
			self.server_pid = self.server_process.pid
	    
	def stop(self):
		"""Stop the StackQL server process.

		"""
		if self.server_mode and self.server_process is not None:
			self.server_process.kill()
			self.server_process = None
			self.server_pid = None

	def show_properties(self):
		"""Prints the properties of the StackQL instance in JSON format.

		"""
		props = {}
		for var in vars(self):
			if var == "server_process":
				continue
			props[var] = getattr(self, var)
		print(json.dumps(props, indent=4, sort_keys=True))

	def upgrade(self, showprogress=True):
		"""Upgrades the StackQL instance to the latest version.
		
		"""
		_setup(self.download_dir, self.platform, showprogress)
		self.version, self.sha = _get_version(self.bin_path)
		print("stackql upgraded to version %s" % (self.version))

	def executeStmt(self, query):
		"""Executes a query using the StackQL instance and returns the output as a string.  
			This is intended for operations which do not return a result set, for example a mutation 
			operation such as an `INSERT` or a `DELETE` or life cycle method such as an `EXEC` operation.

		:param query: the StackQL query to execute
		:type query: str, required
		:return: the output of the statement (`stderr` or `stdout`)
		:rtype: str
		"""
		local_params = self.params
		local_params.insert(1, query)
		try:
			iqlPopen = subprocess.Popen([self.bin_path] + local_params,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			output = iqlPopen.stdout.read()
			iqlPopen.terminate()
		except FileNotFoundError as e:
			return("ERROR %s not found" % (self.bin_path))
		except:
			e = sys.exc_info()[0]
			return("ERROR %s %s" % (str(e), e.__doc__))
		return(str(output, 'utf-8'))

	def execute(self, query):
		"""Executes a query using the StackQL instance and returns the output as a string 
			or JSON object depending on the value of `parse_json` property.

		:param query: the StackQL query to execute
		:type query: str, required
		:return: the result set from the query
		:rtype: json or str
		"""
		local_params = self.params
		local_params.insert(1, query)
		try:
			iqlPopen = subprocess.Popen([self.bin_path] + local_params,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			output = iqlPopen.stdout.read()
			iqlPopen.terminate()
		except FileNotFoundError as e:
			return('[{"error": "%s not found"}]' % (self.bin_path))
		except:
			e = sys.exc_info()[0]
			return("ERROR %s %s" % (str(e), e.__doc__))
		if self.parse_json:
			# try to parse json
			try:
				json.loads(output)
			except ValueError as e:
				return('[{"error": "%s"}]' % (str(output.strip(), 'utf-8')))
		return(str(output, 'utf-8'))
	
	def executeQueriesAsync(self, queries):
		async def _execute_queries_async(queries_list):
			loop = asyncio.get_event_loop()

			# Use functools.partial to bind the necessary arguments
			func = functools.partial(_execute_queries_in_parallel, self, queries_list)

			with ProcessPoolExecutor() as executor:
				results = await loop.run_in_executor(executor, func)
			
			return results

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		all_results = loop.run_until_complete(_execute_queries_async(queries))
		loop.close()

		# Assuming results are JSON arrays, we can combine them:
		combined = []
		for res in all_results:
			combined.extend(json.loads(res))

		return combined