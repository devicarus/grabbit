""" This module contains custom types used in the Grabbit package. """

from dataclasses import dataclass
from enum import Enum


class PostType(str, Enum):
    """ Represents a media type """
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    IMAGE_GALLERY = "IMAGE_GALLERY"
    SELFPOST = "SELFPOST"


class MediaType(Enum):
    """ Represents a media type """
    IMAGE = 1
    VIDEO = 2


@dataclass
class RedditAccount:
    """ Represents a Reddit user """
    username: str
    password: str
    client_id: str
    client_secret: str


class PostStatus(str, Enum):
    """ Represents the status of a post """
    DOWNLOADED = "downloaded"
    SKIPPED = "skipped"
    FAILED = "failed"

@dataclass
class DownloadOptions:
    """ Represents the options for downloading """
    skip_failed: bool
    save_every: int
