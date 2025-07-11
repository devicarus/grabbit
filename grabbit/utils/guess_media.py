""" This file contains helper functions for the grabbit package. """

from mimetypes import guess_extension
from typing import Optional

from requests.models import Response

from grabbit.typing_custom import MediaType


def guess_media_type(response: Response) -> Optional[MediaType]:
    """ Tries to guess the media type of the response """
    media_type = response.headers["content-type"]
    if "image" in media_type.lower():
        return MediaType.IMAGE
    if "video" in media_type.lower():
        return MediaType.VIDEO
    return None


def guess_media_extension(response: Response) -> Optional[str]:
    """ Tries to guess the media extension of the response """
    return guess_extension(response.headers["content-type"].split(";")[0].strip(), strict=False)
