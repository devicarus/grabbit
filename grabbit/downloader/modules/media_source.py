from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader import Downloader
from grabbit.downloader.sources import MediaSource
from grabbit.logger import logger
from grabbit.typing_custom import PostType, MediaType
from grabbit.utils import branch_counter


class MediaSourceDownloader(Downloader):
    """ Downloader for media from known sources. """

    @staticmethod
    def supports(submission: Submission) -> bool:
        domain = getattr(submission, 'domain', None)
        if domain is None:
            return False

        if MediaSource.get(domain) is not None:
            branch_counter.increment("source", "hit", domain)
            logger.debug("MediaSource found for %s", domain)
            return True

        branch_counter.increment("source", "miss", domain)
        logger.debug("No MediaSource found for %s", domain)
        return False

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        media_type, file = MediaSource.get(getattr(submission, 'domain', None)).download(submission.url, target)
        if file is None:
            return None, []
        return PostType.IMAGE if media_type == MediaType.IMAGE else PostType.VIDEO, [file]
