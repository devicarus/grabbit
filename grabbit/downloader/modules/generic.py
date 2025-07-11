from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader.generic.image import download_image
from grabbit.downloader.generic.video import download_video
from grabbit.logger import logger
from grabbit.downloader import Downloader
from grabbit.utils.httpclient import http_client
from grabbit.typing_custom import MediaType, PostType
from grabbit.utils import guess_media_type


class GenericDownloader(Downloader):
    """ Downloader for generic media. """

    @staticmethod
    def supports(_: Submission) -> bool:
        """ Dummy method. """
        return True

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        response = http_client.head(submission.url, allow_redirects=True)
        guess = guess_media_type(response)
        if guess is None:
            logger.debug("Failed to guess post format")
        else:
            logger.debug("Guessed format as %s", guess.name.lower())

        if guess is MediaType.IMAGE:
            return PostType.IMAGE, [download_image(submission.url, target)]
        if guess is MediaType.VIDEO:
            return PostType.VIDEO, [download_video(submission.url, target)]

        image_file = download_image(submission.url, target)
        if image_file is not None:
            return PostType.IMAGE, [image_file]
        video_file = download_video(submission.url, target)
        if video_file is not None:
            return PostType.VIDEO, [video_file]

        return None, []
