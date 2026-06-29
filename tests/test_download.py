# tests/test_download.py

"""
Download utility tests for PyStackQL.

These tests verify that all stackql binary downloads are routed through the
releases.stackql.io proxy and that requests carry the distinguishable
`pystackql/{version}` User-Agent. See issue #64.
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add the parent directory to the path so we can import from pystackql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pystackql.utils import download


class TestDownloadUrl:
    """Tests for get_download_url across platforms."""

    @pytest.mark.parametrize("system,machine,expected", [
        ('Linux', 'x86_64', 'https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip'),
        ('Windows', 'AMD64', 'https://releases.stackql.io/stackql/latest/stackql_windows_amd64.zip'),
        ('Darwin', 'arm64', 'https://releases.stackql.io/stackql/latest/stackql_darwin_multiarch.pkg'),
    ])
    def test_all_platforms_route_via_proxy(self, system, machine, expected):
        """Every supported platform must download from releases.stackql.io."""
        with patch('platform.system', return_value=system), \
             patch('platform.machine', return_value=machine):
            url = download.get_download_url()
        assert url == expected
        assert url.startswith('https://releases.stackql.io/'), \
            f"{system} download must route through the proxy, got {url}"

    def test_unsupported_platform_raises(self):
        """An unsupported OS should raise rather than return a URL."""
        with patch('platform.system', return_value='Plan9'), \
             patch('platform.machine', return_value='mips'):
            with pytest.raises(Exception):
                download.get_download_url()


class TestUserAgent:
    """Tests for the pystackql User-Agent."""

    def test_user_agent_format(self):
        """User-Agent must be the versioned pystackql identifier."""
        with patch('pystackql.utils.download.get_package_version', return_value='9.9.9'):
            assert download.get_user_agent() == 'pystackql/9.9.9'

    def test_user_agent_falls_back_when_version_missing(self):
        """A missing package version must not produce an empty identifier."""
        with patch('pystackql.utils.download.get_package_version', return_value=None):
            assert download.get_user_agent() == 'pystackql/unknown'

    def test_download_file_sends_user_agent(self, tmp_path):
        """download_file must send the pystackql User-Agent header."""
        fake_response = MagicMock()
        fake_response.headers = {'content-length': '4'}
        fake_response.iter_content.return_value = [b'data']
        fake_response.raise_for_status.return_value = None

        dest = os.path.join(str(tmp_path), 'out.bin')
        with patch('pystackql.utils.download.requests.get', return_value=fake_response) as mock_get:
            download.download_file('https://releases.stackql.io/stackql/latest/x.zip',
                                   dest, showprogress=False)

        assert mock_get.called
        headers = mock_get.call_args.kwargs.get('headers', {})
        assert headers.get('User-Agent', '').startswith('pystackql/')
