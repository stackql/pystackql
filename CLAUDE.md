# CLAUDE.md

PyStackQL - a Python wrapper for the [StackQL](https://stackql.io) query engine, which runs SQL against cloud and SaaS providers. Published to PyPI as `pystackql`.

## Layout

- `pystackql/core/` - main logic
  - `stackql.py` - `StackQL` class, the primary public interface (`execute`, `executeStmt`, `executeQueriesAsync`, `properties`, `upgrade`, `test_connection`)
  - `query.py` - `QueryExecutor` / `AsyncQueryExecutor`
  - `server.py` - `ServerConnection` (server mode via psycopg/postgres wire protocol)
  - `output.py` - `OutputFormatter` (output formats: `dict`, `pandas`, `csv`, `markdownkv`)
  - `binary.py` - `BinaryManager` (locates/downloads the stackql binary)
  - `error_detector.py` - `ErrorDetector`, matches messages against patterns in `pystackql/errors.yaml`
- `pystackql/utils/` - platform, binary, download, auth, and param helpers (re-exported from `utils/__init__.py`)
- `pystackql/magic_ext/` - Jupyter magics: `StackqlMagic` (local) and `StackqlServerMagic` (server), sharing `base.py`
- `pystackql/__init__.py` - public API: `StackQL`, `StackqlMagic`, `StackqlServerMagic`

## Two execution modes

- **Local mode** (default): downloads/runs the stackql binary as a subprocess.
- **Server mode** (`server_mode=True`): connects to a running stackql server over the postgres wire protocol. `csv` output and several local-only options are unsupported here.

## Testing

Tests use the no-auth Homebrew provider and provider-agnostic literal queries (avoid adding auth-requiring tests).

- Non-server tests: `python run_tests.py` (optionally pass specific `tests/test_*.py` files, `-v`)
- Server tests: start a server first (`stackql srv --pgsrv.address 127.0.0.1 --pgsrv.port 5466`), then `python run_server_tests.py`
- CI (`.github/workflows/test.yaml`) runs both across Linux/macOS/Windows and Python 3.9-3.13.

## Conventions

- Supports Python 3.9-3.13 on Windows, macOS, and Linux - keep changes cross-platform.
- `README.rst` is reStructuredText (the PyPI readme); docs in `docs/` build to ReadTheDocs from Sphinx-style docstrings. Update the `StackQL.__init__` docstring when changing constructor params.
- Bump `version` in `pyproject.toml` for releases; record changes in `CHANGELOG.md`.
