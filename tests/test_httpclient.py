""" Tests for the HTTPClient class """
# @generated [partially] GPT-4o: Prompt: Write pytest unit tests for the HTTPClient class. Use flexmock where appropriate.

import pytest
from flexmock import flexmock

import time
import requests
from requests.models import Response

from grabbit.httpclient import HTTPClient, RetryLimitExceededException

def test_successful_request():
    """ Tests a successful request """
    mock_response = flexmock(Response)
    flexmock(requests).should_receive('request').and_return(mock_response)

    client = HTTPClient()
    response = client.request("GET", "https://example.com")
    assert response == mock_response


def test_retry_logic():
    """ Tests the retry logic """
    mock_response = flexmock(Response)
    # faking the delay for testing
    flexmock(time).should_receive('sleep').and_return(None)
    # 5x ordered() because: https://github.com/flexmock/flexmock/issues/8
    flexmock(requests).should_receive('request').and_raise(requests.exceptions.ConnectionError).times(5).ordered().ordered().ordered().ordered().ordered()
    flexmock(requests).should_receive('request').and_return(mock_response).ordered()

    client = HTTPClient()
    response = client.request("GET", "https://example.com", max_tries=6)
    assert response == mock_response


def test_retry_limit_exceeded():
    """ Tests the retry limit mechanism """
    # faking the delay for testing
    flexmock(time).should_receive('sleep').and_return(None)
    flexmock(requests).should_receive('request').and_raise(requests.exceptions.ConnectionError).times(2)

    client = HTTPClient()
    with pytest.raises(RetryLimitExceededException):
        client.request("GET", "https://example.com", max_tries=2)


def test_get_method():
    """ Tests the GET method"""
    mock_response = flexmock(Response)
    flexmock(requests).should_receive('request').with_args("GET", "https://example.com", params={}, headers={}, timeout=30).and_return(mock_response)

    client = HTTPClient()
    response = client.get("https://example.com")
    assert response == mock_response


def test_head_method():
    """ Tests the HEAD method"""
    mock_response = flexmock(Response)
    flexmock(requests).should_receive('request').with_args("HEAD", "https://example.com", params={}, headers={}, timeout=30).and_return(mock_response)

    client = HTTPClient()
    response = client.head("https://example.com")
    assert response == mock_response
