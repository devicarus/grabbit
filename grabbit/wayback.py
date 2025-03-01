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

    def __init__(self, http_client: HTTPClient, urls: list[str]):
        self._http_client = http_client
        self._urls = urls

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


class Wayback:
    """ A class for interacting with the Wayback Machine. """
    _api_url: str = "https://web.archive.org/cdx/search/cdx"
    _src_url: str = "https://web.archive.org/web"

    _http_client: HTTPClient

    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client

    def get(self, url: str) -> WaybackList:
        """ Returns a list of Wayback URLs for the specified URL. """
        return WaybackList(self._http_client, self._get_urls(url))

    def _get_urls(self, url: str) -> list[str]:
        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,statuscode"
        }
        captures = self._http_client.get(self._api_url, params).json()

        if len(captures) == 0:
            return []
        del captures[0] # Remove the header

        stamps: list[str] = [capture[0] for capture in captures if capture[1].isdigit()]
        return [f"{self._src_url}/{stamp}/{url}" for stamp in sorted(stamps)]
