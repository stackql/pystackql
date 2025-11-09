# pystackql/core/error_detector.py

"""
Error detection module for PyStackQL.

This module provides centralized error detection logic that checks messages
against predefined error patterns loaded from errors.yaml.
"""

import os
import re
import yaml


class ErrorDetector:
    """Detects errors in query results based on predefined patterns.

    This class loads error patterns from errors.yaml and provides methods
    to check if a message contains any of these error patterns.
    """

    def __init__(self):
        """Initialize the ErrorDetector by loading error patterns from errors.yaml."""
        self.fuzzy_patterns = []
        self.exact_patterns = []
        self.regex_patterns = []  # List of compiled regex pattern objects
        self._load_error_patterns()

    def _load_error_patterns(self):
        """Load error patterns from the errors.yaml file.

        The errors.yaml file should be located in the same directory as this module.
        """
        # Get the directory containing the pystackql package
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(current_dir)
        errors_file = os.path.join(package_dir, 'errors.yaml')

        try:
            if os.path.exists(errors_file):
                with open(errors_file, 'r') as f:
                    error_config = yaml.safe_load(f)

                if error_config and 'errors' in error_config:
                    errors = error_config['errors']

                    # Load fuzzy match patterns (case-insensitive substring matching)
                    if 'fuzzy_matches' in errors:
                        self.fuzzy_patterns = [
                            pattern.lower()
                            for pattern in errors['fuzzy_matches']
                            if pattern
                        ]

                    # Load exact match patterns (case-sensitive exact/prefix matching)
                    if 'exact_matches' in errors:
                        self.exact_patterns = [
                            pattern
                            for pattern in errors['exact_matches']
                            if pattern
                        ]

                    # Load regex patterns (compile them for efficiency)
                    if 'regex_matches' in errors:
                        self.regex_patterns = []
                        for pattern in errors['regex_matches']:
                            if pattern:
                                try:
                                    # Compile with IGNORECASE flag for case-insensitive matching
                                    compiled = re.compile(pattern, re.IGNORECASE)
                                    self.regex_patterns.append((pattern, compiled))
                                except re.error as regex_err:
                                    print(f"Warning: Invalid regex pattern '{pattern}': {regex_err}")
        except Exception as e:
            # If we can't load the error patterns, continue with empty lists
            # This ensures the module doesn't break existing functionality
            print(f"Warning: Could not load error patterns from {errors_file}: {e}")

    def is_error(self, message):
        """Check if a message contains any error patterns.

        Args:
            message (str): The message to check for error patterns

        Returns:
            bool: True if the message matches any error pattern, False otherwise
        """
        if not message or not isinstance(message, str):
            return False

        message_lower = message.lower()

        # Check fuzzy matches (case-insensitive substring matching)
        for pattern in self.fuzzy_patterns:
            if pattern in message_lower:
                return True

        # Check exact matches (exact string or starts with prefix)
        for pattern in self.exact_patterns:
            if message == pattern or message.startswith(pattern):
                return True

        # Check regex matches
        for pattern_str, compiled_pattern in self.regex_patterns:
            if compiled_pattern.search(message):
                return True

        return False

    def extract_error_info(self, message):
        """Extract error information from a message.

        Args:
            message (str): The error message

        Returns:
            dict: Dictionary containing error details with 'error' and 'detected_pattern' keys
        """
        if not self.is_error(message):
            return None

        message_lower = message.lower()
        detected_pattern = None
        pattern_type = None

        # Find which pattern was matched (check in order: fuzzy, exact, regex)
        for pattern in self.fuzzy_patterns:
            if pattern in message_lower:
                detected_pattern = pattern
                pattern_type = "fuzzy"
                break

        if not detected_pattern:
            for pattern in self.exact_patterns:
                if message == pattern or message.startswith(pattern):
                    detected_pattern = pattern
                    pattern_type = "exact"
                    break

        if not detected_pattern:
            for pattern_str, compiled_pattern in self.regex_patterns:
                if compiled_pattern.search(message):
                    detected_pattern = pattern_str
                    pattern_type = "regex"
                    break

        return {
            "error": message,
            "detected_pattern": detected_pattern,
            "pattern_type": pattern_type
        }
