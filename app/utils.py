from mimetypes import guess_extension
from typing import Optional

from logging import Logger

import requests
from requests.models import Response

from app.typing_custom import MediaType

def follow_redirects(url: str) -> str:
    try:
        response = requests.head(url, allow_redirects = True, timeout = 10)
        response.raise_for_status()
        return response.url.split("?")[0] 
    except Exception:
        return url
        
def guess_media_type(response: Response) -> MediaType:
    media_type = response.headers["content-type"]
    if "image" in media_type.lower():
        return MediaType.IMAGE
    elif "video" in media_type.lower():
        return MediaType.VIDEO
    return MediaType.UNKNOWN

def guess_media_extension(response: Response) -> Optional[str]:
    return guess_extension(response.headers["content-type"].split(";")[0].strip())

class NullLogger(Logger):
    def __init__(self):
        pass

    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass
