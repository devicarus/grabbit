from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

PostId = str

@dataclass
class Post:
    id: PostId
    sub: str
    title: str
    author: str
    date: int
    url: Optional[str] = None
    url_preview: Optional[str] = None
    source: Optional[str] = None
    data: list[str] = field(default_factory=list)

    def good(self):
        return (self.url is not None
                or self.url_preview is not None
                or (self.data != ['[removed]'] and self.data != ['[ Removed by Reddit in response to a copyright notice. ]'] and len(self.data) != 0))
    
class MediaType(Enum):
    IMAGE = 1
    GALLERY = 2
    VIDEO = 3
    TEXT = 4
    UNKNOWN = 5