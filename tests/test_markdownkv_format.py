# tests/test_markdownkv_format.py

"""
Tests for Markdown-KV output format.

This format is optimized for LLM understanding based on research showing
it achieves 60.7% accuracy vs 44.3% for CSV when LLMs process tabular data.

Reference: https://www.empiricalagents.com/blog/which-table-format-do-llms-understand-best
"""

import os
import sys
import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystackql.core.output import OutputFormatter


class TestMarkdownKVFormat:
    """Tests for Markdown-KV output formatting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = OutputFormatter(output_format='markdownkv')

    def test_format_initialization(self):
        """Test that markdownkv is accepted as a valid output format."""
        assert self.formatter.output_format == 'markdownkv'

    def test_invalid_format_rejected(self):
        """Test that invalid formats are rejected."""
        with pytest.raises(ValueError) as exc_info:
            OutputFormatter(output_format='invalid')
        assert "Invalid output format" in str(exc_info.value)

    def test_format_simple_data(self):
        """Test formatting simple data as Markdown-KV."""
        import json

        data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25}
        ]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        # Check structure
        assert isinstance(result, str)
        assert "# Query Results" in result
        assert "## Record 1" in result
        assert "## Record 2" in result
        assert "id: 1" in result
        assert "name: Alice" in result
        assert "age: 30" in result
        assert "id: 2" in result
        assert "name: Bob" in result

    def test_format_with_null_values(self):
        """Test formatting data with null values."""
        import json

        data = [
            {"id": 1, "name": "Alice", "city": None}
        ]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        assert "city: null" in result

    def test_format_empty_data(self):
        """Test formatting empty data."""
        result = self.formatter._format_empty()

        assert isinstance(result, str)
        assert "# Query Results" in result
        assert "No records found" in result

    def test_format_error(self):
        """Test formatting error messages."""
        error_msg = "http response status code: 404"

        result = self.formatter._format_markdownkv_error(error_msg)

        assert isinstance(result, str)
        assert "# Query Results" in result
        assert "## Error" in result
        assert "error: http response status code: 404" in result

    def test_format_statement_result(self):
        """Test formatting statement results."""
        result = {
            "error": "okta provider, version 'v0.5.0' successfully installed"
        }

        formatted = self.formatter.format_statement_result(result)

        assert isinstance(formatted, str)
        assert "# Statement Result" in formatted
        assert "message: okta provider" in formatted

    def test_format_with_code_blocks(self):
        """Test that code blocks are properly formatted."""
        import json

        data = [{"id": 1, "name": "Test"}]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        # Count code block markers
        assert result.count("```") >= 2  # At least opening and closing

    def test_llm_friendly_structure(self):
        """Test that the output follows LLM-friendly Markdown-KV structure."""
        import json

        data = [
            {"employee_id": 1, "department": "Engineering", "salary": 100000}
        ]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        # Verify hierarchical structure
        lines = result.split('\n')

        # Should have main header
        assert any('# Query Results' in line for line in lines)

        # Should have record header
        assert any('## Record' in line for line in lines)

        # Should have code block with key: value pairs
        assert 'employee_id: 1' in result
        assert 'department: Engineering' in result
        assert 'salary: 100000' in result

    def test_multiple_records_formatting(self):
        """Test formatting multiple records maintains structure."""
        import json

        data = [
            {"id": i, "value": f"test{i}"}
            for i in range(1, 6)
        ]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        # Should have 5 record sections
        for i in range(1, 6):
            assert f"## Record {i}" in result
            assert f"id: {i}" in result
            assert f"value: test{i}" in result

    def test_complex_data_types(self):
        """Test handling of various data types."""
        import json

        data = [{
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "empty_string": ""
        }]
        json_data = json.dumps(data)

        result = self.formatter._format_data(json_data)

        assert "string: test" in result
        assert "number: 42" in result
        assert "float: 3.14" in result
        assert "boolean: True" in result or "boolean: true" in result.lower()
        assert "null: null" in result
        assert "empty_string:" in result

    def test_error_detection_integration(self):
        """Test that error detection works with markdownkv format."""
        # HTTP error should be detected
        error_data = "http response status code: 404, response body: Not Found"

        result = self.formatter._format_data(error_data)

        assert "# Query Results" in result
        assert "## Error" in result
        assert "404" in result


class TestMarkdownKVServerModeCompatibility:
    """Tests for markdownkv in server mode scenarios."""

    def test_server_mode_formatting(self):
        """Test that markdownkv can format server mode results."""
        formatter = OutputFormatter(output_format='markdownkv')

        # Simulate server mode result (list of dicts from database)
        data = [
            {"formula_name": "python", "version": "3.9.0", "license": "Python-2.0"}
        ]

        result = formatter._format_markdownkv(data)

        assert "# Query Results" in result
        assert "formula_name: python" in result
        assert "version: 3.9.0" in result


if __name__ == "__main__":
    pytest.main(["-v", __file__])
