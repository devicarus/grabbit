from pathlib import Path
from typing import Optional

from grabbit.downloader.generic import download
from grabbit.downloader.sources import MediaSource
from grabbit.typing_custom import MediaType


class YoutuBe(MediaSource):
    """ Downloader for i.redd.it media. """

    domain = "youtu.be"

    @staticmethod
    def download(url: str, target: Path) -> (Optional[MediaType], Optional[Path]):
        """ Returns the media URL for the given submission. """
        return MediaType.VIDEO, download(url, target, MediaType.VIDEO)
