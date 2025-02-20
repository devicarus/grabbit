import re
from typing import Optional

from requests.models import Response

from app.utils import guess_media_type
from app.typing_custom import MediaType
from app.httpclient import HTTPClient

class WaybackList:
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
        else:
            raise StopIteration
            
    def __len__(self) -> int:
        return len(self._urls)
        
    def _has_more_urls(self) -> bool:
        return self._current + 1 <= len(self._urls)
    
    def _get_next_url(self) -> str:
        current = self._current
        self._current += 1
        
        response = self._http_client.get(self._urls[current])
        
        if guess_media_type(response) != MediaType.UNKNOWN:
            return self._urls[current]
        
        media = self._get_media_url(response) # TODO: If this is used, push the original URL as next
        return media if media else self._urls[current]
        
    def _get_media_url(self, response: Response) -> Optional[str]:
        match = re.findall(r'(?<=source src=")[^"]+(?=")', response.text)
        if not match: return
        
        if len(match) > 1:
            raise Exception("More than one source found")
        if not match[0].startswith("//"):
            raise Exception("Source URL does not start with //")
            
        return "https:" + match[0]
        
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
    _http_client: HTTPClient
    
    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client
        
    def get(self, url: str) -> WaybackList:
        return WaybackList(self._http_client, url)