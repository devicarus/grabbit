from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader import Downloader
from grabbit.typing_custom import PostType


class SelfpostDownloader(Downloader):
    """ Downloader for gallery posts. """

    @staticmethod
    def supports(submission: Submission) -> bool:
        return submission.is_self

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        if submission.selftext == "" or submission.selftext is None:
            return None, []
        target = target.with_suffix(".md")
        with open(target, "w", encoding="utf-8") as f:
            f.write(submission.selftext)
        return PostType.SELFPOST, [target]
