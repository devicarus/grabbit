""" This module contains the Wayback and WaybackList classes."""

import re

from requests.models import Response

from grabbit.utils import guess_media_type
from grabbit.typing_custom import MediaType
from grabbit.httpclient import HTTPClient

class WaybackList:
    """ A class that represents a list of URLs from the Wayback Machine. """
    _current: int = 0
    _urls: list[str] = []

    _http_client: HTTPClient

    def __init__(self, http_client: HTTPClient, url: str):
        self._http_client = http_client
        self._urls = self._get_urls(url)

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self._has_more_urls():
            return self._get_next_url()
        raise StopIteration

    def __len__(self) -> int:
        return len(self._urls)

    def _has_more_urls(self) -> bool:
        return self._current + 1 <= len(self._urls)

    def _get_next_url(self) -> str:
        current = self._current
        self._current += 1

        # If the url is not a raw media link, check if it has a media source and add it to the list
        response = self._http_client.get(self._urls[current])
        if guess_media_type(response) == MediaType.UNKNOWN:
            media_sources = self._get_media_sources(response)
            if len(media_sources) > 0:
                self._urls = self._urls[:current+1] + media_sources + self._urls[current+1:]

        return self._urls[current]

    @staticmethod
    def _get_media_sources(response: Response) -> list[str]:
        matches = re.findall(r'(?<=source src=")[^"]+(?=")', response.text)
        return ["https:" + url if url.startswith("//") else url for url in matches]

    # TODO: Refactor this method
    def _get_urls(self, url: str) -> list[str]:
        wb_api = "https://web.archive.org/cdx/search/cdx"
        wb_src = "https://web.archive.org/web"

        params = {
            "url": url,
            "output": "json",
            "gzip": False,
            "fl": "timestamp,statuscode",
            "collapse": "digest",
        }
        response = self._http_client.get(wb_api, params)

        captures = response.json()
        urls = []
        if len(captures) != 0:
            stamps = captures[1:]
            stamps = [stamp for stamp in stamps if stamp[1].isdigit()]
            stamps = sorted(stamps, key = lambda x: int(x[1]))
            urls = [f"{wb_src}/{stamp[0]}/{url}" for stamp in stamps][:3]

        return urls

class Wayback:
    """ A class for interacting with the Wayback Machine. """
    _http_client: HTTPClient

    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client

    def get(self, url: str) -> WaybackList:
        """ Returns a list of Wayback URLs for the specified URL. """
        return WaybackList(self._http_client, url)
