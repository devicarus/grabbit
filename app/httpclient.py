import requests
from requests.models import Response
from requests.exceptions import RequestException
from time import sleep
from urllib.parse import urlparse
from logging import Logger

from app.utils import NullLogger

class HTTPClient:
    _headers: dict[str, str]
    _logger: Logger
    _backoff_factor: float = 0.3
    
    def __init__(self, headers: dict | None = None, logger: Logger | None = None):
        self._headers = headers if headers is not None else {}
        self._logger = logger if logger is not None else NullLogger()

    def request(self, method: str, url: str, params: dict | None = None, max_retries: int = 3, **kwargs) -> Response:
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.request(method, url, headers=self._headers, params=params if params is not None else {}, timeout=30, **kwargs)
                return response
            except RequestException as e:
                if isinstance(e, requests.exceptions.ConnectionError):
                    if e.request and urlparse(e.request.url).hostname == "web.archive.org" and 'Errno 61' in str(e):
                        self._logger.debug("Wayback Machine has overheated, cooling off for a minute...")
                        retry_count += 1
                        sleep(61)
                        continue
                if isinstance(e, requests.exceptions.ReadTimeout):
                    self._logger.debug(f"Request timed out, retrying in {self._backoff_factor * (2 ** retry_count)} seconds")
                    retry_count += 1
                    sleep(self._backoff_factor * (2 ** retry_count))
                    continue
                raise
                
        raise Exception(f"Failed to fetch data from {url} after {max_retries} retries")
        
    def get(self, url: str, params: dict | None = None, **kwargs) -> Response:
        return self.request("GET", url, params if params is not None else {}, **kwargs)
        
    def head(self, url: str, params: dict | None = None, **kwargs) -> Response:
        return self.request("HEAD", url, params if params is not None else {}, **kwargs)