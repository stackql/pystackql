#!/usr/bin/env python3
"""
Test runner script for PyStackQL.

This script runs all the PyStackQL tests. It can be used to run
individual test files or all tests.

Examples:
    # Run all tests
    python run_tests.py

    # Run specific test files
    python run_tests.py tests/test_core.py tests/test_query_execution.py

    # Run with verbose output
    python run_tests.py -v
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
    print(colored("\n===== PyStackQL Test Runner =====\n", "cyan"))
    
    # Default pytest arguments
    args = ["-v"]
    
    # Add any specific test files passed as arguments
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    else:
        # If no specific tests were requested, run all non-server test files
        args.extend([
            "tests/test_core.py",
            "tests/test_query_execution.py",
            "tests/test_output_formats.py",
            "tests/test_magic.py",
            "tests/test_async.py"
        ])
        
        # Skip server tests by default as they require a running server
        # Uncomment to run server tests
        # args.append("tests/test_server.py")
        # args.append("tests/test_server_magic.py")
    
    # Run pytest with the arguments
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())