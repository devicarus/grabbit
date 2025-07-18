import json
from pathlib import Path
from typing import Optional

from praw.models import Submission
from prawcore.exceptions import NotFound

from grabbit.typing_custom import PostType
from grabbit.utils import safe


class Downloader:
    """ Downloader interface for grabbit. """

    @staticmethod
    def supports(submission: Submission) -> bool:
        """ Returns True, if capable of downloading provided Submission, otherwise returns False. """
        raise NotImplementedError("Downloader must implement the supports method.")

    @classmethod
    def download(cls, submission: Submission, target: Path) -> bool:
        post_type, files = cls.download_media(submission, target)
        if post_type is None:
            return False
        cls.download_metadata(submission, target, post_type, files)
        return True

    @staticmethod
    def download_media(submission: Submission, target: Path) -> (Optional[PostType], list[Path]):
        """ Attempts to download the media from the submission. """
        raise NotImplementedError("Downloader must implement the download_media method.")

    @staticmethod
    def download_metadata(submission: Submission, target: Path, post_type: PostType, files: list[Path]):
        with open(target.with_suffix(".json"), "w", encoding="utf-8") as file:
            json.dump({
                "id": submission.id,
                "title": submission.title,
                "subreddit": {
                    "id": submission.subreddit.id,
                    "name": submission.subreddit.display_name,
                },
                "author": safe(
                    lambda :{
                        "id": submission.author.id,
                        "name": submission.author.name,
                    },
                    default=None,
                    exceptions=(NotFound,AttributeError)
                ) if submission.author else None,
                "date": submission.created_utc,
                "type": post_type,
                "body": submission.selftext if submission.selftext else None,
                "files": [str(file.relative_to(target.parent)) for file in files],
            }, file, indent=4)
