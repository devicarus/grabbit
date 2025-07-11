""" This module contains a wrapper around the "requests" library. """

from urllib.parse import urlparse
from random import uniform
import time

import requests
from requests import RequestException
from requests.models import Response

from grabbit.logger import logger

def exponential_backoff(retry_count: int, base_delay: float = 2, jitter: bool = False) -> float:
    """ Sleeps for an exponentially increasing amount of time. """
    backoff_time = base_delay * (2 ** retry_count - 1)
    if jitter:
        backoff_time += uniform(0, 1)
    return backoff_time

class RequestFailedException(Exception):
    """ Raised when a request fails. """

class RequestRetryLimitExceededException(RequestFailedException):
    """ Raised when a request fails due to exceeding the retry limit. """

class RequestFatalException(RequestFailedException):
    """ Raised when a request fails due to a fatal error. """

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0"}

class HTTPClient:
    """ A wrapper around the requests library that handles retries and backoff. """
    _base_delay: float = 2

    def __init__(self, headers: dict | None = None):
        self._headers = headers if headers is not None else DEFAULT_HEADERS.copy()

    def request(self, method: str, url: str, max_tries: int = 3, timeout: int = 30, **kwargs) -> Response:
        """ Sends a request to the specified URL. """
        retry_count = 0
        while retry_count < max_tries:
            try:
                response = requests.request(method, url, headers=self._headers, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                retry_count += 1

                logger.debug("Request failed, retrying (%d/%d)...", retry_count, max_tries)

                if urlparse(url).hostname == "web.archive.org":
                    logger.debug("Wayback Machine has overheated, cooling off for a minute...")
                    time.sleep(61)

                time.sleep(exponential_backoff(retry_count, self._base_delay, jitter=True))

            except RequestException as e:
                logger.debug("Request failed", exc_info=e)
                raise RequestFatalException from e

        raise RequestRetryLimitExceededException(f"Failed to fetch data from {url} after {max_tries} retries")

    def get(self, url: str, params: dict | None = None, **kwargs) -> Response:
        """ Sends a GET request to the specified URL. """
        return self.request("GET", url, params=params, **kwargs)

    def head(self, url: str, params: dict | None = None, **kwargs) -> Response:
        """ Sends a HEAD request to the specified URL. """
        return self.request("HEAD", url, params=params, **kwargs)

http_client = HTTPClient()
