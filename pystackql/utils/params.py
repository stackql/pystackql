# pystackql/utils/params.py

"""
Parameter generation utility for StackQL local mode.

This module provides functions to generate command-line parameters for the StackQL binary
and helps set instance attributes.
"""

import json
from .auth import format_auth

def _set_param(params, param_name, value):
    """Add a parameter and its value to the params list.
    
    :param params: List of parameters to append to
    :param param_name: Parameter name to add
    :param value: Value to add
    :return: Updated params list
    """
    params.append(f"--{param_name}")
    params.append(str(value))
    return params

def generate_params_for_execution(base_kwargs, override_kwargs=None):
    """Generate parameters for a single execution with optional overrides.
    
    This function generates command-line parameters for executing a query,
    optionally overriding base parameters with execution-specific ones.
    
    :param base_kwargs: Base keyword arguments (from constructor)
    :param override_kwargs: Keyword arguments to override (from execute/executeStmt)
    :return: List of parameters for StackQL binary
    """
    # Merge kwargs, with override_kwargs taking precedence
    merged_kwargs = base_kwargs.copy()
    if override_kwargs:
        merged_kwargs.update(override_kwargs)
    
    # Initialize parameter list
    params = ["exec"]
    
    # Extract parameters from merged_kwargs
    output = merged_kwargs.get('output', 'dict')
    backend_storage_mode = merged_kwargs.get('backend_storage_mode', 'memory')
    backend_file_storage_location = merged_kwargs.get('backend_file_storage_location', 'stackql.db')
    app_root = merged_kwargs.get('app_root', None)
    execution_concurrency_limit = merged_kwargs.get('execution_concurrency_limit', -1)
    dataflow_dependency_max = merged_kwargs.get('dataflow_dependency_max', 50)
    dataflow_components_max = merged_kwargs.get('dataflow_components_max', 50)
    custom_registry = merged_kwargs.get('custom_registry', None)
    custom_auth = merged_kwargs.get('custom_auth', None)
    sep = merged_kwargs.get('sep', ',')
    header = merged_kwargs.get('header', False)
    max_results = merged_kwargs.get('max_results', -1)
    page_limit = merged_kwargs.get('page_limit', 20)
    max_depth = merged_kwargs.get('max_depth', 5)
    api_timeout = merged_kwargs.get('api_timeout', 45)
    http_debug = merged_kwargs.get('http_debug', False)
    proxy_host = merged_kwargs.get('proxy_host', None)
    proxy_port = merged_kwargs.get('proxy_port', -1)
    proxy_user = merged_kwargs.get('proxy_user', None)
    proxy_password = merged_kwargs.get('proxy_password', None)
    proxy_scheme = merged_kwargs.get('proxy_scheme', 'http')
    
    # Set output format
    params.append("--output")
    if output.lower() == "csv":
        params.append("csv")
    else:
        params.append("json")
    
    # Backend storage settings
    if backend_storage_mode == 'file':
        params.append("--sqlBackend")
        params.append(json.dumps({ "dsn": f"file:{backend_file_storage_location}" }))
    
    # If app_root is set, use it
    if app_root is not None:
        _set_param(params, 'approot', app_root)

    # Set execution parameters
    _set_param(params, 'execution.concurrency.limit', execution_concurrency_limit)
    _set_param(params, 'dataflow.dependency.max', dataflow_dependency_max)
    _set_param(params, 'dataflow.components.max', dataflow_components_max)

    # If custom_auth is set, use it
    if custom_auth is not None:
        authobj, authstr = format_auth(custom_auth)
        params.append("--auth")
        params.append(authstr)
    
    # If custom_registry is set, use it
    if custom_registry is not None:
        params.append("--registry")
        params.append(json.dumps({ "url": custom_registry }))
    
    # CSV output settings
    if output.lower() == "csv":
        _set_param(params, 'delimiter', sep)
        
        if not header:
            params.append("--hideheaders")
   
    # App behavioral properties
    _set_param(params, 'http.response.maxResults', max_results)
    _set_param(params, 'http.response.pageLimit', page_limit)
    _set_param(params, 'indirect.depth.max', max_depth)
    _set_param(params, 'apirequesttimeout', api_timeout)

    if http_debug:
        params.append("--http.log.enabled")
    
    # Proxy settings
    if proxy_host is not None:
        # Set basic proxy parameters
        _set_param(params, 'http.proxy.host', proxy_host)
        _set_param(params, 'http.proxy.port', proxy_port)
        _set_param(params, 'http.proxy.user', proxy_user)
        _set_param(params, 'http.proxy.password', proxy_password)
        
        # Validate and set proxy scheme
        ALLOWED_PROXY_SCHEMES = {'http', 'https'}
        if proxy_scheme.lower() not in ALLOWED_PROXY_SCHEMES:
            raise ValueError(f"Invalid proxy_scheme. Expected one of {ALLOWED_PROXY_SCHEMES}, got {proxy_scheme}.")
        
        _set_param(params, 'http.proxy.scheme', proxy_scheme.lower())
    
    # Return the params list
    return params

