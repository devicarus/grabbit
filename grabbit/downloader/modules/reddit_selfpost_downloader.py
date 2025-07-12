from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader import Downloader
from grabbit.typing_custom import PostType


class RedditSelfpostDownloader(Downloader):
    """ Downloader for gallery posts. """

    @staticmethod
    def supports(submission: Submission) -> bool:
        return submission.is_self

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        """ Dummy method, as selfpost bodies are always saved in metadata. """
        return PostType.SELFPOST, []
