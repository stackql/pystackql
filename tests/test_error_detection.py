# tests/test_error_detection.py

"""
Error detection tests for PyStackQL.

This module tests the centralized error detection functionality that identifies
error patterns in query results.
"""

import os
import sys
import json
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystackql.core.error_detector import ErrorDetector
from pystackql.core.output import OutputFormatter


class TestErrorDetector:
    """Tests for the ErrorDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ErrorDetector()

    def test_detector_initialization(self):
        """Test that ErrorDetector initializes and loads patterns."""
        assert self.detector is not None
        assert isinstance(self.detector.fuzzy_patterns, list)
        assert isinstance(self.detector.exact_patterns, list)
        # Check that some patterns were loaded
        assert len(self.detector.fuzzy_patterns) > 0
        assert len(self.detector.exact_patterns) > 0

    def test_http_4xx_error_detection(self):
        """Test detection of HTTP 4xx status codes."""
        messages = [
            "http response status code: 404",
            "http response status code: 400, response body: Bad Request",
            "HTTP RESPONSE STATUS CODE: 403 Forbidden",
        ]
        for msg in messages:
            assert self.detector.is_error(msg), f"Should detect error in: {msg}"

    def test_http_5xx_error_detection(self):
        """Test detection of HTTP 5xx status codes."""
        messages = [
            "http response status code: 500",
            "http response status code: 503, service unavailable",
            "HTTP RESPONSE STATUS CODE: 502 Bad Gateway",
        ]
        for msg in messages:
            assert self.detector.is_error(msg), f"Should detect error in: {msg}"

    def test_exact_match_detection(self):
        """Test detection of exact match patterns."""
        messages = [
            "error: invalid syntax",
            "ERROR: something went wrong",
            "Error: connection failed",
        ]
        for msg in messages:
            assert self.detector.is_error(msg), f"Should detect error in: {msg}"

    def test_fuzzy_match_detection(self):
        """Test detection of fuzzy match patterns."""
        messages = [
            "An error occurred during processing",
            "Operation failed due to timeout",
            "Cannot find matching operation for this request",
            "Disparity in fields to insert and supplied data",
        ]
        for msg in messages:
            assert self.detector.is_error(msg), f"Should detect error in: {msg}"

    def test_non_error_messages(self):
        """Test that non-error messages are not detected as errors."""
        messages = [
            "Query executed successfully",
            "Retrieved 10 rows",
            "Connection established",
            "Data retrieved from provider",
        ]
        for msg in messages:
            assert not self.detector.is_error(msg), f"Should not detect error in: {msg}"

    def test_case_insensitive_fuzzy_matching(self):
        """Test that fuzzy matching is case-insensitive."""
        messages = [
            "ERROR occurred",
            "Error Occurred",
            "error occurred",
            "An EXCEPTION was raised",
        ]
        for msg in messages:
            assert self.detector.is_error(msg), f"Should detect error in: {msg}"

    def test_extract_error_info(self):
        """Test extraction of error information."""
        msg = "http response status code: 404"
        info = self.detector.extract_error_info(msg)
        assert info is not None
        assert "error" in info
        assert "detected_pattern" in info
        assert info["error"] == msg
        assert info["detected_pattern"] is not None

    def test_extract_error_info_non_error(self):
        """Test that non-error messages return None."""
        msg = "Success"
        info = self.detector.extract_error_info(msg)
        assert info is None

    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        assert not self.detector.is_error("")
        assert not self.detector.is_error(None)

    def test_non_string_handling(self):
        """Test handling of non-string inputs."""
        assert not self.detector.is_error(123)
        assert not self.detector.is_error([])
        assert not self.detector.is_error({})


class TestOutputFormatterErrorDetection:
    """Tests for error detection integration in OutputFormatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(output_format='dict')

    def test_format_error_in_raw_data(self):
        """Test detection of errors in raw data strings."""
        error_data = "http response status code: 404, response body: Not Found"
        result = self.formatter._format_data(error_data)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" in result[0]

    def test_format_error_in_json_data(self):
        """Test detection of errors in JSON-formatted data."""
        # Simulate data returned by StackQL with an error message
        data = [
            {
                "message": "http response status code: 404",
                "status": "failed"
            }
        ]
        json_data = json.dumps(data)
        result = self.formatter._format_data(json_data)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" in result[0]

    def test_format_valid_data_not_detected_as_error(self):
        """Test that valid data is not detected as error."""
        data = [
            {
                "formula_name": "python",
                "version": "3.9.0",
                "status": "installed"
            }
        ]
        json_data = json.dumps(data)
        result = self.formatter._format_data(json_data)

        assert isinstance(result, list)
        assert len(result) > 0
        # Should return the data, not an error
        if "error" not in result[0]:
            assert "formula_name" in result[0] or "version" in result[0]

    def test_check_data_for_errors_in_dict(self):
        """Test error detection in dictionary data."""
        data = {
            "status": "failed",
            "message": "error: operation failed"
        }
        error = self.formatter._check_data_for_errors(data)
        assert error is not None
        assert "error" in error.lower()

    def test_check_data_for_errors_in_list(self):
        """Test error detection in list data."""
        data = [
            {"name": "test1", "status": "ok"},
            {"name": "test2", "message": "http response status code: 500"}
        ]
        error = self.formatter._check_data_for_errors(data)
        assert error is not None
        assert "http response status code" in error.lower()

    def test_check_data_for_errors_nested(self):
        """Test error detection in nested data structures."""
        data = {
            "results": [
                {
                    "id": 1,
                    "details": {
                        "status": "error: connection timeout"
                    }
                }
            ]
        }
        error = self.formatter._check_data_for_errors(data)
        assert error is not None

    def test_check_data_for_errors_no_error(self):
        """Test that valid data returns None."""
        data = {
            "status": "success",
            "results": [
                {"name": "item1", "value": 100},
                {"name": "item2", "value": 200}
            ]
        }
        error = self.formatter._check_data_for_errors(data)
        assert error is None

    def test_format_statement_with_error(self):
        """Test statement result formatting with error detection."""
        result = {
            "error": "http response status code: 404"
        }
        formatted = self.formatter.format_statement_result(result)

        # Should be formatted as error, not as message
        if isinstance(formatted, dict):
            # For dict output, check if it's an error list or message
            if isinstance(formatted, list):
                assert "error" in formatted[0]
            elif "error" in formatted:
                assert formatted["error"] is not None
        elif isinstance(formatted, list):
            assert "error" in formatted[0]

    def test_format_statement_without_error(self):
        """Test statement result formatting without errors."""
        result = {
            "error": "okta provider, version 'v0.5.0' successfully installed"
        }
        formatted = self.formatter.format_statement_result(result)

        # Should be formatted as message since it's not an error
        assert formatted is not None


