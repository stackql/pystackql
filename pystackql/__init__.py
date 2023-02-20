import sys, subprocess, platform, json, site, os, requests, zipfile

def get_platform():
	return platform.system()

def get_download_dir():
	return site.getuserbase()

def get_binary_name(platform):
	if platform == 'Windows':
		return r'stackql.exe'
	else:
		return r'stackql'

def get_url(platform):
	if platform == 'Linux':
		return 'https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip'
	elif platform == 'Windows':
		return 'https://releases.stackql.io/stackql/latest/stackql_windows_amd64.zip'
	elif platform == 'Darwin':
		return 'https://storage.googleapis.com/stackql-public-releases/latest/stackql_darwin_multiarch.pkg'
	else:
		raise Exception("ERROR: [get_url] unsupported OS type: %s" % (platform))

def download_file(url, path):
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
				print(f'\r[{progress_bar.ljust(20)}] {int(downloaded_size / total_size_in_bytes * 100)}%', end='')

		print("\nDownload complete.")
	except Exception as e:
		error_message = e.args[0]
		print("ERROR: [download_file] %s" % (error_message))
		exit()

def setup():
	print('installing stackql...')
	try:
		download_dir = get_download_dir()
		platform = get_platform()
		binary_name = get_binary_name(platform)
		url = get_url(platform)
		print("downloading latest version of stackql from %s to %s" % (url, download_dir))
		archive_file_name = os.path.join(download_dir, os.path.basename(url))
		download_file(url, archive_file_name)
		if platform == 'Darwin':
			os.system('sudo installer -pkg {} -target /'.format(archive_file_name))
		else:
			with zipfile.ZipFile(archive_file_name, 'r') as zip_ref:
				zip_ref.extractall(download_dir) 
		os.chmod(os.path.join(download_dir, binary_name), 0o755)
	except Exception as e:
		error_message = e.args[0]
		print("ERROR: [setup] %s" % (error_message))
		exit()

def get_version(bin_path):
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
		print("ERROR: [get_version] %s not found" % (bin_path))
		exit()
	except Exception as e:
		error_message = e.args[0]
		print("ERROR: [get_version] %s" % (error_message))		
		exit()

class StackQL:
	"""
	A class representing an instance of the StackQL query engine.

	Methods:
	- show_properties: prints the properties of the StackQL instance in JSON format
	- upgrade: upgrades the StackQL instance to the latest version
	- executeStmt: executes a query using the StackQL instance and returns the output as a string
	- execute: executes a query using the StackQL instance and returns the output as a string or JSON object depending on the value of parse_json property.

	Properties:
	- platform: the operating system platform (read only)
	- parse_json: whether to parse the output as JSON (read only)
	- params: a list of command-line parameters to pass to the StackQL executable, populated by the class constructor (read only)
	- bin_path: the file path of the StackQL executable (read only)
	- version: the version number of the StackQL executable (read only)
	- sha: the SHA-256 hash of the StackQL executable (read only)
	"""

	def __init__(self, **kwargs):
		"""
		Initializes a new instance of the StackQL class.

		Parameters:
		- **kwargs: a dictionary of keyword arguments representing command-line parameters to pass to the StackQL executable
		"""
		# get platform and set property
		self.platform = get_platform()

		# get each kwarg and set property
		self.parse_json = True
		self.params = ["exec"]
		output_set = False
		for key, value in kwargs.items():
			self.params.append("--%s" % key)
			self.params.append(value)
			if key == "output":
				output_set = True
				if value != "json":
					self.parse_json = False
		if not output_set:
			self.params.append("--output")
			self.params.append("json")

		# set fq path
		binary = get_binary_name(self.platform)
		download_dir = get_download_dir()
		self.bin_path = os.path.join(download_dir, binary)

		# get and set version
		if os.path.exists(self.bin_path):
			self.version, self.sha = get_version(self.bin_path)
		else:
			setup()
			self.version, self.sha = get_version(self.bin_path)

	def show_properties(self):
		"""
		Prints the properties of the StackQL instance in JSON format.
		"""
		props = {}
		for var in vars(self):
			props[var] = getattr(self, var)
		print(json.dumps(props, indent=4, sort_keys=True))

	def upgrade(self):
		"""
		Upgrades the StackQL instance to the latest version.
		"""
		setup()
		self.version, self.sha = get_version(self.bin_path)
		print("stackql upgraded to version %s" % (self.version))

	def executeStmt(self, query):
		"""
		Executes a query using the StackQL instance and returns the output as a string.  This is intended for operations which do not return a result set, for example mutation or life cycle methods.

		Parameters:
		- query: the StackQL query to execute

		Returns:
		- output: the output of the query as a string
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
		"""
		Executes a query using the StackQL instance and returns the output as a string or JSON object depending on the value of parse_json property.

		Parameters:
		- query: the StackQL query to execute

		Returns:
		- output: the output of the query as a string or JSON object
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