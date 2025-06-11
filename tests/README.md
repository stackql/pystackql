# PyStackQL Testing Guide

## Overview

This guide explains the PyStackQL testing framework. The tests have been designed to:

1. Focus on provider-agnostic queries where possible
2. Use the Homebrew provider for provider-specific tests (no authentication required)
3. Be organized into logical modules based on functionality
4. Support both local execution and GitHub Codespaces

## Test Structure

The tests are organized into these main files:

- `test_constants.py`: Common constants and helper functions
- `conftest.py`: Test fixtures and setup
- `test_core.py`: Core functionality tests
- `test_query_execution.py`: Query execution tests
- `test_output_formats.py`: Output format tests
- `test_magic.py`: Magic extension tests
- `test_async.py`: Async functionality tests
- `test_server.py`: Server mode tests

## Running Tests

### Running All Tests

To run all tests:

```bash
python run_tests.py
```

### Running Specific Tests

To run specific test files:

```bash
python run_tests.py tests/test_core.py tests/test_query_execution.py
```

### Running with Extra Verbosity

```bash
python run_tests.py -v
```

### Running Server Tests

Server tests are skipped by default because they require a running StackQL server. To run these tests:

1. Start a StackQL server:
   ```bash
   stackql srv --pgsrv.address 127.0.0.1 --pgsrv.port 5466
   ```

2. Run the server tests:
   ```bash
   python run_tests.py tests/test_server.py -v
   ```

## Test Categories

### Core Tests

Tests the basic properties and attributes of the `StackQL` class:

- `properties()` method
- `version`, `package_version`, `platform` attributes
- Binary path and download directory
- Upgrade functionality

### Query Execution Tests

Tests the query execution functionality with provider-agnostic queries:

- Literal values (integers, strings, floats)
- Expressions
- JSON extraction
- Homebrew provider queries
- Registry pull operations

### Output Format Tests

Tests the different output formats:

- Dict output
- Pandas output with type checking
- CSV output with different separators and headers
- Error handling for invalid configurations

### Magic Tests

Tests the Jupyter magic extensions:

- Line and cell magic in non-server mode
- Line and cell magic in server mode
- Result storage in user namespace
- Display options

### Async Tests

Tests the async query execution functionality:

- `executeQueriesAsync` with different output formats
- Concurrent queries with the Homebrew provider
- Error handling

### Server Tests

Tests the server mode functionality (requires a running server):

- Server connectivity
- Query execution in server mode
- Statement execution in server mode
- Different output formats in server mode

## Test Data

The tests use:

1. **Simple literals and expressions**:
   ```sql
   SELECT 1 as literal_int_value
   SELECT 1.001 as literal_float_value
   SELECT 'test' as literal_string_value
   SELECT 1=1 as expression
   ```

2. **Homebrew provider queries**:
   ```sql
   SELECT name, full_name, tap FROM homebrew.formula.formula WHERE formula_name = 'stackql'
   SELECT * FROM homebrew.formula.vw_usage_metrics WHERE formula_name = 'stackql'
   ```

3. **Registry operations**:
   ```sql
   REGISTRY PULL homebrew
   ```

## Testing in GitHub Codespaces

When running in GitHub Codespaces:

1. The tests automatically detect if they're running in GitHub Actions and skip the binary upgrade
2. The server tests are skipped by default (can be enabled if needed)
3. Async tests might be skipped on Windows due to asyncio issues

## Adding New Tests

When adding new tests:

1. Use provider-agnostic queries where possible
2. For provider-specific tests, prefer the Homebrew provider
3. Add new tests to the appropriate test file based on functionality
4. Update `run_tests.py` if adding a new test file
5. Follow the existing patterns for consistency