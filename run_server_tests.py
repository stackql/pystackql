#!/usr/bin/env python3
"""
Test runner script for PyStackQL.

This script runs all the PyStackQL tests in server mode. It can be used to run
individual test files or all tests.

A running instance of the stackql server is required to run the server tests.

Examples:
    # Run all tests
    python run_server_tests.py

    # Run specific test files
    python run_server_tests.py tests/test_server.py

    # Run with verbose output
    python run_server_tests.py -v
"""

import sys
import os
import pytest
from termcolor import colored

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Add the tests directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests')))

def main():
    """Run the tests."""
    print(colored("\n===== PyStackQL Server Test Runner =====\n", "cyan"))
    
    # Default pytest arguments
    args = ["-v"]
    
    # Add any specific test files passed as arguments
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    else:
        # If no specific tests were requested, run all non-server test files
        args.extend([
            "tests/test_server.py",
            "tests/test_server_magic.py"
        ])
    
    # Run pytest with the arguments
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main())