from pathlib import Path
from typing import Optional

from grabbit.downloader.generic import download
from grabbit.downloader.sources import MediaSource
from grabbit.typing_custom import MediaType


class RedditCom(MediaSource):
    """ Downloader for i.redd.it media. """

    domain = "reddit.com"

    @staticmethod
    def download(url: str, target: Path) -> (Optional[MediaType], Optional[Path]):
        """ Returns the media URL for the given submission. """
        return MediaType.IMAGE, download(url, target, MediaType.IMAGE)
