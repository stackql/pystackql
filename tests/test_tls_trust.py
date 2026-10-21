# tests/test_tls_trust.py

"""
TLS trust store tests for PyStackQL.

PyStackQL makes one outbound HTTPS call (downloading the stackql binary from
releases.stackql.io via `requests`), and `requests` validates server
certificates against the CA bundle shipped by `certifi`. These tests guard
against resolving a certifi bundle that still trusts a compromised root.

Background: in October 2026 the private keys of eight eMudhra intermediate CAs
chaining to "emSign ECC Root CA - G3" were found to be trivially recoverable
(Mozilla Bugzilla 2083449). certifi removed that root in 2026.10.18 and
restored the unaffected emSign roots in 2026.10.19 (GHSA-6q48-6c7w-9gw2).
"""

import hashlib
import os
import re
import ssl
import sys
from unittest.mock import patch, MagicMock

import certifi
import requests

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystackql.utils import download

# Minimum certifi release that distrusts the compromised root while keeping the
# unaffected emSign roots. Must match the floor declared in pyproject.toml.
MIN_CERTIFI_VERSION = (2026, 10, 19)

# SHA-256 fingerprint of "emSign ECC Root CA - G3", the root that signed the
# compromised eMudhra intermediates.
DISTRUSTED_ROOT_SHA256 = (
    "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b"
)

_PEM_BLOCK = re.compile(
    r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", re.S
)


def _bundle_fingerprints(path):
    """Return the set of SHA-256 fingerprints (hex) of every cert in a PEM bundle."""
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    fingerprints = set()
    for block in _PEM_BLOCK.findall(data):
        der = ssl.PEM_cert_to_DER_cert(block)
        fingerprints.add(hashlib.sha256(der).hexdigest())
    return fingerprints


class TestCertifiTrustStore:
    """The resolved certifi bundle must not trust the compromised root."""

    def test_certifi_meets_minimum_version(self):
        """certifi must be at least the first release that distrusts the root
        while retaining the unaffected emSign roots."""
        installed = tuple(int(p) for p in certifi.__version__.split("."))
        assert installed >= MIN_CERTIFI_VERSION, (
            f"certifi {certifi.__version__} is older than "
            f"{'.'.join(map(str, MIN_CERTIFI_VERSION))}; its CA bundle still "
            "trusts emSign ECC Root CA - G3"
        )

    def test_bundle_is_non_empty_and_parseable(self):
        """Sanity check so the fingerprint test cannot pass on an empty bundle."""
        fingerprints = _bundle_fingerprints(certifi.where())
        assert len(fingerprints) > 50

    def test_bundle_excludes_compromised_emsign_root(self):
        """emSign ECC Root CA - G3 must be absent from the bundle, checked by
        certificate fingerprint rather than by the human-readable label."""
        fingerprints = _bundle_fingerprints(certifi.where())
        assert DISTRUSTED_ROOT_SHA256 not in fingerprints, (
            "certifi bundle still contains emSign ECC Root CA - G3 "
            f"({certifi.where()})"
        )


class TestRequestsUsesCertifi:
    """The HTTPS client used for downloads must validate against certifi."""

    def test_requests_default_ca_bundle_is_certifi(self):
        """requests must resolve its default CA bundle from certifi, so the
        certifi floor is what governs the download's trust store."""
        assert os.path.realpath(requests.certs.where()) == \
            os.path.realpath(certifi.where())

    def test_download_file_does_not_disable_verification(self, tmp_path):
        """download_file must never opt out of certificate verification."""
        fake_response = MagicMock()
        fake_response.headers = {'content-length': '4'}
        fake_response.iter_content.return_value = [b'data']
        fake_response.raise_for_status.return_value = None

        dest = os.path.join(str(tmp_path), 'out.bin')
        with patch('pystackql.utils.download.requests.get',
                   return_value=fake_response) as mock_get:
            download.download_file(
                'https://releases.stackql.io/stackql/latest/x.zip',
                dest, showprogress=False)

        assert mock_get.called
        assert mock_get.call_args.kwargs.get('verify', True) is not False
