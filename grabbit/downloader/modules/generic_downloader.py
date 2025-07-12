from pathlib import Path
from typing import Optional

from praw.models import Submission

from grabbit.downloader.generic import download
from grabbit.logger import logger
from grabbit.downloader import Downloader
from grabbit.utils.httpclient import http_client
from grabbit.typing_custom import PostType, post_type_from_media_type, MediaType
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

        if guess is not None:
            logger.debug("Guessed media type as %s", guess.name.lower())
            file = download(submission.url, target, guess)
            if file is not None:
                return post_type_from_media_type(guess), [file]
            return None, []

        logger.debug("Failed to guess media type")
        for media_type in MediaType:
            logger.debug("Trying to download as %s", media_type.name.lower())
            file = download(submission.url, target, media_type)
            if file is not None:
                return post_type_from_media_type(media_type), [file]

        return None, []
