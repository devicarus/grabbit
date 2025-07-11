""" Tests for the Wayback class """

import pytest
from unittest.mock import patch, Mock

from grabbit.utils import HTTPClient, Wayback, WaybackList


@pytest.fixture(name="httpclient")
def fixture_httpclient():
    """ Fixture of the HTTPClient """
    return HTTPClient()


@pytest.fixture(name="wayback")
def fixture_wayback():
    """ Fixture of the Wayback class """
    return Wayback()


def test_wayback(wayback: Wayback):
    """ Test the Wayback class """
    mock_response_stamps = ["20200101000000", "20200102000000"]
    mock_response_json = [["timestamp", "statuscode"]] + [
        [stamp, "200"] for stamp in mock_response_stamps
    ]

    mock_response = Mock()
    mock_response.json.return_value = mock_response_json

    with patch.object(HTTPClient, "get", return_value=mock_response):
        results: WaybackList = wayback.get("https://example.com")

    assert results is not None
    assert len(results) == len(mock_response_stamps)