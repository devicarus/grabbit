""" This file contains helper functions for the grabbit package. """

import csv
from mimetypes import guess_extension
from pathlib import Path
from typing import Optional
from logging import Logger

from requests.models import Response

from grabbit.typing_custom import MediaType, PostId


def guess_media_type(response: Response) -> MediaType:
    """ Tries to guess the media type of the response """
    media_type = response.headers["content-type"]
    if "image" in media_type.lower():
        return MediaType.IMAGE
    if "video" in media_type.lower():
        return MediaType.VIDEO
    return MediaType.UNKNOWN


def guess_media_extension(response: Response) -> Optional[str]:
    """ Tries to guess the media extension of the response """
    return guess_extension(response.headers["content-type"].split(";")[0].strip(), strict=False)


def load_gdpr_saved_posts_csv(path: Path) -> list[PostId]:
    """ Loads post ids from the GDPR Saved Posts CSV file """
    with open(path, encoding="utf-8") as file:
        reader = csv.reader(file)
        ids = [ensure_post_id(row[0]) for row in reader]
        del ids[0]
    return ids

def ensure_post_id(post_id_like: str) -> PostId:
    """ Makes sure the post id is prefixed with "t3_" """
    if post_id_like.startswith("t3_"):
        return post_id_like
    return f"t3_{post_id_like}"

class NullLogger(Logger):
    """ A logger that logs nothing """

    def __init__(self):
        super().__init__("NullLogger")

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
