# pystackql/utils/auth.py

"""
Authentication utility functions for PyStackQL.

This module contains functions for handling authentication.
"""

import json

def format_auth(auth):
    """Formats an authentication object for use with stackql.
    
    Args:
        auth: The authentication object, can be a string or a dict
        
    Returns:
        tuple: (auth_obj, auth_str)
            - auth_obj: The authentication object as a dict
            - auth_str: The authentication object as a JSON string
            
    Raises:
        Exception: If the authentication object is invalid
    """
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
            raise Exception("ERROR: [format_auth] auth key supplied with no value")
    except Exception as e:
        error_message = e.args[0]
        print(f"ERROR: [format_auth] {error_message}")
        exit(1)