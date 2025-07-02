""" This module contains custom types used in the Grabbit package. """

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

PostId = str
SubredditId = str
UserId = str

@dataclass
class Subreddit:
    """ Represents a subreddit """
    id: SubredditId
    name: str

@dataclass
class User:
    """ Represents a Reddit user """
    id: UserId
    name: str

# pylint: disable=too-many-instance-attributes
# This class represents a Reddit post and includes the fields required to capture relevant metadata.
# Making it a dictionary instead would hurt readability and maintainability, while also essentially removing typing.
@dataclass
class Post:
    """ Represents a post on Reddit """
    id: PostId
    subreddit: Subreddit
    title: str
    author: Optional[User]
    date: int
    url: Optional[str]
    url_preview: Optional[str]
    source: Optional[str]
    data: list[str] = field(default_factory=list)

    def good_data(self):
        """ Returns True if the post data is good, False otherwise."""
        return not (
            self.data == ['[removed]']
            or self.data == ['[ Removed by Reddit in response to a copyright notice. ]']
            or self.data == ['[ Removed by Reddit on account of violating the [content policy](/help/contentpolicy). ]']
            or len(self.data) == 0
        )

    def good(self):
        """ Returns True if the post is good, False otherwise. """
        return self.url is not None or self.url_preview is not None or self.good_data()


class MediaType(Enum):
    """ Represents a media type """
    IMAGE = 1
    GALLERY = 2
    VIDEO = 3
    TEXT = 4
    UNKNOWN = 5


@dataclass
class RedditUser:
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
