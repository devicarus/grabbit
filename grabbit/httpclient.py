""" This module contains a wrapper around the "requests" library. """

from time import sleep
from urllib.parse import urlparse
from logging import Logger

import requests
from requests.models import Response

from grabbit.utils import NullLogger

class RetryLimitExceededException(Exception):
    """ Raised when the maximum number of retries is exceeded. """

class HTTPClient:
    """ A wrapper around the requests library that handles retries and backoff. """
    _headers: dict[str, str]
    _logger: Logger
    _backoff_factor: float = 0.5

    def __init__(self, headers: dict | None = None, logger: Logger | None = None):
        self._headers = headers if headers is not None else {}
        self._logger = logger if logger is not None else NullLogger()

    def request(self, method: str, url: str, max_retries: int = 5, timeout: int = 30, **kwargs) -> Response:
        """ Sends a request to the specified URL. """
        retry_count = 0
        while retry_count < max_retries:
            try:
                return requests.request(method, url, headers=self._headers, timeout=timeout, **kwargs)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                if urlparse(url).hostname == "web.archive.org" and 'Errno 61' in str(e):
                    self._logger.debug("Wayback Machine has overheated, cooling off for a minute...")
                    sleep(61)

            retry_count += 1
            sleep(self._backoff_factor * (2 ** retry_count))
        raise RetryLimitExceededException(f"Failed to fetch data from {url} after {max_retries} retries")

    def get(self, url: str, params: dict | None = None, **kwargs) -> Response:
        """ Sends a GET request to the specified URL. """
        return self.request("GET", url, params=params if params is not None else {}, **kwargs)

    def head(self, url: str, params: dict | None = None, **kwargs) -> Response:
        """ Sends a HEAD request to the specified URL. """
        return self.request("HEAD", url, params=params if params is not None else {}, **kwargs)
