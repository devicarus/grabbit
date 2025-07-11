""" Tests for the HTTPClient class """

import requests
from requests.models import Response

import pytest
from unittest.mock import patch, Mock

from grabbit.utils import HTTPClient, RequestRetryLimitExceededException


def test_successful_request():
    """ Tests a successful request """
    mock_response = Mock(spec=Response)

    with patch("requests.request", return_value=mock_response):
        client = HTTPClient()
        response = client.request("GET", "https://example.com")
        assert response == mock_response


def test_retry_logic():
    """ Tests the retry logic """
    mock_response = Mock(spec=Response)

    with patch("requests.request") as mock_request, patch("time.sleep") as mock_sleep:
        # First 5 calls raise ConnectionError
        mock_request.side_effect = [requests.exceptions.ConnectionError] * 5 + [mock_response]

        client = HTTPClient()
        response = client.request("GET", "https://example.com", max_tries=6)

        assert response == mock_response
        assert mock_request.call_count == 6
        assert mock_sleep.called


def test_retry_limit_exceeded():
    """ Tests the retry limit mechanism """
    with patch("requests.request", side_effect=requests.exceptions.ConnectionError), \
         patch("time.sleep"):
        client = HTTPClient()
        with pytest.raises(RequestRetryLimitExceededException):
            client.request("GET", "https://example.com", max_tries=2)


def test_get_method():
    """ Tests the GET method """
    mock_response = Mock(spec=Response)

    with patch("requests.request", return_value=mock_response):
        client = HTTPClient()
        response = client.get("https://example.com")
        assert response == mock_response


def test_head_method():
    """ Tests the HEAD method """
    mock_response = Mock(spec=Response)

    with patch("requests.request", return_value=mock_response):
        client = HTTPClient()
        response = client.head("https://example.com")
        assert response == mock_response