def setup_local_mode(instance, **kwargs):
    """Set up local mode for a StackQL instance.
    
    This function generates parameters and sets instance attributes
    for local mode operation.
    
    :param instance: The StackQL instance
    :param kwargs: Keyword arguments from the constructor
    :return: List of parameters for StackQL binary
    """
    # Store base kwargs for later use
    instance._base_kwargs = kwargs.copy()
    
    # Initialize parameter list
    params = ["exec"]
    
    # Extract parameters from kwargs with defaults matching the StackQL.__init__ defaults
    output = kwargs.get('output', 'dict')
    backend_storage_mode = kwargs.get('backend_storage_mode', 'memory')
    backend_file_storage_location = kwargs.get('backend_file_storage_location', 'stackql.db')
    app_root = kwargs.get('app_root', None)
    execution_concurrency_limit = kwargs.get('execution_concurrency_limit', -1)
    dataflow_dependency_max = kwargs.get('dataflow_dependency_max', 50)
    dataflow_components_max = kwargs.get('dataflow_components_max', 50)
    custom_registry = kwargs.get('custom_registry', None)
    custom_auth = kwargs.get('custom_auth', None)
    sep = kwargs.get('sep', ',')
    header = kwargs.get('header', False)
    max_results = kwargs.get('max_results', -1)
    page_limit = kwargs.get('page_limit', 20)
    max_depth = kwargs.get('max_depth', 5)
    api_timeout = kwargs.get('api_timeout', 45)
    http_debug = kwargs.get('http_debug', False)
    proxy_host = kwargs.get('proxy_host', None)
    proxy_port = kwargs.get('proxy_port', -1)
    proxy_user = kwargs.get('proxy_user', None)
    proxy_password = kwargs.get('proxy_password', None)
    proxy_scheme = kwargs.get('proxy_scheme', 'http')
    download_dir = kwargs.get('download_dir', None)
    debug = kwargs.get('debug', False)
    debug_log_file = kwargs.get('debug_log_file', None)
    
    # Set output format
    params.append("--output")
    if output.lower() == "csv":
        params.append("csv")
    else:
        params.append("json")
    
    # Backend storage settings
    if backend_storage_mode == 'file':
        params.append("--sqlBackend")
        params.append(json.dumps({ "dsn": f"file:{backend_file_storage_location}" }))
    
    # If app_root is set, use it
    if app_root is not None:
        instance.app_root = app_root
        _set_param(params, 'approot', app_root)

    # Set execution parameters
    instance.execution_concurrency_limit = execution_concurrency_limit
    _set_param(params, 'execution.concurrency.limit', execution_concurrency_limit)
    
    instance.dataflow_dependency_max = dataflow_dependency_max
    _set_param(params, 'dataflow.dependency.max', dataflow_dependency_max)
    
    instance.dataflow_components_max = dataflow_components_max
    _set_param(params, 'dataflow.components.max', dataflow_components_max)

    # If custom_auth is set, use it
    if custom_auth is not None:
        authobj, authstr = format_auth(custom_auth)
        instance.auth = authobj
        params.append("--auth")
        params.append(authstr)
    
    # If custom_registry is set, use it
    if custom_registry is not None:
        instance.custom_registry = custom_registry
        params.append("--registry")
        params.append(json.dumps({ "url": custom_registry }))
    
    # CSV output settings
    if output.lower() == "csv":
        instance.sep = sep
        _set_param(params, 'delimiter', sep)
        
        instance.header = header
        if not header:
            params.append("--hideheaders")
   
    # App behavioral properties
    instance.max_results = max_results
    _set_param(params, 'http.response.maxResults', max_results)
    
    instance.page_limit = page_limit
    _set_param(params, 'http.response.pageLimit', page_limit)
    
    instance.max_depth = max_depth
    _set_param(params, 'indirect.depth.max', max_depth)
    
    instance.api_timeout = api_timeout
    _set_param(params, 'apirequesttimeout', api_timeout)

    instance.http_debug = bool(http_debug)
    if http_debug:
        params.append("--http.log.enabled")
    
    # Proxy settings
    if proxy_host is not None:
        # Set attributes
        instance.proxy_host = proxy_host
        instance.proxy_port = proxy_port
        instance.proxy_user = proxy_user
        instance.proxy_password = proxy_password
        
        # Set basic proxy parameters
        _set_param(params, 'http.proxy.host', proxy_host)
        _set_param(params, 'http.proxy.port', proxy_port)
        _set_param(params, 'http.proxy.user', proxy_user)
        _set_param(params, 'http.proxy.password', proxy_password)
        
        # Validate and set proxy scheme
        ALLOWED_PROXY_SCHEMES = {'http', 'https'}
        if proxy_scheme.lower() not in ALLOWED_PROXY_SCHEMES:
            raise ValueError(f"Invalid proxy_scheme. Expected one of {ALLOWED_PROXY_SCHEMES}, got {proxy_scheme}.")
        
        instance.proxy_scheme = proxy_scheme.lower()
        _set_param(params, 'http.proxy.scheme', proxy_scheme.lower())
    
    # Initialize binary manager
    from ..core.binary import BinaryManager  # Import here to avoid circular imports
    instance.binary_manager = BinaryManager(download_dir)
    instance.bin_path = instance.binary_manager.bin_path
    instance.version = instance.binary_manager.version
    instance.sha = instance.binary_manager.sha
    
    # Return the params list
    return params