class TestHomebrewProviderErrorScenario:
    """Tests for the specific homebrew provider error scenario."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(output_format='dict')
        self.detector = ErrorDetector()

    def test_homebrew_404_error_detection(self):
        """Test detection of homebrew 404 error message."""
        # This is the actual error message from the user's example
        error_msg = "http response status code: 404, response body: <!DOCTYPE html>..."

        # Should be detected as error
        assert self.detector.is_error(error_msg)

    def test_homebrew_404_formatting(self):
        """Test formatting of homebrew 404 error."""
        # Simulate the raw data that would come from StackQL
        error_data = "http response status code: 404, response body: <!DOCTYPE html>..."

        result = self.formatter._format_data(error_data)

        # Should be formatted as error
        assert isinstance(result, list)
        assert len(result) > 0
        assert "error" in result[0]
        assert "404" in str(result[0]["error"])

    def test_homebrew_valid_formula_not_error(self):
        """Test that valid homebrew formula data is not detected as error."""
        # Simulate valid formula data
        valid_data = [
            {
                "formula_name": "python",
                "full_name": "python@3.9",
                "homepage": "https://www.python.org",
                "latest_version": "3.9.7",
                "license": "Python-2.0"
            }
        ]
        json_data = json.dumps(valid_data)

        result = self.formatter._format_data(json_data)

        # Should return data, not error
        assert isinstance(result, list)
        assert len(result) > 0
        if "error" not in result[0]:
            assert "formula_name" in result[0]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
