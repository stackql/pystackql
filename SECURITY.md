# Security Policy

The StackQL team takes the security of `pystackql` seriously. We appreciate everyone who reports vulnerabilities responsibly, and we will do our best to acknowledge and address valid reports promptly.

## Reporting a Vulnerability

Please do not open a public GitHub issue for security reports. A public issue discloses the problem before a fix is available and puts users at risk.

Instead, report privately using GitHub private vulnerability reporting:

1. Open the [new advisory form](https://github.com/stackql/pystackql/security/advisories/new) (Security tab -> Advisories -> "Report a vulnerability").
2. Provide as much detail as you can: affected `pystackql` version(s), Python version and operating system, reproduction steps, impact, and any suggested remediation.
3. Submit. This opens a private advisory thread visible only to you and the maintainers.

If you cannot use GitHub private vulnerability reporting, email us at [info@stackql.io](mailto:info@stackql.io). Please put "SECURITY" in the subject line and treat the contents as confidential.

## Supported Versions

Security fixes are applied to the latest released minor line, published to [PyPI](https://pypi.org/project/pystackql/). Older lines are supported on a best-effort basis only; we recommend upgrading to the latest release with `pip install --upgrade pystackql`. See the [changelog](/CHANGELOG.md) and the [PyPI release history](https://pypi.org/project/pystackql/#history) for the current version.

| Version | Supported    |
| ------- | ------------ |
| 3.8.x   | Yes          |
| < 3.8   | Best-effort  |

`pystackql` supports Python 3.9 to 3.13 on Linux, macOS and Windows.

## Response Expectations

These are targets, not contractual guarantees:

- We aim to acknowledge a report within a few business days.
- We will keep you updated as we investigate and work on a fix.
- We will coordinate disclosure timing with you once a fix or mitigation is ready.

## Disclosure Policy

We follow coordinated (responsible) disclosure. Please give us a reasonable opportunity to release a fix before any public disclosure. We are happy to credit reporters in the advisory and release notes, unless you prefer to remain anonymous.

## Scope

This policy covers the `pystackql` Python package in this repository as published to PyPI, including its Jupyter magic extensions. `pystackql` downloads and runs the `stackql` engine binary in local mode and connects to a `stackql` server in server mode; the engine, its binaries and its Docker images are maintained in [stackql/stackql](https://github.com/stackql/stackql) and covered by that repository's [security policy](https://github.com/stackql/stackql/blob/main/SECURITY.md). Provider definitions are maintained separately in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry). Please report issues specific to those in their respective repositories.
