import sys, subprocess, platform

class StackQL:
	def __init__(self, **kwargs):
		plat = platform.system()
		defaultbin = r'stackql'
		if plat == 'Windows':
			defaultbin = r'stackql.exe'
		# stackql binary
		self.exe = kwargs.get('exe')
		if self.exe is not None:
			self.exe = kwargs.get('exe')
		else:
			self.exe = defaultbin
		self.params = ['exec', '--output', 'json']			
		# authentication method
		self.auth = kwargs.get('auth')
		if self.auth is not None:
			self.params.append('--auth')
			self.params.append(self.auth)		
		# specify dbfilepath
		self.dbfilepath = kwargs.get('dbfilepath')
		if self.dbfilepath is not None:
			self.params.append('--dbfilepath')
			self.params.append(self.dbfilepath)
			
	def execute(self, query):
		local_params = self.params
		local_params.insert(1, query)
		try:
			iqlPopen = subprocess.Popen([self.exe] + local_params,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			output = iqlPopen.stdout.read()
			iqlPopen.terminate()
		except:
			e = sys.exc_info()[0]
			print("ERROR %s %s" % (str(e), e.__doc__))
			output = None
		return str(output, 'utf-8')
		
	def version(self):
		try:
			iqlPopen = subprocess.Popen([self.exe] + ["--version"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			output = iqlPopen.stdout.read()
			iqlPopen.terminate()
		except:
			e = sys.exc_info()[0]
			print("ERROR %s %s" % (str(e), e.__doc__))
			output = None
		return output		