**Note**:

- All contributions to `pystackql`, through any means, are subject to the [license](/LICENSE).
- This document itself and the patterns specified herein, are heavily influenced by [redis](https://github.com/redis/redis). We profusely thank the maintainers of same, from which we draw inspiration.
- For useful information contributors **may** want to consider in developing `pystackql`, please see the "Building the package", "Testing Locally" and "Building the docs" sections of the [README](/README.rst), the [tests README](/tests/README.md), and the published documentation at [pystackql.readthedocs.io](https://pystackql.readthedocs.io).
- All contributions to `pystackql` and actions related, through any means, are subject to the StackQL [CODE OF CONDUCT](https://github.com/stackql/stackql/blob/main/CODE_OF_CONDUCT.md).

# Contribution flow

Before beginning implementation work, please raise an issue (using the bug report, feature request or question template as appropriate) and receive a consensus that work should proceed.

Please raise pull requests (PRs) from a fork of this repository. The richer the detail / evidence supplied, the easier the review process. A usefully named feature branch for the PR source is appreciated.

PRs against `main` run the test suite on Linux, macOS and Windows across Python 3.9 to 3.13. Please keep changes working on all of them.

## Development notes

- `pystackql` is a Python wrapper around the `stackql` engine. Changes to the engine itself belong in [stackql/stackql](https://github.com/stackql/stackql), and provider definitions belong in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry).
- Run the non-server tests with `python run_tests.py`. Server-mode tests need a running `stackql srv` process (see `start-stackql-server.sh` or `start-stackql-server.ps1`), then `python run_server_tests.py`.
- Tests use the no-auth Homebrew provider and provider-agnostic literal queries. Please do not add tests that require cloud credentials.
- Runtime dependencies are declared in `pyproject.toml` as minimum versions rather than pins. Please keep it that way and avoid unrelated dependency bumps.
- `README.rst` is reStructuredText and doubles as the PyPI readme. The documentation in `docs/` is built with Sphinx from the docstrings, so update the `StackQL.__init__` docstring when changing constructor parameters.
- Releases bump `version` in `pyproject.toml` and add an entry to `CHANGELOG.md`.

Finally, in respect of all your efforts; we thank you and ask that you please give us a star while you are at it.

Many Thanks,

The StackQL team.
