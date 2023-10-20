import subprocess, platform, json, site, os, requests, zipfile

# Conditional import for package metadata retrieval
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # This is for Python versions earlier than 3.8
    from importlib_metadata import version, PackageNotFoundError

def _is_binary_local(platform):
	"""Checks if the binary exists at the specified local path."""
	if platform == 'Linux' and os.path.exists('/usr/local/bin/stackql'):
		return True
	return False

def _get_package_version(package_name):
    try:
        pkg_version = version(package_name)
        if pkg_version is None:
            print(f"Warning: Retrieved version for '{package_name}' is None!")
        return pkg_version
    except PackageNotFoundError:
        print(f"Warning: Package '{package_name}' not found!")
        return None

def _get_platform():
	system_val = platform.system()
	machine_val = platform.machine()
	platform_val = platform.platform()
	python_version_val = platform.python_version()
	return "%s %s (%s), Python %s" % (system_val, machine_val, platform_val, python_version_val), system_val

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

def _get_url():
    system_val = platform.system()
    machine_val = platform.machine()

    if system_val == 'Linux' and machine_val == 'x86_64':
        return 'https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip'
    elif system_val == 'Windows':
        return 'https://releases.stackql.io/stackql/latest/stackql_windows_amd64.zip'
    elif system_val == 'Darwin':
        return 'https://storage.googleapis.com/stackql-public-releases/latest/stackql_darwin_multiarch.pkg'
    else:
        raise Exception(f"ERROR: [_get_url] unsupported OS type: {system_val} {machine_val}")

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
		url = _get_url()
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
        # Use communicate to fetch the outputs and wait for the process to finish
        output, _ = iqlPopen.communicate()
        # Decode the output
        decoded_output = output.decode('utf-8')
        # Split to get the version tokens
        version_tokens = decoded_output.split('\n')[0].split(' ')
        version = version_tokens[1]
        sha = version_tokens[3].replace('(', '').replace(')', '')
        return version, sha
    except FileNotFoundError:
        print("ERROR: [_get_version] %s not found" % (bin_path))
        exit(1)
    except Exception as e:
        error_message = e.args[0]
        print("ERROR: [_get_version] %s" % (error_message))        
        exit(1)
    finally:
        # Ensure the subprocess is terminated and streams are closed
        iqlPopen.terminate()
        iqlPopen.stdout.close()

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
