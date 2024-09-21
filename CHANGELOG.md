# Changelog

## v3.6.5 (2024-09-19)

### Bug Fixes

- Fix(MacOS): Enhanced platform check for stackql installation
- Fix(Test Code): Removed loading of `test.env` in test execution script and Add mocking logic for `pystackql.StackQL`'s methods.

## v3.6.4 (2024-07-17)

### Updates

- added dataflow dependency arguments

## v3.6.3 (2024-06-22)

### Updates

- build updates

## v3.6.2 (2024-05-06)

### Updates

- added `rowsaffected` to dict response for `executeStmt`

## v3.6.1 (2024-04-18)

### Updates

- modified dict response for `executeStmt`
- modified error response for `execute`, should never return `None`

## v3.5.4 (2024-04-11)

### Updates

- added `suppress_errors` argument to the `execute` function

## v3.5.3 (2024-04-08)

### Updates

- added `backend_storage_mode` and `backend_file_storage_location` constructor args for specifying a file based backend (not applicable in `server_mode`)

## v3.5.2 (2024-03-21)

### Updates

- added `custom_registry` constructor arg for specifying a non-default registry

## v3.5.1 (2024-03-15)

### Updates

- included `pandas` and `IPython` install requirements
- optional required import of `psycopg2` only if in `server_mode`

## v3.2.5 (2023-12-07)

### Updates

- included `app_root` and `execution_concurrency_limit` options in `StackQL` constructor

## v3.2.4 (2023-10-24)

### Updates

- implemented non `server_mode` magic extension
- updated dataframe output for statements
- `pandas` type updates
- updated class parameters
- added additional tests
- bin path defaults for codespaces notebooks

## v3.0.0 (2023-10-11)

### Updates

- added `StackqlMagic` class for `jupyter`, `IPython` integration
- `server_mode` is now used to connect to a `stackql` server process using `pyscopg2`
- added additional tests

## v2.0.0 (2023-08-15)

### Updates

- added `executeQueriesAsync` stackql class method

## v1.5.0 (2023-04-04)

### Updates

- added `server_mode` to run a background stackql server process

## v1.0.2 (2023-02-23)

### Updates

- enabled custom `download_dir` argument

## v1.0.1 (2023-02-23)

### Minor updates

- updated `setup.py`

## v1.0.0 (2023-02-22)

### Refactor

- refactored package
- added support for `kwargs` for the `StackQL` constructor
- added `setup.py`
- added `docs` using `sphinx`
- added additional tests

## v0.9.0 (2022-06-06)

### Bug Fixes

- added exception handling

## v0.5.0 (2022-06-03)

### Bug Fixes

- added local registry support
- updated docs

## v0.4.1 (2022-05-31)

### Bug Fixes

- added `str` handling
- updated docs

## v0.4.0 (2022-02-08)

### Updates

- updated `version` output
- updated docs

## v0.3.0 (2022-02-07)

### Initial release as `pystackql`

- added `auth` switch
- converted `byte` output to `str`

## v0.2.0 (2021-07-19)

### Updates to `pyinfraql`

- added `version` method
- updates to accept `None` for arguments
- updated docs

## v0.1.1 (2021-07-16)

### Updates to `pyinfraql`

- added `dbfilepath` argument

## v0.1.0 (2021-02-15)

### Initial Release (as `pyinfraql`)

- class constructor for `pyinfraql`
- support for `google` provider
- support for integration with `pandas`, `matplotlib` and `jupyter`
