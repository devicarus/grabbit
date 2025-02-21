from mimetypes import guess_extension
from typing import Optional

from logging import Logger

from requests.models import Response

from app.typing_custom import MediaType, PostId
        
def guess_media_type(response: Response) -> MediaType:
    media_type = response.headers["content-type"]
    if "image" in media_type.lower():
        return MediaType.IMAGE
    elif "video" in media_type.lower():
        return MediaType.VIDEO
    return MediaType.UNKNOWN

def guess_media_extension(response: Response) -> Optional[str]:
    return guess_extension(response.headers["content-type"].split(";")[0].strip(), strict=False)

class NullLogger(Logger):
    def __init__(self):
        super().__init__("NullLogger")
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
