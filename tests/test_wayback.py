""" Tests for the Wayback class """

import pytest
from flexmock import flexmock

from grabbit.httpclient import HTTPClient
from grabbit.wayback import Wayback, WaybackList

@pytest.fixture(name="httpclient")
def fixture_httpclient():
    """ Fixture of the HTTPClient """
    return HTTPClient({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0"})

@pytest.fixture(name="wayback")
def fixture_wayback(httpclient: HTTPClient):
    """ Fixture of the Wayback class """
    return Wayback(httpclient)

def test_wayback(wayback: Wayback):
    """ Test the Wayback class """
    mock_response_stamps = ["20200101000000", "20200102000000"]
    mock_response_json = [["timestamp", "statuscode"], *[[stamp, "200"] for stamp in mock_response_stamps]]

    mock_response = flexmock()
    mock_response.should_receive("json").and_return(mock_response_json)
    flexmock(HTTPClient).should_receive("get").and_return(mock_response)

    results: WaybackList = wayback.get("https://example.com")
    assert results is not None
    assert len(results) == len(mock_response_stamps)
