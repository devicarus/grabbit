from time import sleep
from urllib.parse import urlparse
from logging import Logger

import requests
from requests.models import Request, Response
from requests.exceptions import ConnectionError, ReadTimeout

from grabbit.utils import NullLogger

class RetryLimitExceededException(Exception):
    pass

class HTTPClient:
    _headers: dict[str, str]
    _logger: Logger
    _backoff_factor: float = 0.3
    
    def __init__(self, headers: dict | None = None, logger: Logger | None = None):
        self._headers = headers if headers is not None else {}
        self._logger = logger if logger is not None else NullLogger()

    def request(self, method: str, url: str, params: dict | None = None, max_retries: int = 3, timeout: int = 30, **kwargs) -> Response:
        retry_count = 0
        while retry_count < max_retries:
            try:
                return requests.request(method, url, headers=self._headers, params=params if params is not None else {}, timeout=timeout, **kwargs)
            except ConnectionError as e:
                if isinstance(e.request, Request) and urlparse(e.request.url).hostname == "web.archive.org" and 'Errno 61' in str(e):
                    self._logger.debug("Wayback Machine has overheated, cooling off for a minute...")
                    retry_count += 1
                    sleep(61)
                    continue
                raise
            except ReadTimeout:
                self._logger.debug(f"Request timed out, retrying in {self._backoff_factor * (2 ** retry_count)} seconds")
                retry_count += 1
                sleep(self._backoff_factor * (2 ** retry_count))
                continue
                
        raise RetryLimitExceededException(f"Failed to fetch data from {url} after {max_retries} retries")
        
    def get(self, url: str, params: dict | None = None, **kwargs) -> Response:
        return self.request("GET", url, params if params is not None else {}, **kwargs)
        
    def head(self, url: str, params: dict | None = None, **kwargs) -> Response:
        return self.request("HEAD", url, params if params is not None else {}, **kwargs)